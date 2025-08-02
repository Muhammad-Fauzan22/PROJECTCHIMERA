# -*- coding: utf-8 -*-
# ==============================================================================
# ==                TOOLKIT COINGECKO - PROJECT CHIMERA GENESIS               ==
# ==============================================================================
#
# Lokasi: PERCEPTION_SYSTEM/platform_integrations/coingecko_toolkit.py
# Deskripsi: Modul ini berfungsi sebagai adapter untuk library pycoingecko.
#            Tujuannya adalah untuk menyediakan cara yang andal dalam mengambil
#            data pasar dari CoinGecko, yang bisa digunakan sebagai sumber
#            data primer atau sekunder.
#
# ==============================================================================

# --- Import Library Standar ---
import logging
import sys

# --- Import Library Pihak Ketiga ---
# Pastikan library berikut sudah terinstal:
# pip install pycoingecko numpy
try:
    from pycoingecko import CoinGeckoAPI
except ImportError:
    logging.critical("Error: Library 'pycoingecko' tidak ditemukan. Silakan instal dengan 'pip install pycoingecko'")
    sys.exit(1)

import numpy as np

# Konfigurasi logging dasar untuk modul ini
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')


class CoinGeckoToolkit:
    """
    Kelas yang menyediakan fungsionalitas untuk mengambil data pasar
    dari API CoinGecko.
    """

    def __init__(self, orchestrator):
        """
        Konstruktor untuk CoinGeckoToolkit.

        Args:
            orchestrator (ChimeraOrchestrator): Instance dari orkestrator utama.
        """
        logging.info("Inisialisasi CoinGecko Toolkit...")
        self.cg = None

        # Mengambil kunci API dari 'secrets' yang sudah dimuat oleh orkestrator.
        # Ini mengasumsikan 'secrets.vault' memiliki seksi [market_data_apis].
        try:
            api_key = orchestrator.secrets['market_data_apis']['coingecko_key']

            if "MASUKKAN_API_KEY" in api_key:
                logging.warning("Kunci API CoinGecko masih menggunakan nilai placeholder. Menggunakan API publik (rate limit lebih rendah).")
                # Inisialisasi tanpa kunci untuk menggunakan API publik
                self.cg = CoinGeckoAPI()
            else:
                # Inisialisasi dengan kunci API untuk akses Pro
                self.cg = CoinGeckoAPI(api_key=api_key)
                logging.info("Klien CoinGecko diinisialisasi dengan kunci API Pro.")

            logging.info(">>> CoinGecko Toolkit berhasil diinisialisasi.")

        except (KeyError, TypeError):
            logging.error("Seksi [market_data_apis] atau 'coingecko_key' tidak ditemukan di file secrets. Menginisialisasi dengan API publik.")
            self.cg = CoinGeckoAPI()
        except Exception as e:
            logging.critical(f"Terjadi error tak terduga saat inisialisasi CoinGeckoToolkit: {e}")


    def get_historical_data(self, coin_id: str = 'bitcoin', vs_currency: str = 'usd', days: int = 7) -> np.ndarray:
        """
        Mengambil data harga historis dari CoinGecko.

        Args:
            coin_id (str): ID koin sesuai CoinGecko (contoh: 'bitcoin', 'ethereum').
            vs_currency (str): Mata uang pembanding (contoh: 'usd', 'idr').
            days (int): Jumlah hari data historis yang akan diambil.

        Returns:
            np.ndarray: Sebuah array NumPy berisi data harga.
                        Mengembalikan array kosong jika terjadi error.
        """
        if not self.cg:
            logging.error("Pengambilan data dibatalkan. Klien CoinGecko belum terinisialisasi.")
            return np.array([])

        logging.info(f"Mencoba mengambil data historis untuk '{coin_id}' vs '{vs_currency}' ({days} hari terakhir)...")
        try:
            # Memanggil API untuk mendapatkan data market chart
            market_chart = self.cg.get_coin_market_chart_by_id(
                id=coin_id,
                vs_currency=vs_currency,
                days=days
            )

            # Data harga adalah list of lists, di mana setiap elemen adalah [timestamp, harga]
            # Kita hanya perlu mengekstrak harganya.
            prices = [item[1] for item in market_chart['prices']]

            if not prices:
                logging.warning(f"Tidak ada data harga yang ditemukan untuk '{coin_id}'.")
                return np.array([])

            logging.info(f"Berhasil mengambil {len(prices)} titik data untuk '{coin_id}'.")
            return np.array(prices)

        except Exception as e:
            # Menangkap semua kemungkinan error dari API (koneksi, id tidak valid, dll.)
            logging.error(f"Gagal mengambil data dari CoinGecko untuk '{coin_id}'. Error: {e}")
            return np.array([])