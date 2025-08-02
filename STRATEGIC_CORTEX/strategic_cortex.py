# -*- coding: utf-8 -*-
# ==============================================================================
# == STRATEGIC CORTEX vFinal - PROJECT CHIMERA ==
# ==============================================================================
#
# Lokasi: STRATEGIC_CORTEX/strategic_cortex.py
# Deskripsi: Modul intelektual tingkat tinggi yang menganalisis data persepsi
#            dan membuat keputusan trading berdasarkan data on-chain, teknikal,
#            fundamental, dan sentimen. Menggunakan AI untuk sintesis.
#
# ==============================================================================

import logging
import sys
import os

# --- PENYESUAIAN PATH DINAMIS ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_script_dir) # Naik ke PROJECTCHIMERA/
sys.path.insert(0, project_root)
# --- AKHIR PENYESUAIAN PATH ---

class StrategicCortex:
    """
    Korteks Strategis: Menganalisis data kompleks dan membuat keputusan trading.
    Mengimplementasikan spesifikasi:
    - __init__ menginisialisasi LLMRouter dan DataSynthesizer.
    - analyze menerima perception_snapshot dan menghasilkan sinyal.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi StrategicCortex.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator untuk akses ke sistem lain.
        """
        logging.info("Inisialisasi StrategicCortex vFinal...")
        self.orchestrator = orchestrator
        logging.info("Menginisialisasi komponen AI...")

        try:
            # Inisialisasi instance dari LLMRouter dan DataSynthesizer dari modul AI_BRAIN
            # Sesuai dengan spesifikasi dari PINDAH PINDAH PINDAH.txt
            from AI_BRAIN.llm_router import LLMRouter
            from AI_BRAIN.data_synthesizer import DataSynthesizer
            self.llm_router = LLMRouter(self.orchestrator)
            self.synthesizer = DataSynthesizer(self.orchestrator)
            logging.info("LLMRouter dan DataSynthesizer berhasil diinisialisasi.")
        except Exception as e:
            logging.critical(f"Kesalahan saat menginisialisasi komponen AI_BRAIN: {e}", exc_info=True)
            raise # Hentikan inisialisasi jika komponen inti gagal

        logging.info("StrategicCortex vFinal berhasil diinisialisasi.")

    def analyze(self, perception_snapshot: dict):
        """
        Fungsi utama untuk menganalisis data persepsi dan menghasilkan sinyal trading.

        Args:
            perception_snapshot (dict): Data gabungan dari PerceptionSystem.
                Harus mengandung kunci seperti 'market_data', 'onchain', 'news'.

        Returns:
            dict: Sinyal trading akhir, misal {'signal': 'BULLISH', 'confidence': 0.8, ...}
                  atau {'signal': 'HOLD'} jika tidak ada kondisi yang memenuhi.
        """
        logging.info("Memulai analisis strategis di StrategicCortex...")
        
        # --- Validasi Input ---
        if not isinstance(perception_snapshot, dict):
            logging.error("Input perception_snapshot bukan dictionary.")
            return {'signal': 'HOLD', 'reason': 'Invalid perception_snapshot format'}

        # --- a. Menerima perception_snapshot ---
        # Data sudah diterima sebagai argumen
        
        # --- b. Mengambil data berita dari snapshot ---
        # Asumsikan data berita ada di bawah kunci 'news'
        # Berdasarkan struktur dari PerceptionSystem sebelumnya, ini bisa berupa dict atau list
        news_data_for_analysis = []
        
        raw_news_data = perception_snapshot.get('news', {})
        if isinstance(raw_news_data, dict):
            # Jika berupa dict (misalnya dari scraping), gabungkan semua nilai
            for source_news in raw_news_data.values():
                if isinstance(source_news, list):
                    news_data_for_analysis.extend(source_news)
        elif isinstance(raw_news_data, list):
            # Jika berupa list langsung
            news_data_for_analysis = raw_news_data
        else:
            logging.warning("Format data 'news' dalam perception_snapshot tidak dikenali.")
            news_data_for_analysis = []

        logging.debug(f"Berita yang dianalisis: {len(news_data_for_analysis)} item(s)")

        # --- f. Jika tidak ada berita, kembalikan sinyal 'HOLD' ---
        # (Catatan: Logika ini bisa diubah jika kita ingin analisis berdasarkan data lain)
        if not news_data_for_analysis:
            logging.info("Tidak ada berita baru. Mengembalikan sinyal HOLD berdasarkan kebijakan awal.")
            # Namun, kita bisa tetap melanjutkan untuk analisis berdasarkan data lain
            # Untuk sekarang, kita ikuti spesifikasi awal.
            # return {'signal': 'HOLD', 'reason': 'No news data available'}

        # --- c. Jika ada berita, kirim teks berita ke llm_router.get_council_analysis() ---
        all_council_reports = []
        for i, news_item in enumerate(news_data_for_analysis):
            if not isinstance(news_item, dict):
                logging.warning(f"Item berita ke-{i} bukan dictionary. Melewati.")
                continue

            title = news_item.get('title', 'No Title')
            description = news_item.get('description', '')
            full_text = f"{title}\n\n{description}".strip()

            if not full_text:
                logging.warning(f"Berita ke-{i} tidak memiliki teks. Melewati.")
                continue

            logging.info(f"Menganalisis berita: {title[:50]}...")
            try:
                # Meminta analisis dari dewan AI secara paralel
                # Ini adalah bagian utama dari integrasi AI
                council_report = self.llm_router.get_council_analysis(full_text)
                if council_report:
                    all_council_reports.append(council_report)
                    logging.debug(f"Laporan dewan untuk berita '{title[:30]}...': Diterima")
                else:
                    logging.warning(f"Tidak ada laporan dari dewan untuk berita '{title[:30]}...'")
            except Exception as e:
                logging.error(f"Kesalahan saat menganalisis berita '{title[:30]}...': {e}", exc_info=True)
                # Tidak menghentikan proses jika satu berita gagal

        # --- d. Jika ada laporan, sintesis menjadi sinyal akhir ---
        final_signal = {'signal': 'HOLD', 'confidence': 0.0, 'reason': 'No strong AI signal from news analysis.'}
        if all_council_reports:
            logging.info(f"Menyintesis {len(all_council_reports)} laporan dari dewan...")
            try:
                # Mengirim laporan ke synthesizer untuk menghasilkan sinyal trading akhir
                # Ini adalah bagian kedua dari integrasi AI
                synthesized_result = self.synthesizer.synthesize_council_reports(all_council_reports)
                if synthesized_result and isinstance(synthesized_result, dict):
                    final_signal = synthesized_result
                    logging.info(f"Sinyal akhir dihasilkan dari analisis berita: {final_signal}")
                else:
                    logging.warning("Synthesizer tidak menghasilkan sinyal yang valid dari berita.")
            except Exception as e:
                logging.error(f"Kesalahan saat menyintesis laporan berita: {e}", exc_info=True)
        else:
            logging.info("Tidak ada laporan dewan yang valid untuk disintesis dari berita.")

        # --- e. Mengembalikan sinyal trading akhir ---
        # Sinyal sudah disiapkan di variabel final_signal
        logging.info("Analisis strategis di StrategicCortex selesai.")
        return final_signal

# --- CONTOH PENGGUNAAN (Untuk debugging) ---
if __name__ == '__main__':
    # Konfigurasi logging dasar untuk debugging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Karena kelas ini membutuhkan orchestrator, kita tidak bisa menjalankannya secara mandiri
    # tanpa mocking atau instance sebenarnya. Ini hanya untuk memastikan tidak ada syntax error.
    print("strategic_cortex.py vFinal dimuat dengan sukses. Siap untuk diintegrasikan.")
