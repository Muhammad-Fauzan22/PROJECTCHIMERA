# -*- coding: utf-8 -*-
# ==============================================================================
# == ORKESTRATOR UTAMA v3 - PROJECT CHIMERA ==
# ==============================================================================
#
# Lokasi: SENTIENT_CORE/chimera_orchestrator.py
# Deskripsi: Titik masuk utama sistem. Mengelola siklus hidup, inisialisasi
#            semua sub-sistem, dan memulai Cognitive Loop.
#
# ==============================================================================

import logging
import sys
import os
import time
import signal
import toml
from pathlib import Path

# --- PENYESUAIAN PATH DINAMIS UNTUK MENGATASI MASALAH IMPOR ---
# Mendapatkan path absolut dari direktori script ini
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Naik satu level untuk mendapatkan direktori root proyek (PROJECTCHIMERA)
project_root = os.path.dirname(current_script_dir)
# Menambahkan direktori root ke sys.path agar modul-modul bisa diimpor
sys.path.insert(0, str(project_root))
# --- AKHIR PENYESUAIAN PATH ---

class ChimeraOrchestrator:
    """
    Orkestrator utama yang mengelola siklus hidup dan semua sub-sistem robot.
    """

    def __init__(self):
        """
        Inisialisasi Orkestrator Utama v3.
        """
        print("Inisialisasi Orkestrator Chimera v3...")
        self.is_shutting_down = False

        # --- Memuat konfigurasi ---
        self.config = self._load_single_config("chimera_config.toml")
        self.risk_profile = self._load_single_config("risk_profile.toml")
        self.secrets = self._load_single_config("secrets.vault")
        self._setup_logging()

        # --- Inisialisasi semua sub-sistem ---
        logging.info("Mempersiapkan dan menginisialisasi semua Sub-Sistem...")
        try:
            # 1. API Manager: Pusat kendali untuk semua koneksi API eksternal
            from CONTROL_PANEL.api_manager import APIManager
            self.api_manager = APIManager(self)
            logging.info("APIManager berhasil diinisialisasi.")

            # 2. Perception System: Mata dan telinga robot
            from PERCEPTION_SYSTEM.perception_system import PerceptionSystem
            self.perception_system = PerceptionSystem(self)
            logging.info("PerceptionSystem berhasil diinisialisasi.")

            # 3. Strategic Cortex: Otak strategis yang menganalisis data
            from STRATEGIC_CORTEX.strategic_cortex import StrategicCortex
            self.strategic_cortex = StrategicCortex(self)
            logging.info("StrategicCortex berhasil diinisialisasi.")

            # 4. Execution System: Tangan dan kaki robot
            from EXECUTION_SYSTEM.execution_system import ExecutionSystem
            self.execution_system = ExecutionSystem(self)
            logging.info("ExecutionSystem berhasil diinisialisasi.")

            # 5. Cognitive Loop: Jantung yang mengatur siklus operasi
            from SENTIENT_CORE.cognitive_loop import CognitiveLoop
            self.cognitive_loop = CognitiveLoop(self)
            logging.info("CognitiveLoop berhasil diinisialisasi.")

            # 6. Risk Management Agent: Pelindung modal
            # from EXECUTION_SYSTEM.risk_management_agent import RiskManagementAgent
            # self.risk_management_agent = RiskManagementAgent(self)
            # logging.info("RiskManagementAgent berhasil diinisialisasi.")

            # 7. GDrive Synchronizer: Untuk arsip data
            # from COLLECTIVE_MEMORY.gdrive_synchronizer import GDriveSynchronizer
            # self.gdrive_sync = GDriveSynchronizer(self)
            # logging.info("GDriveSynchronizer berhasil diinisialisasi.")

            # 8. On-Chain Collector & Metric Generator
            # from GLOBAL_ANALYZER.ONCHAIN_INTELLIGENCE.onchain_collector import OnChainCollector
            # from GLOBAL_ANALYZER.ONCHAIN_INTELLIGENCE.metric_generator import OnChainMetricGenerator
            # self.onchain_collector = OnChainCollector(self)
            # self.metric_generator = OnChainMetricGenerator(self)
            # logging.info("Sub-sistem On-Chain Intelligence berhasil diinisialisasi.")

            # 9. News Aggregator (dengan IntelligentScraper)
            # from PERCEPTION_SYSTEM.global_intelligence.news_aggregator import NewsAggregator
            # self.news_aggregator = NewsAggregator(self)
            # logging.info("NewsAggregator (dengan IntelligentScraper) berhasil diinisialisasi.")

            # 10. Intelligent Scraper
            # from WEB_SCRAPERS.intelligent_scraper import IntelligentScraper
            # self.intelligent_scraper = IntelligentScraper(self)
            # logging.info("IntelligentScraper berhasil diinisialisasi.")

        except Exception as e:
            logging.critical(f"Kesalahan kritis saat menginisialisasi sub-sistem: {e}", exc_info=True)
            raise # Hentikan inisialisasi jika komponen inti gagal

        logging.info(">>> Semua Sub-Sistem berhasil dibuat dan terhubung.")
        logging.info("==================================================")

    def _load_single_config(self, filename: str) -> dict:
        """
        Memuat satu file konfigurasi TOML.
        Args:
            filename (str): Nama file di dalam folder CONFIG.
        Returns:
            dict: Dictionary konfigurasi yang dimuat.
        """
        try:
            config_path = Path(self.project_root) / "CONTROL_PANEL" / "CONFIG" / filename
            if not config_path.is_file():
                raise FileNotFoundError(f"File konfigurasi krusial '{filename}' tidak ditemukan.")
            print(f">>> Memuat file: {config_path}")
            with open(config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except Exception as e:
            print(f"\n[FATAL STARTUP ERROR]: Gagal memuat atau mem-parsing '{filename}': {e}")
            # Gunakan logging jika sudah siap, jika tidak, print ke console
            if 'logging' in globals() and logging.getLogger().hasHandlers():
                logging.critical(f"FATAL ERROR saat memuat '{filename}': {e}", exc_info=True)
            sys.exit(1)

    def _setup_logging(self):
        """Mengkonfigurasi sistem logging berdasarkan `chimera_config.toml`."""
        try:
            log_config = self.config.get('logging', {})
            log_file_path = log_config.get('log_file_path', 'COLLECTIVE_MEMORY/chimera_main.log')
            log_level = log_config.get('log_level', 'INFO').upper()
            
            # Pastikan path absolut untuk file log
            absolute_log_path = Path(self.project_root) / log_file_path
            # Buat direktori jika belum ada
            absolute_log_path.parent.mkdir(parents=True, exist_ok=True)

            # Konfigurasi logging
            logging.basicConfig(
                level=getattr(logging, log_level), # Konversi string ke level logging
                format='%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s',
                handlers=[
                    logging.FileHandler(absolute_log_path, mode='a', encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ],
                force=True # Untuk memastikan konfigurasi diterapkan ulang jika perlu
            )
            logging.info("Sistem logging berhasil dikonfigurasi.")
        except Exception as e:
            print(f"\n[FATAL STARTUP ERROR]: Gagal mengkonfigurasi logging: {e}")
            sys.exit(1)

    def start(self):
        """Memulai siklus utama robot."""
        logging.info("==================================================")
        logging.info("||   ORKESTRATOR CHIMERA MEMULAI LOOP KOGNITIF   ||")
        logging.info("==================================================")
        # Memulai loop kognitif yang tak terbatas
        self.cognitive_loop.start()

    def shutdown(self):
        """Menangani prosedur shutdown dengan anggun."""
        if self.is_shutting_down:
            return
        self.is_shutting_down = True

        logging.info("==================================================")
        logging.info("||   ORKESTRATOR CHIMERA MEMULAI PROSEDUR SHUTDOWN   ||")
        # Tambahkan logika shutdown untuk setiap komponen jika diperlukan
        # Misalnya, menyimpan state, menutup koneksi API, dll.
        # if self.gdrive_sync:
        #     self.gdrive_sync.save_final_state()
        logging.info("||   Sistem berhasil dimatikan. Selamat tinggal.   ||")
        logging.info("==================================================")

# --- TITIK MASUK EKSEKUSI SKRIP ---
# Blok ini dieksekusi saat Anda menjalankan: python -m SENTIENT_CORE.chimera_orchestrator
if __name__ == "__main__":
    orchestrator = None
    try:
        orchestrator = ChimeraOrchestrator()
        orchestrator.start()
    except KeyboardInterrupt:
        # Pesan ini akan muncul jika logging sudah siap
        if orchestrator and logging.getLogger().hasHandlers():
            logging.warning("Interupsi pengguna terdeteksi (Ctrl+C). Memulai prosedur shutdown...")
        else:
            print("\nInterupsi pengguna terdeteksi. Shutdown.")
        if orchestrator:
            orchestrator.shutdown()
    except Exception as e:
        # Pesan ini akan muncul jika logging sudah siap
        if orchestrator and logging.getLogger().hasHandlers():
            logging.critical(f"FATAL ERROR YANG TIDAK TERDUGA DALAM ORKESTRATOR: {e}", exc_info=True)
        else:
            print(f"FATAL ERROR SEBELUM LOGGING SIAP: {e}")
        if orchestrator:
            orchestrator.shutdown()
    finally:
        if orchestrator:
            orchestrator.shutdown()
