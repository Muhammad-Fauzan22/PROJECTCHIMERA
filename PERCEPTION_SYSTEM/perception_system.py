# -*- coding: utf-8 -*-
# ==============================================================================
# == SISTEM PERSEPSI vFinal - PROJECT CHIMERA ==
# ==============================================================================
#
# Lokasi: PERCEPTION_SYSTEM/perception_system.py
# Deskripsi: Sistem persepsi yang menyeluruh, mengintegrasikan data pasar,
#            on-chain, berita (API & scraping), dan tren sosial.
#            Menyimpan snapshot ke Collective Memory (Google Drive).
#
# ==============================================================================

import logging
import sys
import os
import time
import datetime as dt
import pandas as pd
from collections import defaultdict

# --- PENYESUAIAN PATH DINAMIS UNTUK MENGATASI MASALAH IMPOR ---
# Mendapatkan path absolut dari direktori script ini
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Naik ke direktori root proyek (PROJECTCHIMERA)
# PERCEPTION_SYSTEM/ -> PROJECTCHIMERA/
project_root = os.path.dirname(current_script_dir)
# Menambahkan direktori root ke sys.path agar modul-modul bisa diimpor
sys.path.insert(0, project_root)
# --- AKHIR PENYESUAIAN PATH ---

# Impor komponen lain dari proyek
try:
    from CONTROL_PANEL.api_manager import APIManager
    from COLLECTIVE_MEMORY.gdrive_synchronizer import GDriveSynchronizer
    from GLOBAL_ANALYZER.ONCHAIN_INTELLIGENCE.onchain_collector import OnChainCollector
    from GLOBAL_ANALYZER.ONCHAIN_INTELLIGENCE.metric_generator import OnChainMetricGenerator
    from PERCEPTION_SYSTEM.global_intelligence.news_aggregator import NewsAggregator
    from WEB_SCRAPERS.intelligent_scraper import IntelligentScraper
    logging.info("Semua komponen PerceptionSystem berhasil diimpor.")
except ImportError as e:
    logging.critical(f"Gagal mengimpor komponen PerceptionSystem: {e}")
    raise

