# -*- coding: utf-8 -*-
# ==============================================================================
# ==            TOOLKIT BINANCE FAULT-TOLERANT - PROJECT CHIMERA              ==
# ==============================================================================
#
# Lokasi: EXECUTION_SYSTEM/platform_integrations/binance_toolkit.py
# Deskripsi: Versi Fault-Tolerant. Kegagalan koneksi tidak akan menghentikan
#            seluruh bot, memungkinkan modul lain tetap berjalan.
#
# ==============================================================================

import ccxt
import logging
import time

class BinanceToolkit:
    """
    Wrapper CCXT yang tangguh dengan status koneksi yang jelas.
    """
    def __init__(self, orchestrator):
        logging.info("Inisialisasi Binance Toolkit (Fault-Tolerant)...")
        self.orchestrator = orchestrator
        self.client = None
        self.is_connected = False # <-- Atribut baru untuk melacak status koneksi
        self._connect_with_retry()

    def _connect_with_retry(self, max_retries=3, delay=5):
        """
        Mencoba terhubung ke Binance. Jika gagal, set is_connected = False.
        """
        try:
            secrets = self.orchestrator.secrets.get('exchange_apis', {})
            api_key = secrets.get('binance_api_key')
            secret_key = secrets.get('binance_secret_key')

            if not api_key or not secret_key:
                logging.warning("Kunci API Binance tidak ditemukan di secrets.vault. Fungsi trading akan dinonaktifkan.")
                self.is_connected = False
                return # Keluar dari fungsi, jangan error

            # ... (Opsi proxy tetap sama) ...
            proxies = {}
            if self.orchestrator.config.get('network', {}).get('use_proxy', False):
                proxy_url = self.orchestrator.config['network']['proxy_url']
                proxies = {'http': proxy_url, 'https': proxy_url}

            self.client = ccxt.binance({
                'apiKey': api_key,
                'secret': secret_key,
                'options': {'defaultType': 'future'},
                'proxies': proxies,
                'timeout': 20000,
            })
            
            # Tes koneksi
            self.client.fetch_time()
            logging.info(">>> Koneksi ke Binance Futures berhasil dibuat dan diverifikasi.")
            self.is_connected = True # <-- Set status menjadi terhubung

        except Exception as e:
            # Jika terjadi error apapun saat koneksi, catat sebagai warning dan lanjutkan
            logging.critical(f"Gagal total terhubung ke Binance setelah beberapa kali percobaan: {e}")
            logging.warning("Bot akan berjalan dalam mode 'DATA-ONLY'. Semua fungsi trading dinonaktifkan.")
            self.is_connected = False # <-- Pastikan status tidak terhubung

    def get_account_balance(self):
        """Mengambil saldo hanya jika terhubung."""
        if not self.is_connected:
            logging.warning("Tidak dapat mengambil saldo: Tidak terhubung ke Binance.")
            return None
        try:
            balance = self.client.fetch_balance()
            usdt_balance = balance['total'].get('USDT', 0)
            logging.info(f"Saldo akun futures: {usdt_balance:.2f} USDT")
            return usdt_balance
        except Exception as e:
            logging.error(f"Gagal mengambil saldo akun: {e}")
            self.is_connected = False # Set status ke false jika ada error
            return None

    # ... (fungsi lainnya seperti place_order juga harus memiliki 'if not self.is_connected:') ...