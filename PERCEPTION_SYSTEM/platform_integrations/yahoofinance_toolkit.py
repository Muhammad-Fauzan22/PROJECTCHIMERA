# -*- coding: utf-8 -*-
# ==============================================================================
# ==              TOOLKIT YAHOO FINANCE - PROJECT CHIMERA GENESIS             ==
# ==============================================================================
#
# Lokasi: PERCEPTION_SYSTEM/platform_integrations/yahoofinance_toolkit.py
# Deskripsi: Modul ini berfungsi sebagai adapter untuk library yfinance.
#            Tujuannya adalah untuk menyediakan cara yang mudah dan andal
#            dalam mengambil data harga historis dari Yahoo Finance, yang dapat
#            digunakan untuk analisis, backtesting, atau melatih model.
#
# ==============================================================================

# --- Import Library Standar ---
import logging

# --- Import Library Pihak Ketiga ---
# Pastikan library berikut sudah terinstal:
# pip install yfinance numpy
import yfinance as yf
import numpy as np

# Konfigurasi logging dasar untuk modul ini
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')


class YahooFinanceToolkit:
    """
    Kelas yang menyediakan fungsionalitas untuk mengambil data pasar
    dari API publik Yahoo Finance.
    """

    def __init__(self):
        """
        Konstruktor untuk YahooFinanceToolkit.
        """
        logging.info("Inisialisasi Yahoo Finance Toolkit...")
        logging.info(">>> Yahoo Finance Toolkit berhasil diinisialisasi.")


    def get_historical_data(self, symbol: str, period: str = '7d', interval: str = '1h') -> np.ndarray:
        """
        Mengambil data harga penutupan (Close) historis untuk simbol tertentu.

        Args:
            symbol (str): Simbol ticker sesuai format Yahoo Finance (misal: 'BTC-USD').
            period (str): Durasi data yang akan diambil (contoh: '1d', '5d', '1mo', '1y').
            interval (str): Frekuensi atau interval data (contoh: '1m', '5m', '1h', '1d').

        Returns:
            np.ndarray: Sebuah array NumPy berisi data harga penutupan.
                        Mengembalikan array kosong jika terjadi error atau tidak ada data.
        """
        logging.info(f"Mencoba mengambil data historis untuk '{symbol}' (Periode: {period}, Interval: {interval})...")
        try:
            # Membuat objek Ticker dari yfinance
            ticker = yf.Ticker(symbol)

            # Mengambil data historis
            hist_data = ticker.history(period=period, interval=interval)

            # Pemeriksaan keamanan: Pastikan data tidak kosong
            if hist_data.empty:
                logging.warning(f"Tidak ada data yang ditemukan untuk simbol '{symbol}' dengan parameter yang diberikan.")
                return np.array([])

            # Ekstrak hanya kolom 'Close' dan konversi ke NumPy array
            close_prices = hist_data['Close'].values

            logging.info(f"Berhasil mengambil {len(close_prices)} titik data untuk '{symbol}'.")
            return close_prices

        except Exception as e:
            # Menangkap semua kemungkinan error dari library yfinance
            # (misal: koneksi gagal, simbol tidak valid, dll)
            logging.error(f"Gagal mengambil data untuk '{symbol}'. Error: {e}")
            return np.array([])