class PerceptionSystem:
    """
    Mengumpulkan, memproses, dan menyimpan data dari semua sumber intelijen:
    - Data pasar (harga, volume, dll) dari berbagai API.
    - Data on-chain (aktivitas jaringan, metrik) dari API on-chain.
    - Data berita & sentimen (dari API dan hasil scraping cerdas).
    Data ini digabung menjadi satu 'snapshot persepsi' untuk siklus kognitif.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi Sistem Persepsi vFinal.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator.
        """
        logging.info("Inisialisasi Sistem Persepsi vFinal...")
        self.orchestrator = orchestrator

        # --- Inisialisasi semua sub-komponen ---
        try:
            # 1. APIManager: Pusat kendali untuk semua koneksi API eksternal
            self.api_manager = self.orchestrator.api_manager
            logging.info("APIManager berhasil diinisialisasi.")

            # 2. GDriveSynchronizer: Untuk arsip snapshot
            self.gdrive_sync = GDriveSynchronizer(self.orchestrator)
            logging.info("GDriveSynchronizer berhasil diinisialisasi.")

            # 3. On-Chain Intelligence
            self.onchain_collector = OnChainCollector(self.orchestrator)
            self.metric_generator = OnChainMetricGenerator(self.orchestrator, self.api_manager)
            logging.info("Sub-sistem On-Chain Intelligence berhasil diinisialisasi.")

            # 4. News Aggregator (dengan scraping)
            self.news_aggregator = NewsAggregator(self.orchestrator)
            logging.info("NewsAggregator (dengan IntelligentScraper) berhasil diinisialisasi.")

            # 5. IntelligentScraper: Untuk scraping data tambahan
            self.intelligent_scraper = IntelligentScraper(self.orchestrator)
            logging.info("IntelligentScraper berhasil diinisialisasi.")

        except Exception as e:
            logging.critical(f"Kesalahan kritis saat menginisialisasi sub-komponen PerceptionSystem: {e}", exc_info=True)
            raise # Hentikan inisialisasi jika komponen inti gagal

        # Konfigurasi
        self.assets_to_scan = self.orchestrator.config.get('market', {}).get('assets', ['BTC/USDT', 'ETH/USDT'])
        self.gdrive_folder_id = self.orchestrator.config.get('gdrive', {}).get('raw_data_folder_id', None)
        logging.info("Sistem Persepsi vFinal berhasil diinisialisasi.")

    def scan(self, specific_symbols=None, specific_assets=None):
        """
        Metode utama yang dipanggil oleh Cognitive Loop untuk mendapatkan snapshot pasar.
        Args:
            specific_symbols (list, optional): Daftar simbol spesifik untuk di-scan.
            specific_assets (list, optional): Daftar nama aset on-chain spesifik untuk di-scan.
        Returns:
            dict: Snapshot persepsi yang menyeluruh dari kondisi pasar saat ini.
        """
        logging.info("--- Memulai Siklus Persepsi Komprehensif ---")
        perception_start_time = dt.datetime.utcnow()

        perception_snapshot = {
            'timestamp': perception_start_time.isoformat() + 'Z',
            'sources': {}, # Untuk melacak sumber data mana yang berhasil/gagal
            'market_data': {},
            'onchain': {},
            'news': {}, # Data berita dari API dan scraping
            'social': {}, # Placeholder untuk data sosial jika tersedia
            'errors': [] # Untuk mencatat error non-kritis
        }

        # --- 1. Kumpulkan Data Pasar ---
        logging.info("1. Mengumpulkan data pasar...")
        try:
            symbols_to_scan = specific_symbols if specific_symbols else self.assets_to_scan
            market_data = {}
            
            # Gunakan APIManager untuk mengumpulkan data pasar dari berbagai sumber
            # Ini akan menggunakan fallback internal (Binance API -> CoinGecko -> CoinCap -> CoinStats)
            market_data = self.api_manager.aggregate_market_data(symbols=symbols_to_scan)
            
            perception_snapshot['market_data'] = market_data
            perception_snapshot['sources']['market_data'] = 'success' if market_data else 'no_data'
            successful_symbols = list(market_data.keys()) if market_data else []
            logging.debug(f"Data pasar untuk {len(successful_symbols)} simbol dikumpulkan.")
        except Exception as e:
            error_msg = f"Kesalahan saat mengumpulkan data pasar: {e}"
            logging.error(error_msg, exc_info=True)
            perception_snapshot['errors'].append({'component': 'market_data', 'error': str(e)})
            perception_snapshot['sources']['market_data'] = 'failed'

        # --- 2. Kumpulkan Data On-Chain ---
        logging.info("2. Mengumpulkan data on-chain...")
        try:
            if self.onchain_collector and self.metric_generator:
                # Fokus pada BTC dan ETH untuk on-chain data jika tidak spesifik
                assets_to_scan_onchain = specific_assets if specific_assets else ['bitcoin', 'ethereum'] 
                raw_onchain_data = self.onchain_collector.collect_all_onchain_data(assets=assets_to_scan_onchain)
                onchain_metrics = self.metric_generator.generate_all_metrics(raw_onchain_data)
                perception_snapshot['onchain'] = onchain_metrics
                perception_snapshot['sources']['onchain'] = 'success' if raw_onchain_data else 'no_data'
                logging.debug("Data on-chain berhasil dikumpulkan dan diproses.")
            else:
                 logging.info("Sub-sistem On-Chain tidak tersedia. Melewati pengumpulan data on-chain.")
                 perception_snapshot['sources']['onchain'] = 'unavailable'
        except Exception as e:
            error_msg = f"Kesalahan saat mengumpulkan data on-chain: {e}"
            logging.error(error_msg, exc_info=True)
            perception_snapshot['errors'].append({'component': 'onchain', 'error': str(e)})
            perception_snapshot['sources']['onchain'] = 'failed'

        # --- 3. Kumpulkan Data Berita & Intelijen ---
        logging.info("3. Mengumpulkan data berita & intelijen...")
        try:
             if self.news_aggregator:
                 # Gunakan NewsAggregator yang terintegrasi dengan IntelligentScraper dan API
                 aggregated_intelligence = self.news_aggregator.aggregate_all()
                 perception_snapshot['news'] = aggregated_intelligence
                 perception_snapshot['sources']['news_intel'] = 'success' if aggregated_intelligence else 'no_data'
                 logging.debug("Data berita & intelijen berhasil dikumpulkan.")
             else:
                 logging.info("NewsAggregator tidak tersedia. Melewati pengumpulan data berita.")
                 perception_snapshot['sources']['news_intel'] = 'unavailable'
        except Exception as e:
            error_msg = f"Kesalahan saat mengumpulkan data berita/intelijen: {e}"
            logging.error(error_msg, exc_info=True)
            perception_snapshot['errors'].append({'component': 'news_intel', 'error': str(e)})
            perception_snapshot['sources']['news_intel'] = 'failed'

        # --- 4. Finalisasi Snapshot & Arsipkan ---
        perception_end_time = dt.datetime.utcnow()
        perception_duration = (perception_end_time - perception_start_time).total_seconds()
        perception_snapshot['processing_time_seconds'] = perception_duration
        logging.info(f"--- Siklus Persepsi Komprehensif Selesai (Durasi: {perception_duration:.2f}s) ---")

        # --- 5. Arsipkan snapshot ke Google Drive ---
        if self.gdrive_sync and self.gdrive_folder_id:
            try:
                logging.info("Mengarsipkan snapshot ke Collective Memory (Google Drive)...")
                # Gunakan json_normalize untuk membuat DataFrame yang rapi
                df_snapshot = pd.json_normalize(perception_snapshot, sep='_')
                timestamp_str = perception_start_time.strftime("%Y%m%d_%H%M%S")
                filename = f"perception_snapshot_{timestamp_str}.csv"

                # Unggah menggunakan GDriveSynchronizer
                self.gdrive_sync.upload_data_as_csv(df_snapshot, filename, self.gdrive_folder_id)
                logging.info("Snapshot berhasil diarsipkan.")
            except Exception as e:
                error_msg = f"Gagal mengunggah snapshot ke Google Drive: {e}"
                logging.error(error_msg, exc_info=True)
                perception_snapshot['errors'].append({'component': 'archive', 'error': str(e)})
        else:
             logging.info("GDriveSynchronizer tidak tersedia atau folder ID tidak diset. Melewati pengarsipan.")

        return perception_snapshot

# --- CONTOH PENGGUNAAN (Untuk debugging) ---
if __name__ == '__main__':
    # Untuk debugging, Anda perlu mocking `orchestrator`
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    print("perception_system.py vFinal siap untuk diintegrasikan.")
