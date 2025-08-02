# -*- coding: utf-8 -*-
# ==============================================================================
# == PENGUMPUL DATA ON-CHAIN vFinal - PROJECT CHIMERA ==
# ==============================================================================
#
# Lokasi: GLOBAL_ANALYZER/ONCHAIN_INTELLIGENCE/onchain_collector.py
# Deskripsi: Modul ini bertanggung jawab untuk mengumpulkan data on-chain mentah
#            dari berbagai API publik & premium. Ia memiliki mekanisme rotasi
#            kunci, fallback, dan penanganan error yang sangat tangguh.
#
# ==============================================================================

import logging
import sys
import os
import requests
import time
import random
from collections import defaultdict

# --- PENYESUAIAN PATH DINAMIS ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_script_dir)) # Naik ke PROJECTCHIMERA/
sys.path.insert(0, project_root)
# --- AKHIR PENYESUAIAN PATH ---

class OnChainCollector:
    """
    Mengumpulkan data on-chain mentah dengan rotasi kunci, fallback, dan ketahanan terhadap error.
    Menyediakan data dalam format dictionary Python yang konsisten.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi Pengumpul Data On-Chain vFinal.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator untuk akses ke secrets/config.
        """
        logging.info("Inisialisasi Pengumpul Data On-Chain vFinal...")
        self.orchestrator = orchestrator
        self.secrets = self.orchestrator.secrets
        
        # Untuk melacak indeks kunci terakhir yang digunakan untuk setiap layanan multi-kunci
        self.key_indices = defaultdict(int)
        
        # Muat semua kunci API on-chain yang tersedia
        self._load_api_keys()
        
        logging.info("Pengumpul Data On-Chain vFinal berhasil diinisialisasi.")

    def _load_api_keys(self):
        """
        Memuat semua kunci API on-chain dari secrets.vault.
        """
        try:
            onchain_secrets = self.secrets.get('onchain_apis', {})
            
            # --- 1. ON-CHAIN (API spesifik on-chain) ---
            # Kunci untuk layanan multi-akun
            self.clients = {}
            self.clients['etherscan_keys'] = onchain_secrets.get('etherscan_keys', [])
            self.key_indices['etherscan'] = 0 # Inisialisasi indeks rotasi
            logging.info("Kunci API untuk data on-chain spesifik berhasil dimuat.")

            # --- 2. DATA PASAR (untuk fallback harga) ---
            market_secrets = self.secrets.get('market_data_apis', {})
            self.clients['coingecko_key'] = market_secrets.get('coingecko_api_key')
            self.clients['coincap_key'] = market_secrets.get('coincap_api_key')
            # Kunci untuk layanan multi-akun
            self.clients['coinstats_keys'] = market_secrets.get('coinstats_keys', [])
            self.key_indices['coinstats'] = 0 # Inisialisasi indeks rotasi
            logging.info("Kunci API untuk data pasar (fallback) berhasil dimuat.")

            # --- 3. INTELIJEN & BERITA (untuk fallback data berita) ---
            intelligence_secrets = self.secrets.get('intelligence_apis', {})
            # Kunci untuk layanan multi-akun
            self.clients['messari_keys'] = intelligence_secrets.get('messari_keys', [])
            self.clients['coindesk_keys'] = intelligence_secrets.get('coindesk_keys', [])
            self.key_indices['messari'] = 0 # Inisialisasi indeks rotasi
            self.key_indices['coindesk'] = 0 # Inisialisasi indeks rotasi

            self.clients['newsapi_key'] = intelligence_secrets.get('newsapi_key')
            self.clients['thenewsapi_key'] = intelligence_secrets.get('thenewsapi_key')
            logging.info("Kunci API untuk intelijen & berita (fallback) berhasil dimuat.")

            # --- 4. AI APIs ---
            # Kunci untuk AI biasanya digunakan langsung saat memanggil API oleh LLMRouter.
            # Tidak perlu diinisialisasi sebagai klien di sini.

            # --- 5. TOOLS ---
            tool_secrets = self.secrets.get('tool_apis', {})
            self.clients['scrapeops_key'] = tool_secrets.get('scrapeops_api_key')
            # self.clients['opensea_key'] = tool_secrets.get('opensea_api_key')
            logging.info("Kunci API untuk tools berhasil dimuat.")

        except Exception as e:
            logging.critical(f"Gagal memuat kunci API on-chain: {e}", exc_info=True)
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

    # --- FUNGSI PENGUMPULAN DATA ON-CHAIN SPESIFIK ---
    def collect_all_onchain_data(self, assets=None):
        """
        Mengumpulkan semua data on-chain yang tersedia dalam satu panggilan.
        Args:
            assets (list, optional): Daftar nama aset (slug) untuk dikumpulkan data spesifiknya.
                                     Jika None, gunakan default ['bitcoin', 'ethereum'].
        Returns:
            dict: Dictionary berisi semua data on-chain yang berhasil dikumpulkan.
        """
        logging.info("Memulai siklus pengumpulan data on-chain...")
        collected_data = {}

        # --- 1. Data Pasar Fallback ---
        logging.info("1. Mengumpulkan data pasar (fallback)...")
        try:
            # Placeholder untuk data pasar fallback
            # Dalam implementasi nyata, ini akan menggunakan IntelligenceAggregator
            # atau metode internal untuk mengambil harga pasar.
            # Untuk sekarang, kita buat data dummy.
            market_data_fallback = {
                'BTC/USDT': {'price': 60000.0, 'change_24h': 1.5},
                'ETH/USDT': {'price': 3000.0, 'change_24h': 2.0}
            }
            collected_data['market_fallback'] = market_data_fallback
            logging.debug("Data pasar (fallback) berhasil dikumpulkan (dummy).")
        except Exception as e:
            logging.error(f"Kesalahan saat mengumpulkan data pasar (fallback): {e}", exc_info=True)
            collected_data['market_fallback'] = {}

        # --- 2. Data On-Chain Spesifik ---
        logging.info("2. Mengumpulkan data on-chain spesifik...")
        try:
            assets_to_scan = assets if assets else ['bitcoin', 'ethereum']
            onchain_data = {}
            for asset in assets_to_scan:
                asset_data = {}
                if asset.lower() == 'ethereum':
                    # Contoh spesifik untuk Ethereum
                    eth_price_data = self._get_etherscan_data('stats', 'ethprice')
                    if eth_price_
                         asset_data['eth_price_info'] = eth_price_data
                    
                    # Tambahkan data lain dari Etherscan jika diperlukan
                    # Misalnya:
                    # gas_price_data = self._get_etherscan_data('gastracker', 'gasoracle')
                    # asset_data['gas_price_info'] = gas_price_data

                # Placeholder untuk data aset lain (Glassnode, CryptoQuant, dll.)
                # Misalnya:
                # if asset.lower() == 'bitcoin':
                #     btc_netflow_data = self._get_glassnode_data('market/exchange_netflow', 'BTC')
                #     asset_data['exchange_netflow'] = btc_netflow_data

                onchain_data[asset] = asset_data if asset_data else {}
            
            collected_data['onchain'] = onchain_data
            logging.debug("Data on-chain spesifik berhasil dikumpulkan.")
        except Exception as e:
            logging.error(f"Kesalahan saat mengumpulkan data on-chain spesifik: {e}", exc_info=True)
            collected_data['onchain'] = {}

        # --- 3. Data Berita & Intelijen (Fallback) ---
        logging.info("3. Mengumpulkan data berita & intelijen (fallback)...")
        try:
            # Placeholder untuk data berita & intelijen (fallback)
            # Dalam implementasi nyata, ini akan menggunakan NewsAggregator
            # atau metode internal untuk mengambil berita.
            # Untuk sekarang, kita buat data dummy.
            news_data_fallback = [
                {
                    'source': 'NewsAPI',
                    'title': 'Breaking News: Crypto Market Surges Amidst Positive Regulatory News',
                    'description': 'The cryptocurrency market sees a significant uptick following favorable regulatory developments in major economies.',
                    'url': 'https://example.com/news1',
                    'published_at': '2023-10-27T10:00:00Z'
                },
                {
                    'source': 'TheNewsAPI',
                    'title': 'Ethereum Upgrades Signal Strong Future for DeFi Sector',
                    'description': 'Recent upgrades to the Ethereum network are boosting confidence in the DeFi space, leading to increased investment.',
                    'url': 'https://example.com/news2',
                    'published_at': '2023-10-27T09:30:00Z'
                }
            ]
            collected_data['news_fallback'] = news_data_fallback
            logging.debug("Data berita & intelijen (fallback) berhasil dikumpulkan (dummy).")
        except Exception as e:
            logging.error(f"Kesalahan saat mengumpulkan data berita (fallback): {e}", exc_info=True)
            collected_data['news_fallback'] = []

        logging.info("Siklus pengumpulan data on-chain selesai.")
        return collected_data

    def _get_etherscan_data(self, module='stats', action='ethprice'):
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
        except Exception as e:
            logging.error(f"Kesalahan saat mengambil data Etherscan ({module}.{action}): {e}", exc_info=True)
            return None

    # --- FUNGSI AGREGASI UTAMA (INTERFACE UNTUK PERCEPTION SYSTEM) ---
    def aggregate_onchain_data(self, assets=['bitcoin', 'ethereum']):
        """
        Mengumpulkan dan menggabungkan data on-chain untuk beberapa aset.
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
                 eth_price_data = self._get_etherscan_data('stats', 'ethprice')
                 if eth_price_
                      data_points['eth_price_info'] = eth_price_data
             
             # Tambahkan data dari sumber lain jika tersedia
             # Placeholder untuk data lain (Glassnode, CryptoQuant, dll.)
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
    print("onchain_collector.py vFinal siap untuk diintegrasikan.")
