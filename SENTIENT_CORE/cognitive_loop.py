# -*- coding: utf-8 -*-
# ==============================================================================
# == LOOP KOGNITIF v3 - PROJECT CHIMERA ==
# ==============================================================================
#
# Lokasi: SENTIENT_CORE/cognitive_loop.py
# Deskripsi: "Jantung" dari sistem. Ia menjalankan siklus kognitif tak terbatas:
#            Persepsi -> Analisis -> Aksi -> Evaluasi.
#
# ==============================================================================

import logging
import time
import signal
import sys
import os

# --- PENYESUAIAN PATH DINAMIS UNTUK MENGATASI MASALAH IMPOR ---
# Mendapatkan path absolut dari direktori script ini
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Naik satu level untuk mendapatkan direktori root proyek (PROJECTCHIMERA)
project_root = os.path.dirname(current_script_dir)
# Menambahkan direktori root ke sys.path agar modul-modul bisa diimpor
sys.path.insert(0, str(project_root))
# --- AKHIR PENYESUAIAN PATH ---

class CognitiveLoop:
    """
    Kelas utama yang menjalankan siklus kognitif bot trading.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi Cognitive Loop v3.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator.
        """
        logging.info("Inisialisasi Cognitive Loop v3...")
        self.orchestrator = orchestrator
        self.is_running = False
        self.loop_interval = self.orchestrator.config.get('system', {}).get('cognitive_loop_interval_seconds', 15)
        logging.info("Cognitive Loop v3 berhasil diinisialisasi.")

    def start(self):
        """
        Memulai loop kognitif yang berjalan terus-menerus.
        """
        logging.info("Memulai Cognitive Loop...")
        self.is_running = True

        # Handler untuk interupsi (Ctrl+C)
        def signal_handler(sig, frame):
            logging.info("Interupsi diterima (Ctrl+C). Menghentikan Cognitive Loop...")
            self.stop()
            # Keluar dari program
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        try:
            cycle_count = 0
            while self.is_running:
                cycle_start_time = time.time()
                self._run_single_cycle()
                cycle_end_time = time.time()

                cycle_count += 1
                cycle_duration = cycle_end_time - cycle_start_time
                logging.debug(f"Siklus #{cycle_count} selesai dalam {cycle_duration:.2f} detik.")

                # Tidur sejenak sebelum siklus berikutnya untuk menghindari beban berlebih
                # Misalnya, siklus setiap 15 detik. Sesuaikan dengan kebutuhan.
                time_to_sleep = max(1.0, self.loop_interval - cycle_duration)
                if self.is_running: # Cek lagi sebelum tidur
                    time.sleep(time_to_sleep)

        except Exception as e:
            logging.critical(f"Kesalahan kritis dalam loop utama: {e}", exc_info=True)
        finally:
            self.stop()
            logging.info("Cognitive Loop telah dihentikan.")

    def _run_single_cycle(self):
        """
        Menjalankan satu siklus lengkap dari proses kognitif.
        1. Scan lingkungan (Perception).
        2. Analisis data (Strategic Cortex).
        3. Eksekusi keputusan (Execution System).
        """
        try:
            logging.info("--- Memulai Siklus Kognitif Baru ---")

            # --- 1. Persepsi: Mengumpulkan data dari dunia luar ---
            perception_snapshot = self.orchestrator.perception_system.scan()
            if not perception_snapshot:
                logging.warning("PerceptionSystem mengembalikan data kosong. Melewati siklus ini.")
                return

            # --- 2. Analisis: Mengubah data menjadi keputusan ---
            strategic_decision = self.orchestrator.strategic_cortex.analyze(perception_snapshot)
            if not strategic_decision or strategic_decision.get('signal') == 'HOLD':
                logging.info("StrategicCortex mengembalikan sinyal HOLD. Tidak ada aksi yang diambil.")
                return

            # --- 3. Aksi: Menjalankan keputusan ---
            self.orchestrator.execution_system.process_signal(strategic_decision)
            
            logging.info("--- Siklus Kognitif Selesai ---\n")

        except Exception as e:
            logging.error(f"Kesalahan dalam siklus kognitif: {e}", exc_info=True)
            # Di sini bisa ditambahkan logika untuk self-healing atau notifikasi error

    def stop(self):
        """
        Menghentikan loop kognitif dengan aman.
        """
        logging.info("Menghentikan Cognitive Loop...")
        self.is_running = False
        # Bisa menambahkan logika shutdown untuk subsistem lain jika diperlukan

# --- CONTOH PENGGUNAAN (Untuk debugging) ---
if __name__ == '__main__':
    # Untuk debugging, Anda perlu mocking `orchestrator`
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    print("cognitive_loop.py v3 siap untuk diintegrasikan.")
