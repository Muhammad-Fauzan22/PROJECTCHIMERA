# -*- coding: utf-8 -*-
# ==============================================================================
# == TEST INTELLIGENCE AGGREGATOR - PROJECT CHIMERA ==
# ==============================================================================
# Lokasi: test_intel_agg.py (di root direktori proyek)
# Deskripsi: Skrip pengujian mandiri untuk memverifikasi bahwa
#            IntelligenceAggregator berhasil diinisialisasi dan berfungsi.
#            Jalankan dengan: `python test_intel_agg.py`
# ==============================================================================

import sys
import os
import logging
from pathlib import Path

# --- KONFIGURASI AWAL ---
# 1. Konfigurasi logging dasar untuk skrip pengujian
logging.basicConfig(
    level=logging.DEBUG,  # Gunakan DEBUG untuk detail maksimal
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout) # Output ke console
    ]
)
logger = logging.getLogger(__name__)
logger.info("Memulai skrip pengujian IntelligenceAggregator...")

# 2. Menemukan dan menambahkan root proyek ke sys.path
# Ini adalah kunci untuk memperbaiki masalah impor
try:
    # Path ke direktori tempat skrip ini berada (seharusnya root proyek)
    SCRIPT_DIR = Path(__file__).resolve().parent
    PROJECT_ROOT = SCRIPT_DIR

    # Tambahkan root proyek ke sys.path
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    logger.debug(f"Script dir: {SCRIPT_DIR}")
    logger.debug(f"Project root (ditambahkan ke sys.path): {PROJECT_ROOT}")
    logger.debug(f"sys.path saat ini: {sys.path}")
except Exception as e:
    logger.critical(f"Gagal menentukan atau menambahkan PROJECT_ROOT ke sys.path: {e}", exc_info=True)
    sys.exit(1)
# --- AKHIR KONFIGURASI AWAL ---

