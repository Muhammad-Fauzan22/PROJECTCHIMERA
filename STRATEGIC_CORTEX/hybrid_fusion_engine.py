# -*- coding: utf-8 -*-
# ==============================================================================
# ==             MESIN FUSI HIBRIDA - PROJECT CHIMERA GENESIS                 ==
# ==============================================================================
#
# Lokasi: STRATEGIC_CORTEX/hybrid_fusion_engine.py
# Deskripsi: Modul ini adalah "otak" dari Chimera. Ia menerima data yang telah
#            diproses dari Perception System dan menerapkan berbagai model
#            analisis (teknikal, kuantitatif, AI) untuk menghasilkan sinyal
#            trading yang jelas (BUY, SELL, HOLD).
#
# ==============================================================================

# --- Import Library Standar ---
import logging

# --- Import Library Pihak Ketiga ---
import numpy as np

# Konfigurasi logging dasar untuk modul ini
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')


class HybridFusionEngine:
    """
    Kelas yang bertanggung jawab untuk menganalisis data pasar dan
    memutuskan tindakan trading berikutnya.
    """

    def __init__(self, orchestrator):
        """
        Konstruktor untuk HybridFusionEngine.

        Args:
            orchestrator (ChimeraOrchestrator): Instance dari orkestrator utama.
        """
        logging.info("Inisialisasi Hybrid Fusion Engine...")

        # Menyimpan referensi ke profil risiko. Di masa depan, ini akan digunakan
        # untuk menyesuaikan agresivitas strategi. Contoh: jika mendekati
        # max_daily_drawdown, mesin bisa memutuskan untuk tidak membuka posisi baru.
        self.risk_profile = orchestrator.risk_profile

        logging.info(">>> Hybrid Fusion Engine berhasil diinisialisasi.")


    def analyze_and_decide(self, processed_data: np.ndarray) -> dict:
        """
        Menganalisis data yang diproses dan menghasilkan sinyal trading.

        Args:
            processed_data (np.ndarray): Array data dari Perception System.

        Returns:
            dict: Sebuah dictionary yang berisi sinyal, tingkat kepercayaan,
                  dan alasan keputusan.
        """
        logging.info("Menganalisis data pasar untuk menghasilkan keputusan...")

        # --- Pemeriksaan Keamanan Data Input ---
        # Memastikan data cukup panjang untuk dianalisis. Ini mencegah IndexError.
        required_length = 5
        if len(processed_data) < required_length:
            logging.warning(f"Data tidak cukup panjang untuk dianalisis (membutuhkan {required_length}, tersedia {len(processed_data)}). Menghasilkan sinyal HOLD.")
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'reason': 'Data input tidak cukup untuk analisis.'
            }

        # --- Logika Strategi Sederhana: Detektor Momentum ---
        # Di masa depan, bagian ini akan digantikan oleh model yang lebih kompleks,
        # yang mungkin memadukan (fuse) output dari beberapa sub-strategi.

        last_value = processed_data[-1]
        prev_value = processed_data[-required_length]

        # Inisialisasi nilai default
        signal = 'HOLD'
        confidence = 0.5
        reason = "Tidak ada tren signifikan yang terdeteksi."

        # Membandingkan nilai untuk menentukan tren jangka pendek
        if last_value > prev_value:
            signal = 'BUY'
            confidence = 0.75
            reason = f"Tren naik terdeteksi dalam {required_length} bar terakhir."
        elif last_value < prev_value:
            signal = 'SELL'
            confidence = 0.75
            reason = f"Tren turun terdeteksi dalam {required_length} bar terakhir."

        logging.info(f"Keputusan Dihasilkan: SINYAL={signal}, KEPERCAYAAN={confidence:.2f}, ALASAN='{reason}'")

        # Mengembalikan hasil dalam format dictionary yang terstruktur
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason
        }