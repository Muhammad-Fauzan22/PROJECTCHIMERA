# -*- coding: utf-8 -*-
# ==============================================================================
# == BLACK SWAN SHIELD - PROJECT CHIMERA ==
# ==============================================================================
# Lokasi: AGENTS/ALPHA_AGENT/black_swan_shield.py
# Deskripsi: Modul ini bertindak sebagai sistem peringatan dini dan respon otomatis
#            terhadap kondisi pasar ekstrem (Black Swan Events).
# ==============================================================================

import logging
import sys
import os

# --- PENYESUAIAN PATH DINAMIS UNTUK MENGATASI MASALAH IMPOR ---
# Mendapatkan path absolut dari direktori script ini
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# Naik dua level untuk mendapatkan direktori root proyek (PROJECTCHIMERA)
# AGENTS/ALPHA_AGENT/ -> PROJECTCHIMERA/
project_root = os.path.dirname(os.path.dirname(current_script_dir))
# Menambahkan direktori root ke sys.path agar modul-modul bisa diimpor
sys.path.insert(0, project_root)
# --- AKHIR PENYESUAIAN PATH ---

# Impor modul lain dari proyek jika diperlukan di masa depan
# Untuk saat ini, tidak ada impor spesifik yang diperlukan dari proyek

class BlackSwanShield:
    """
    Agen yang memantau kondisi pasar untuk mendeteksi potensi Black Swan
    dan memicu tindakan perlindungan otomatis.
    """

    def __init__(self, orchestrator):
        """
        Inisialisasi BlackSwanShield.

        Args:
            orchestrator: Instance dari ChimeraOrchestrator untuk akses ke sistem lain
                          atau konfigurasi jika diperlukan.
        """
        self.orchestrator = orchestrator
        logging.info("BlackSwanShield diinisialisasi.")

    def scan_for_threats(self, perception_snapshot: dict):
        """
        Menganalisis snapshot persepsi untuk mendeteksi kondisi Black Swan.

        Args:
            perception_snapshot (dict): Data gabungan dari PerceptionSystem.
                Diharapkan berisi kunci seperti 'market_data', 'news', 'onchain'.

        Returns:
            dict or None: Perintah darurat jika ancaman terdeteksi, None jika tidak.
                Contoh: {
                    'emergency': True,
                    'action': 'REDUCE_LEVERAGE',
                    'level': 1,
                    'reason': 'Volatilitas ekstrem terdeteksi...'
                }
        """
        if not isinstance(perception_snapshot, dict):
            logging.warning("Input perception_snapshot tidak valid.")
            return None

        threat_count = 0
        reasons = []

        # --- Kondisi 1: Volatilitas Ekstrem ---
        # Asumsi: Data volatilitas ada di perception_snapshot['market_data']['volatility_24h']
        # atau bisa dihitung dari high/low. Kita gunakan placeholder untuk saat ini.
        market_data = perception_snapshot.get('market_data', {})
        # Contoh logika sederhana: jika perubahan harga 24h > 15%
        price_change_24h = market_data.get('price_change_percentage_24h', 0)
        # Untuk BTC, ambil dari data jika tersedia
        btc_data = market_data.get('BTC/USDT', {})
        if btc_data:
            price_change_24h = btc_data.get('percentage_change_24h', price_change_24h)
        
        # Threshold bisa dibuat konfigurasi
        volatility_threshold = 10.0 # 10% dalam 24 jam
        if abs(price_change_24h) > volatility_threshold:
            threat_count += 1
            direction = "naik" if price_change_24h > 0 else "turun"
            reasons.append(f"Volatilitas ekstrem: BTC {direction} {abs(price_change_24h):.2f}% dalam 24 jam.")
            logging.warning(f"Kondisi 1 terpenuhi: {reasons[-1]}")

        # --- Kondisi 2: Sentimen Negatif Massif ---
        # Asumsi: Data sentimen ada di perception_snapshot['news']['aggregate_sentiment']
        # atau bisa dihitung dari analisis berita. Kita gunakan placeholder.
        news_data = perception_snapshot.get('news', {})
        # Misalnya, kita hitung rata-rata sentimen dari berita terbaru
        sentiment_scores = [item.get('sentiment_score', 0) for item in news_data if isinstance(item, dict)]
        if sentiment_scores:
             avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
             # Threshold untuk sentimen negatif massif
             negative_sentiment_threshold = -0.5
             if avg_sentiment < negative_sentiment_threshold:
                 threat_count += 1
                 reasons.append(f"Sentimen negatif massif: Rata-rata sentimen {avg_sentiment:.2f}.")
                 logging.warning(f"Kondisi 2 terpenuhi: {reasons[-1]}")

        # --- Kondisi 3: Pergerakan On-Chain Mendadak ---
        # Asumsi: Data on-chain ada di perception_snapshot['onchain']
        # Contoh: Netflow exchange meningkat drastis (banyak koin masuk ke exchange)
        onchain_data = perception_snapshot.get('onchain', {})
        # Placeholder untuk logika on-chain
        # Misalnya, jika netflow exchange meningkat > 50% dari rata-rata
        # netflow_change = onchain_data.get('exchange_netflow_change_percent', 0)
        # if netflow_change > 50:
        #     threat_count += 1
        #     reasons.append(f"Netflow exchange meningkat drastis: +{netflow_change}%.")
        #     logging.warning(f"Kondisi 3 terpenuhi: {reasons[-1]}")
        
        # Untuk demonstrasi, kita bisa membuat kondisi 3 terpenuhi berdasarkan kata kunci di berita
        # atau jika tidak ada data on-chain yang spesifik.
        critical_keywords = ["krisis", "crash", "collapse", "regulasi ketat", "larangan"]
        critical_news_found = any(
            any(keyword in (item.get('title', '') + ' ' + item.get('description', '')) 
                for keyword in critical_keywords)
            for item in news_data if isinstance(item, dict)
        )
        if critical_news_found:
            threat_count += 1
            reasons.append("Berita kritis terdeteksi di feed.")
            logging.warning(f"Kondisi 3 terpenuhi (berbasis berita): {reasons[-1]}")


        # --- Evaluasi Ancaman ---
        # Jika 2 dari 3 kondisi terpenuhi, picu darurat
        if threat_count >= 2:
            # Tentukan level berdasarkan jumlah ancaman
            level = min(threat_count, 3) # Maksimal level 3
            action = "REDUCE_LEVERAGE" # Aksi default untuk level 1 & 2
            if level == 3:
                action = "CLOSE_POSITIONS" # Aksi ekstrem untuk level 3
            
            emergency_command = {
                'emergency': True,
                'action': action,
                'level': level,
                'reason': " & ".join(reasons),
                'timestamp': perception_snapshot.get('timestamp') # Jika ada
            }
            logging.critical(f"Ancaman Black Swan terdeteksi (Level {level}): {emergency_command['reason']}")
            return emergency_command
        else:
            logging.info(f"Tidak ada ancaman Black Swan terdeteksi. Kondisi terpenuhi: {threat_count}/3.")
            return None

# --- CONTOH PENGGUNAAN (Untuk debugging) ---
if __name__ == '__main__':
    # Konfigurasi logging dasar untuk debugging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Karena kelas ini membutuhkan orchestrator, kita tidak bisa menjalankannya secara mandiri
    # tanpa mocking atau instance sebenarnya. Ini hanya untuk memastikan tidak ada syntax error.
    print("black_swan_shield.py dimuat dengan sukses. Siap untuk diintegrasikan.")
