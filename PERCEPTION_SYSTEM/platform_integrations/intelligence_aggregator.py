# -*- coding: utf-8 -*-
# ==============================================================================
# == INTELLIGENCE AGGREGATOR v4 - PROJECT CHIMERA ==
# ==============================================================================
#
# Lokasi: PERCEPTION_SYSTEM/platform_integrations/intelligence_aggregator.py
# Deskripsi: Modul ini bertindak sebagai pusat kendali untuk semua koneksi API
#            eksternal. Ia mengelola kunci API, menangani permintaan, dan yang
#            paling penting, mengimplementasikan logika fallback & rotasi kunci
#            serta penanganan error yang sangat tangguh.
#            Versi ini merupakan hasil evolusi dari semua diskusi.
#
# ==============================================================================

import logging
import sys
import os
import time
import random
import requests
import ccxt
from collections import defaultdict

# --- PENYESUAIAN PATH DINAMIS UNTUK MENGATASI MASALAH IMPOR ---
# Mendapatkan path absolut dari direktori script ini
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Naik tiga level untuk mendapatkan direktori root proyek (PROJECTCHIMERA)
# PERCEPTION_SYSTEM/platform_integrations/ -> PROJECTCHIMERA/
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_script_dir)))
# Menambahkan direktori root ke sys.path agar modul-modul bisa diimpor
sys.path.insert(0, str(project_root))
# --- AKHIR PENYESUAIAN PATH ---

