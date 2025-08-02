# -*- coding: utf-8 -*-
# ==============================================================================
# == MANAJER API CERDAS v5 - PROJECT CHIMERA ==
# ==============================================================================
# Lokasi: CONTROL_PANEL/api_manager.py
# Deskripsi: Kelas ini bertindak sebagai pusat kendali untuk semua koneksi API
#            eksternal dengan prioritas dan fallback berbasis Gemini.
# ==============================================================================

import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import sys
from pathlib import Path

# --- PENYESUAIAN PATH DINAMIS ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = Path(current_script_dir).parent
sys.path.insert(0, str(project_root))
# --- AKHIR PENYESUAIAN PATH ---

# --- Impor Gemini Pro untuk fallback cerdas ---
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    logging.info("Gemini Pro API tersedia untuk fallback.")
except ImportError:
    GEMINI_AVAILABLE = False
    logging.warning("Gemini Pro API tidak ditemukan. Fallback cerdas akan dinonaktifkan.")

class SmartAPIClient:
    """
    Klien HTTP yang cerdas dengan retry dan timeout.
    """
    def __init__(self, base_url, api_key=None, headers=None, timeout=5):
        self.base_url = base_url
        self.session = requests.Session()
        retry_strategy = Retry(
            total=2,  # Kurangi retry untuk kecepatan
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.headers = headers or {}
        if api_key:
            # Asumsi header umum, sesuaikan jika perlu
            self.headers['Authorization'] = f'Bearer {api_key}'
        self.timeout = timeout

    def get(self, endpoint, params=None):
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.warning(f"Permintaan ke {url} gagal: {e}")
            return None

class APIManager:
    """
    Mengelola semua koneksi API dengan prioritas dan fallback cerdas.
    """
    def __init__(self, orchestrator):
        logging.info("Inisialisasi Manajer API Cerdas v5...")
        self.orchestrator = orchestrator
        self.secrets = self.orchestrator.secrets
        self.clients = {}
        self._initialize_clients()
        
        # --- Inisialisasi Gemini untuk fallback ---
        if GEMINI_AVAILABLE:
            gemini_key = self.secrets.get('ai_apis', {}).get('gemini_api_key')
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    self.gemini_model = genai.GenerativeModel('gemini-pro')
                    logging.info("Gemini Pro berhasil dikonfigurasi untuk fallback.")
                except Exception as e:
                    logging.error(f"Gagal mengkonfigurasi Gemini Pro: {e}")
                    self.gemini_model = None
            else:
                self.gemini_model = None
                logging.warning("Kunci API Gemini Pro tidak ditemukan di secrets.")
        else:
            self.gemini_model = None
        # --- Akhir Inisialisasi Gemini ---
        
        logging.info("Manajer API Cerdas v5 berhasil diinisialisasi.")

    def _initialize_clients(self):
        """Inisialisasi klien untuk API dengan prioritas tinggi."""
        market_secrets = self.secrets.get('market_data_apis', {})
        intelligence_secrets = self.secrets.get('intelligence_apis', {})
        
        # --- 1. Binance (Prioritas Tertinggi) ---
        binance_key = self.secrets.get('exchange_apis', {}).get('binance_api_key')
        if binance_key:
            try:
                import ccxt
                binance_client = ccxt.binance({
                    'apiKey': binance_key,
                    'secret': self.secrets.get('exchange_apis', {}).get('binance_secret_key'),
                    'options': {'defaultType': 'spot'},
                    'enableRateLimit': True,
                    'timeout': 10000, # 10 detik
                })
                # Tes koneksi ringan
                binance_client.load_markets()
                self.clients['binance'] = binance_client
                logging.info("Klien CCXT Binance berhasil diinisialisasi.")
            except Exception as e:
                logging.error(f"Gagal menginisialisasi klien Binance: {e}")
                self.clients['binance'] = None
        else:
            self.clients['binance'] = None
            logging.warning("Kunci API Binance tidak ditemukan.")

        # --- 2. CoinGecko (Backup Utama) ---
        coingecko_key = market_secrets.get('coingecko_api_key')
        coingecko_headers = {'Authorization': f'Bearer {coingecko_key}'} if coingecko_key else {}
        self.clients['coingecko'] = SmartAPIClient(
            'https://api.coingecko.com/api/v3',
            headers=coingecko_headers
        )
        logging.info("Klien CoinGecko (backup) diinisialisasi.")

        # --- 3. CoinMarketCap (Backup) ---
        cmc_key = market_secrets.get('coinmarketcap_api_key')
        cmc_headers = {'X-CMC_PRO_API_KEY': cmc_key} if cmc_key else {}
        self.clients['coinmarketcap'] = SmartAPIClient(
            'https://pro-api.coinmarketcap.com/v1',
            headers=cmc_headers
        )
        logging.info("Klien CoinMarketCap (backup) diinisialisasi.")

        # --- 4. Alpha Vantage (Data Makro) ---
        av_key = market_secrets.get('alpha_vantage_api_key')
        av_headers = {} # Alpha Vantage biasanya menggunakan parameter ?apikey=
        self.clients['alpha_vantage'] = SmartAPIClient(
            'https://www.alphavantage.co/query',
            headers=av_headers # Kunci akan dikirim sebagai parameter
        )
        logging.info("Klien Alpha Vantage (data makro) diinisialisasi.")

        # --- 5. NewsAPI (Berita & Sentimen) ---
        newsapi_key = intelligence_secrets.get('newsapi_key')
        newsapi_headers = {} # Gunakan parameter
        self.clients['newsapi'] = SmartAPIClient(
            'https://newsapi.org/v2',
            headers=newsapi_headers # Kunci akan dikirim sebagai parameter
        )
        logging.info("Klien NewsAPI (berita) diinisialisasi.")

        # Tambahkan inisialisasi untuk API lain jika diperlukan (Messari, Etherscan, dll.)

    def get_client(self, client_name):
        """Mendapatkan klien API yang telah diinisialisasi."""
        return self.clients.get(client_name)

    def fetch_with_fallback(self, primary_func, fallback_funcs, gemini_prompt=None):
        """
        Mencoba fungsi utama, jika gagal, coba fungsi fallback secara berurutan.
        Jika semua gagal dan ada prompt Gemini, gunakan Gemini sebagai fallback terakhir.
        """
        try:
            result = primary_func()
            if result is not None:
                logging.debug("Data berhasil diambil dari sumber utama.")
                return result
        except Exception as e:
            logging.warning(f"Fungsi utama gagal: {e}")

        for i, fallback_func in enumerate(fallback_funcs):
            try:
                result = fallback_func()
                if result is not None:
                    logging.debug(f"Data berhasil diambil dari fallback #{i+1}.")
                    return result
            except Exception as e:
                logging.warning(f"Fungsi fallback #{i+1} gagal: {e}")
                continue

        # --- Fallback Terakhir: Gemini Pro ---
        if self.gemini_model and gemini_prompt:
            try:
                logging.info("Menggunakan Gemini Pro sebagai fallback terakhir...")
                # Batasi panjang prompt untuk efisiensi
                if len(gemini_prompt) > 10000: # Misalnya
                     gemini_prompt = gemini_prompt[:10000] + "\n... [Prompt terpotong untuk efisiensi]"
                response = self.gemini_model.generate_content(gemini_prompt)
                # Asumsikan respons adalah JSON string yang valid
                # Dalam praktiknya, Anda mungkin perlu mem-parsing teks respons
                # dan mengubahnya menjadi struktur data.
                # Untuk sekarang, kita asumsikan ia mengembalikan dict.
                if response and response.text:
                    import json
                    # Ini sangat bergantung pada format output yang diminta dari Gemini
                    # Prompt harus meminta output dalam format JSON.
                    try:
                        # Coba parsing JSON jika respons diminta sebagai JSON
                        data = json.loads(response.text)
                        logging.info("Data berhasil diambil melalui Gemini Pro.")
                        return data
                    except json.JSONDecodeError:
                        # Jika bukan JSON, kembalikan teks
                        logging.info("Data teks diambil melalui Gemini Pro.")
                        return {"gemini_fallback_text": response.text}
            except Exception as e:
                logging.error(f"Gemini Pro fallback gagal: {e}")
        # --- Akhir Fallback Gemini ---

        logging.error("Semua sumber data dan fallback gagal.")
        return None

# --- CONTOH PENGGUNAAN ---
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    print("api_manager.py v5 siap.")