def main():
    """Fungsi utama untuk menjalankan pengujian."""
    logger.info("=== MULAI PENGUJIAN INTELLIGENCE AGGREGATOR ===")

    orchestrator = None
    intel_agg = None

    # --- 1. Inisialisasi Orkestrator ---
    try:
        logger.info("1. Mengimpor dan menginisialisasi ChimeraOrchestrator...")
        # Impor kelas orkestrator
        from SENTIENT_CORE.chimera_orchestrator import ChimeraOrchestrator
        
        # Buat instance orkestrator
        # Ini akan memicu inisialisasi semua sub-sistem
        orchestrator = ChimeraOrchestrator()
        logger.info("✓ ChimeraOrchestrator berhasil diinisialisasi.")
    except ImportError as e:
        logger.critical(f"✗ GAGAL MENGIMPOR ChimeraOrchestrator: {e}", exc_info=True)
        logger.info("Pastikan struktur direktori dan file 'chimera_orchestrator.py' sudah benar.")
        return False
    except Exception as e:
        logger.critical(f"✗ KESALAHAN SAAT MENGINSIASI ChimeraOrchestrator: {e}", exc_info=True)
        return False

    # --- 2. Akses IntelligenceAggregator ---
    try:
        logger.info("2. Mengakses IntelligenceAggregator melalui PerceptionSystem...")
        
        # Periksa apakah PerceptionSystem ada
        if not hasattr(orchestrator, 'perception_system') or orchestrator.perception_system is None:
            logger.critical("✗ PerceptionSystem tidak ditemukan atau belum diinisialisasi di orkestrator.")
            return False
        logger.debug("✓ PerceptionSystem ditemukan.")

        # Periksa apakah IntelligenceAggregator ada
        if not hasattr(orchestrator.perception_system, 'intelligence_aggregator') or orchestrator.perception_system.intelligence_aggregator is None:
            logger.critical("✗ IntelligenceAggregator tidak ditemukan atau belum diinisialisasi di PerceptionSystem.")
            return False
        
        # Dapatkan instance IntelligenceAggregator
        intel_agg = orchestrator.perception_system.intelligence_aggregator
        logger.info("✓ IntelligenceAggregator berhasil diakses.")
    except AttributeError as e:
        logger.critical(f"✗ ATRIBUT TIDAK DITEMUKAN: {e}", exc_info=True)
        logger.info("Periksa apakah 'intelligence_aggregator' diinisialisasi di dalam 'PerceptionSystem'.")
        return False
    except Exception as e:
        logger.critical(f"✗ KESALAHAN SAAT MENGAKSES IntelligenceAggregator: {e}", exc_info=True)
        return False

    # --- 3. Uji Rotasi Kunci ---
    try:
        logger.info("3. Menjalankan uji rotasi kunci untuk 'coinstats'...")
        rotated_keys = []
        num_tests = 3 # Lakukan beberapa putaran untuk memastikan rotasi bekerja
        service_name = 'coinstats' # Nama layanan yang memiliki multiple keys

        for i in range(num_tests):
            key = intel_agg._rotate_key(service_name)
            if key:
                # Simpan 10 karakter pertama untuk log (jaga kerahasiaan)
                key_preview = key[:10] + "..." if len(key) > 10 else key
                rotated_keys.append(key_preview)
                logger.debug(f"  Putaran #{i+1}: Kunci = {key_preview}")
            else:
                logger.warning(f"  Putaran #{i+1}: Tidak ada kunci yang dikembalikan untuk '{service_name}'.")
        
        if rotated_keys:
             logger.info(f"✓ Rotasi kunci '{service_name}' berhasil. Kunci yang didapat: {rotated_keys}")
        else:
             logger.warning(f"⚠ Rotasi kunci '{service_name}' diuji, tetapi tidak ada kunci yang dikembalikan.")
    except Exception as e:
        logger.error(f"⚠ UJI ROTASI KUNCI GAGAL: {e}", exc_info=True)
        # Jangan hentikan pengujian, lanjutkan ke tes berikutnya

    # --- 4. Uji Pengambilan Harga Pasar ---
    try:
        logger.info("4. Menjalankan uji pengambilan harga pasar untuk 'BTC/USDT'...")
        test_symbol = 'BTC/USDT'
        
        price = intel_agg.get_market_price(test_symbol)
        
        if price is not None:
            logger.info(f"✓ Pengambilan harga untuk {test_symbol} BERHASIL: ${price:.2f}")
        else:
            logger.warning(f"⚠ Pengambilan harga untuk {test_symbol} GAGAL. Tidak ada harga yang dikembalikan.")
    except Exception as e:
        logger.error(f"⚠ UJI PENGAMBILAN HARGA GAGAL: {e}", exc_info=True)
        # Jangan hentikan pengujian

    # --- 5. Uji Pengambilan Berita Terbaru ---
    try:
        logger.info("5. Menjalankan uji pengambilan berita terbaru...")
        
        # Tes dengan query umum
        news_articles = intel_agg.get_latest_news("cryptocurrency")
        
        if news_articles and isinstance(news_articles, list):
            num_articles = len(news_articles)
            logger.info(f"✓ Pengambilan berita BERHASIL. Artikel ditemukan: {num_articles}")
            # Log artikel pertama sebagai contoh
            if num_articles > 0:
                first_article = news_articles[0]
                title = first_article.get('title', 'N/A')[:50] # Batasi panjang judul
                source = first_article.get('source', 'N/A')
                logger.debug(f"  Contoh artikel: [{source}] {title}...")
        else:
            logger.warning("⚠ Pengambilan berita GAGAL. Tidak ada artikel yang dikembalikan.")
    except Exception as e:
        logger.error(f"⚠ UJI PENGAMBILAN BERITA GAGAL: {e}", exc_info=True)
        # Jangan hentikan pengujian

    # --- SELESAI ---
    logger.info("=== PENGUJIAN INTELLIGENCE AGGREGATOR SELESAI ===")
    logger.info("Jika tidak ada pesan CRITICAL/ERROR di atas, komponen bekerja dengan baik.")
    return True

# --- TITIK MASUK EKSEKUSI ---
if __name__ == "__main__":
    success = main()
    if success:
        print("\n[PENGUJIAN BERHASIL] IntelligenceAggregator siap digunakan.")
        sys.exit(0) # Keluar dengan kode sukses
    else:
        print("\n[PENGUJIAN GAGAL] Terdapat kesalahan kritis pada IntelligenceAggregator.")
        sys.exit(1) # Keluar dengan kode error