class IntelligenceAggregator:
    """
    Mengelola semua koneksi API, menyediakan data dengan mekanisme fallback
    dan rotasi kunci untuk ketahanan maksimal.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi Intelligence Aggregator v4.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator untuk akses ke secrets/config.
        """
        logging.info("Inisialisasi Intelligence Aggregator v4...")
        self.orchestrator = orchestrator
        self.secrets = self.orchestrator.secrets
        
        # Untuk melacak indeks kunci terakhir yang digunakan untuk setiap layanan multi-kunci
        self.key_indices = defaultdict(int)
        
        # Muat semua kunci API yang tersedia
        self._load_api_keys()
        
        logging.info("Intelligence Aggregator v4 berhasil diinisialisasi.")

    def _load_api_keys(self):
        """
        Memuat semua kunci API dari secrets.vault.
        """
        try:
            # --- 1. BURSA (Menggunakan CCXT) ---
            exchange_secrets = self.secrets.get('exchange_apis', {})
            binance_api_key = exchange_secrets.get('binance_api_key')
            binance_secret_key = exchange_secrets.get('binance_secret_key')

            if binance_api_key and binance_secret_key:
                self.clients = {}
                self.clients['binance'] = ccxt.binance({
                    'apiKey': binance_api_key,
                    'secret': binance_secret_key,
                    'options': {'defaultType': 'spot'}, # Atau 'future'
                    'enableRateLimit': True, # CCXT akan menangani rate limit dasar
                    'timeout': 10000, # 10 detik timeout
                })
                # Tes koneksi dasar
                self.clients['binance'].load_markets()
                logging.info("Klien CCXT untuk Binance berhasil dibuat dan diverifikasi.")
            else:
                logging.warning("Kunci API Binance tidak lengkap. Fungsi trading pasar akan dinonaktifkan.")
                self.clients['binance'] = None

            # --- 2. DATA PASAR ---
            market_secrets = self.secrets.get('market_data_apis', {})
            # Simpan kunci untuk penggunaan langsung dalam metode pengambilan data
            self.clients['coingecko_key'] = market_secrets.get('coingecko_api_key')
            self.clients['coincap_key'] = market_secrets.get('coincap_api_key')
            self.clients['alpha_vantage_key'] = market_secrets.get('alpha_vantage_api_key')
            # Kunci untuk layanan multi-akun
            self.clients['coinstats_keys'] = market_secrets.get('coinstats_keys', [])
            self.key_indices['coinstats'] = 0 # Inisialisasi indeks rotasi
            logging.info("Kunci API untuk data pasar (fallback) berhasil dimuat.")

            # --- 3. INTELIJEN & BERITA ---
            intelligence_secrets = self.secrets.get('intelligence_apis', {})
            # Kunci untuk layanan multi-akun
            self.clients['messari_keys'] = intelligence_secrets.get('messari_keys', [])
            self.clients['coindesk_keys'] = intelligence_secrets.get('coindesk_keys', [])
            self.key_indices['messari'] = 0 # Inisialisasi indeks rotasi
            self.key_indices['coindesk'] = 0 # Inisialisasi indeks rotasi

            self.clients['newsapi_key'] = intelligence_secrets.get('newsapi_key')
            self.clients['thenewsapi_key'] = intelligence_secrets.get('thenewsapi_key')
            logging.info("Kunci API untuk intelijen & berita (fallback) berhasil dimuat.")

            # --- 4. ON-CHAIN ---
            onchain_secrets = self.secrets.get('onchain_apis', {})
            # Kunci untuk layanan multi-akun
            self.clients['etherscan_keys'] = onchain_secrets.get('etherscan_keys', [])
            self.key_indices['etherscan'] = 0 # Inisialisasi indeks rotasi
            logging.info("Kunci API untuk data on-chain spesifik berhasil dimuat.")

            # --- 5. AI APIs ---
            # Kunci untuk AI biasanya digunakan langsung saat memanggil API oleh LLMRouter.
            # Tidak perlu diinisialisasi sebagai klien di sini.

            # --- 6. TOOLS ---
            tool_secrets = self.secrets.get('tool_apis', {})
            self.clients['scrapeops_key'] = tool_secrets.get('scrapeops_api_key')
            # self.clients['opensea_key'] = tool_secrets.get('opensea_api_key')
            logging.info("Kunci API untuk tools berhasil dimuat.")


        except Exception as e:
            logging.critical(f"Gagal memuat kunci API: {e}", exc_info=True)
            raise # Hentikan inisialisasi jika kunci kritis gagal dimuat

    def _rotate_key(self, service_name):
        """
        Mendapatkan kunci API berikutnya dengan rotasi round-robin.
        Args:
            service_name (str): Nama layanan (e.g., 'coinstats', 'messari', 'coindesk', 'etherscan').
        Returns:
            str: Kunci API yang diputar, atau None jika tidak ditemukan.
        """
        # Asumsi: kunci-kunci untuk layanan multi-akun disimpan dalam list di self.clients
        # Misalnya, self.clients['coindesk_keys'] = [key1, key2, key3]
        keys = self.clients.get(f"{service_name}_keys", [])
        if not keys:
            # logging.debug(f"Tidak ada kunci yang ditemukan untuk rotasi {service_name}.")
            return None

        index = self.key_indices[service_name]
        key = keys[index]
        # Update index untuk rotasi berikutnya
        self.key_indices[service_name] = (index + 1) % len(keys)
        # logging.debug(f"Kunci {service_name} diputar ke index {index}.")
        return key

    def get_client(self, client_name):
        """
        Mendapatkan klien API yang telah diinisialisasi (terutama untuk CCXT).
        Args:
            client_name (str): Nama klien (e.g., 'binance').
        Returns:
            Objek klien atau None.
        """
        return self.clients.get(client_name)

    # --- FUNGSI PENGUMPULAN DATA PASAR (FALLBACK) ---
    def get_market_price(self, symbol: str = 'BTC/USDT'):
        """
        Mendapatkan harga pasar saat ini dengan mekanisme fallback yang tangguh.
        Prioritas: Binance -> CoinGecko -> CoinCap -> CoinStats (rotasi).
        Args:
            symbol (str): Simbol pasangan trading (format CCXT).
        Returns:
            float: Harga terakhir, atau None jika semua sumber gagal.
        """
        logging.info(f"Mengambil harga pasar untuk {symbol} (fallback on-chain)...")
        
        # --- Prioritas 1: Binance (sumber paling real-time) ---
        try:
            if self.clients.get('binance'):
                # Tambahkan jitter kecil untuk menghindari rate limit
                time.sleep(random.uniform(0.1, 0.3))
                ticker = self.clients['binance'].fetch_ticker(symbol)
                price = float(ticker['last'])
                logging.info(f"Harga dari Binance: {price}")
                return price
            else:
                logging.warning("Klien Binance tidak tersedia untuk fallback harga.")
        except ccxt.NetworkError as e:
            logging.warning(f"Binance (jaringan) gagal: {e}. Fallback ke CoinGecko.")
        except ccxt.ExchangeError as e:
             logging.warning(f"Binance (bursa) gagal: {e}. Fallback ke CoinGecko.")
        except Exception as e:
            logging.warning(f"Binance gagal (error lain): {e}. Fallback ke CoinGecko.")

        # --- Prioritas 2: CoinGecko ---
        try:
            # CoinGecko menggunakan ID aset, bukan simbol pair
            asset_id_map = {'BTC/USDT': 'bitcoin', 'ETH/USDT': 'ethereum'} # Tambahkan mapping sesuai kebutuhan
            asset_id = asset_id_map.get(symbol)
            if not asset_id:
                 # Fallback sederhana untuk ekstraksi ID
                 asset_id = symbol.split('/')[0].lower()
            
            if self.clients.get('coingecko_key'):
                 headers = {"Authorization": f"Bearer {self.clients['coingecko_key']}"}
            else:
                 headers = {} # CoinGecko API publik

            url = f"https://api.coingecko.com/api/v3/simple/price?ids={asset_id}&vs_currencies=usd"
            # Tambahkan jitter kecil untuk menghindari rate limit
            time.sleep(random.uniform(0.1, 0.3))
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            price = data.get(asset_id, {}).get('usd')
            if price:
                logging.info(f"Harga dari CoinGecko: {price}")
                return float(price)
        except requests.exceptions.RequestException as e:
            logging.warning(f"CoinGecko (jaringan) gagal: {e}. Fallback ke CoinCap.")
        except Exception as e:
            logging.warning(f"CoinGecko gagal (error lain): {e}. Fallback ke CoinCap.")

        # --- Prioritas 3: CoinCap ---
        try:
            # CoinCap menggunakan slug yang konsisten dengan id
            asset_slug_map = {'BTC/USDT': 'bitcoin', 'ETH/USDT': 'ethereum'}
            asset_slug = asset_slug_map.get(symbol, symbol.split('/')[0].lower())
            
            headers = {"Authorization": f"Bearer {self.clients['coincap_key']}"} if self.clients.get('coincap_key') else {}
            url = f"https://api.coincap.io/v2/assets/{asset_slug}" # Perbaikan: Gunakan slug
            # Tambahkan jitter kecil untuk menghindari rate limit
            time.sleep(random.uniform(0.1, 0.3))
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            price = data.get('data', {}).get('priceUsd')
            if price:
                logging.info(f"Harga dari CoinCap: {price}")
                return float(price)
        except requests.exceptions.RequestException as e:
             logging.warning(f"CoinCap (jaringan) gagal: {e}. Fallback ke CoinStats.")
        except Exception as e:
             logging.warning(f"CoinCap gagal (error lain): {e}. Fallback ke CoinStats.")

        # --- Prioritas 4: CoinStats (dengan rotasi kunci) ---
        try:
            asset_symbol_simple = symbol.split('/')[0] # BTC, ETH
            api_key = self._rotate_key('coinstats')
            if not api_key:
                raise ValueError("Tidak ada kunci CoinStats yang tersedia.")

            headers = {"Authorization": f"Bearer {api_key}"}
            url = f"https://open-api.coinstats.app/api/v1/coins/{asset_symbol_simple}?currency=USD"
            # Tambahkan jitter kecil untuk menghindari rate limit
            time.sleep(random.uniform(0.1, 0.3))
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            price = data.get('coin', {}).get('price')
            if price:
                logging.info(f"Harga dari CoinStats: {price}")
                return float(price)
        except requests.exceptions.RequestException as e:
             logging.error(f"Semua sumber harga gagal. Terakhir gagal di CoinStats: {e}")
        except Exception as e:
             logging.error(f"Semua sumber harga gagal. Terakhir gagal di CoinStats: {e}")
        
        return None

    def get_detailed_market_data(self, symbol='BTC/USDT'):
        """
        Mendapatkan data pasar yang lebih detail (OHLCV, volume) dari exchange.
        Args:
            symbol (str): Simbol pasangan trading.
        Returns:
            dict: Data OHLCV dan statistik, atau None jika gagal.
        """
        try:
            if self.clients.get('binance'):
                client = self.clients['binance']
                # Tambahkan jitter kecil untuk menghindari rate limit
                time.sleep(random.uniform(0.1, 0.3))
                # Fetch ticker
                ticker = client.fetch_ticker(symbol)
                # Fetch recent OHLCV (e.g., last 2 hours of 1h candles)
                ohlcv = client.fetch_ohlcv(symbol, timeframe='1h', limit=2)
                
                data = {
                    'symbol': symbol,
                    'price': ticker.get('last'),
                    'change_24h': ticker.get('percentage'),
                    'volume_24h': ticker.get('baseVolume'),
                    'high_1h': ohlcv[-1][2] if len(ohlcv) >= 1 else None,
                    'low_1h': ohlcv[-1][3] if len(ohlcv) >= 1 else None,
                    'close_1h': ohlcv[-1][4] if len(ohlcv) >= 1 else None,
                    'volume_1h': ohlcv[-1][5] if len(ohlcv) >= 1 else None,
                }
                logging.debug(f"Data pasar detail untuk {symbol} berhasil diambil.")
                return data
            else:
                logging.warning("Klien Binance tidak tersedia untuk data pasar detail.")
        except Exception as e:
            logging.error(f"Kesalahan saat mengambil data pasar detail untuk {symbol}: {e}", exc_info=True)
        return None

    # --- FUNGSI PENGUMPULAN BERITA & INTELIJEN (FALLBACK) ---
    def get_latest_news(self, query="cryptocurrency"):
        """
        Mengambil berita terbaru dengan fallback.
        Prioritas: NewsAPI -> TheNewsAPI -> Messari.
        Args:
            query (str): Kata kunci pencarian berita.
        Returns:
            list: Daftar artikel berita.
        """
        all_articles = []

        # --- 1. NewsAPI ---
        if self.clients.get('newsapi_key'):
            try:
                api_key = self.clients['newsapi_key']
                url = f"https://newsapi.org/v2/everything"
                params = {
                    'q': query,
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'apiKey': api_key
                }
                # Tambahkan jitter kecil untuk menghindari rate limit
                time.sleep(random.uniform(0.1, 0.3))
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                articles = data.get('articles', [])
                for article in articles:
                     all_articles.append({
                         'source': 'NewsAPI',
                         'title': article.get('title'),
                         'description': article.get('description'),
                         'url': article.get('url'),
                         'published_at': article.get('publishedAt')
                     })
                logging.info(f"Berhasil mengambil {len(articles)} artikel dari NewsAPI.")
            except requests.exceptions.RequestException as e:
                logging.warning(f"NewsAPI (jaringan) gagal: {e}")
            except Exception as e:
                logging.warning(f"NewsAPI gagal (error lain): {e}")

        # --- 2. TheNewsAPI ---
        if self.clients.get('thenewsapi_key') and len(all_articles) < 10: # Ambil tambahan jika kurang
             try:
                 api_key = self.clients['thenewsapi_key']
                 url = f"https://thenewsapi.com/api/v1/news/all"
                 params = {
                     'api_token': api_key,
                     'search': query,
                     'locale': 'en-US',
                     'sort': 'published_at',
                     'limit': 10 # Batasi jumlah
                 }
                 # Tambahkan jitter kecil untuk menghindari rate limit
                 time.sleep(random.uniform(0.1, 0.3))
                 response = requests.get(url, params=params)
                 response.raise_for_status()
                 data = response.json()
                 articles = data.get('data', [])
                 for article in articles:
                     all_articles.append({
                         'source': 'TheNewsAPI',
                         'title': article.get('title'),
                         'description': article.get('description'),
                         'url': article.get('url'),
                         'published_at': article.get('published_at')
                     })
                 logging.info(f"Berhasil mengambil {len(articles)} artikel dari TheNewsAPI.")
             except requests.exceptions.RequestException as e:
                 logging.warning(f"TheNewsAPI (jaringan) gagal: {e}")
             except Exception as e:
                 logging.warning(f"TheNewsAPI gagal (error lain): {e}")

        # --- 3. Messari (Fallback terakhir atau tambahan) ---
        # Messari biasanya untuk riset, bukan berita umum. Bisa disesuaikan.
        # Placeholder untuk Messari jika diperlukan...

        if not all_articles:
            logging.warning("Tidak ada artikel berita yang berhasil diambil dari sumber apapun.")
            return []

        logging.info(f"Total {len(all_articles)} artikel berita (fallback) berhasil dikumpulkan.")
        return all_articles

    # --- FUNGSI PENGUMPULAN DATA ON-CHAIN (FALLBACK) ---
    def get_etherscan_data(self, module='stats', action='ethprice'):
        """
        Mendapatkan data dari Etherscan API dengan rotasi kunci.
        Args:
            module (str): Modul Etherscan.
            action (str): Aksi dalam modul.
        Returns:
            dict: Data dari Etherscan, atau None jika gagal.
        """
        try:
            etherscan_key = self._rotate_key('etherscan')
            if not etherscan_key:
                logging.warning("Tidak ada kunci Etherscan yang tersedia.")
                return None

            url = f"https://api.etherscan.io/api"
            params = {
                'module': module,
                'action': action,
                'apikey': etherscan_key
            }
            # Tambahkan jitter kecil untuk menghindari rate limit
            time.sleep(random.uniform(0.1, 0.3))
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == '1': # Sukses
                logging.debug(f"Data Etherscan ({module}.{action}) berhasil diambil.")
                return data.get('result')
            else:
                logging.warning(f"API Etherscan mengembalikan error: {data.get('message')}")
                return None
        except requests.exceptions.RequestException as e:
             logging.error(f"Kesalahan saat mengambil data Etherscan ({module}.{action}): {e}", exc_info=True)
             return None
        except Exception as e:
            logging.error(f"Kesalahan saat mengambil data Etherscan ({module}.{action}): {e}", exc_info=True)
            return None

    # --- FUNGSI AGREGASI UTAMA (INTERFACE UNTUK PERCEPTION SYSTEM) ---
    def aggregate_market_data(self, symbols=['BTC/USDT', 'ETH/USDT']):
        """
        Mengumpulkan dan menggabungkan data pasar untuk beberapa simbol.
        Args:
            symbols (list): Daftar simbol pasangan trading.
        Returns:
            dict: Data pasar yang dikumpulkan.
        """
        market_data = {}
        for symbol in symbols:
            # Prioritaskan data detail dari exchange
            detailed_data = self.get_detailed_market_data(symbol)
            if detailed_data and detailed_data.get('price') is not None:
                market_data[symbol] = detailed_data
            else:
                # Fallback ke harga saja
                price = self.get_market_price(symbol)
                market_data[symbol] = {'symbol': symbol, 'price': price}
        return market_data

    def aggregate_onchain_data(self, assets=['bitcoin', 'ethereum']):
        """
        Mengumpulkan data on-chain untuk aset tertentu.
        Args:
            assets (list): Daftar nama aset (slug).
        Returns:
            dict: Data on-chain yang dikumpulkan.
        """
        onchain_data = {}
        for asset in assets:
             data_points = {}
             if asset.lower() == 'ethereum':
                 # Contoh spesifik untuk Ethereum
                 eth_price_data = self.get_etherscan_data('stats', 'ethprice')
                 if eth_price_
                      data_points['eth_price_info'] = eth_price_data
             
             # Tambahkan placeholder untuk data aset lain (Glassnode, CryptoQuant, dll.)
             # Misalnya:
             # glassnode_key = self._rotate_key('glassnode')
             # if glassnode_key:
             #     # Panggil API Glassnode
             #     pass

             onchain_data[asset] = data_points if data_points else {}
        return onchain_data

# --- CONTOH PENGGUNAAN (Untuk debugging) ---
if __name__ == '__main__':
    # Untuk debugging, Anda perlu mocking `orchestrator`
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    print("intelligence_aggregator.py v4 siap untuk diintegrasikan.")
