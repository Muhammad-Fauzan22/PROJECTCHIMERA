# -*- coding: utf-8 -*-
# ==============================================================================
# ==        DATA SYNTHESIZER v2 (Council Report) - PROJECT CHIMERA          ==
# ==============================================================================
#
# Lokasi: AI_BRAIN/data_synthesizer.py
# Deskripsi: Mensintesis laporan intelijen terstruktur dari berbagai anggota
#            Dewan AI menjadi satu sinyal trading akhir yang komprehensif.
#
# ==============================================================================

import logging
from collections import Counter

class DataSynthesizer:
    """
    Menggabungkan analisis dari berbagai model AI menjadi satu
    sinyal trading yang koheren dan bisa ditindaklanjutkan.
    """
    def __init__(self, orchestrator):
        """
        Inisialisasi Synthesizer.
        """
        logging.info("Menginisialisasi Data Synthesizer v2...")
        self.orchestrator = orchestrator
        # Bobot kepercayaan untuk setiap analis AI di dewan
        self.analyst_weights = {
            "macro_fundamental": 0.35,      # Gemini (gambaran besar)
            "risk_scenario": 0.25,          # Claude (fokus risiko)
            "sentiment_psychology": 0.20,   # GPT-4o (sentimen real-time)
            "execution_strategy": 0.20      # DeepSeek (peluang taktis)
        }

    def synthesize_council_reports(self, council_reports: dict):
        """
        Menganalisis laporan dari dewan AI dan menghasilkan sinyal akhir.
        """
        if not council_reports:
            return None

        valid_reports = [report for report in council_reports.values() if self._is_report_valid(report)]
        if not valid_reports:
            logging.warning("Tidak ada laporan valid dari Dewan AI untuk disintesis.")
            return None

        # --- LANGKAH 1: SINTESIS SENTIMEN KESELURUHAN ---
        sentiment_scores = {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0}
        total_confidence = 0

        for task_name, report in council_reports.items():
            if self._is_report_valid(report):
                sentiment = report.get('Overall Market Sentiment', 'NEUTRAL').upper()
                confidence = report.get('confidence', 0.5) # Default confidence jika tidak ada
                weight = self.analyst_weights.get(task_name, 0.1)
                
                if sentiment in sentiment_scores:
                    sentiment_scores[sentiment] += confidence * weight
                    total_confidence += confidence * weight
        
        if total_confidence == 0:
            final_sentiment = 'NEUTRAL'
            final_confidence = 0.0
        else:
            # Normalisasi skor untuk mendapatkan sinyal dan confidence akhir
            final_sentiment = max(sentiment_scores, key=sentiment_scores.get)
            final_confidence = sentiment_scores[final_sentiment] / total_confidence

        # --- LANGKAH 2: AGREGASI ENTITAS (ASET, RISIKO, PELUANG) ---
        top_cryptos = self._aggregate_lists(valid_reports, 'Top Performing Cryptos')
        caution_cryptos = self._aggregate_lists(valid_reports, 'Cryptos to Watch Cautiously')
        market_risks = self._aggregate_lists(valid_reports, 'Market Risks')
        opportunities = self._aggregate_lists(valid_reports, 'Opportunities')

        # --- LANGKAH 3: KONSTRUKSI SINYAL FINAL YANG KAYA DATA ---
        final_signal = {
            'signal': final_sentiment,
            'confidence': round(final_confidence, 4),
            'recommended_long': top_cryptos,
            'recommended_short': caution_cryptos,
            'summary_risks': market_risks,
            'summary_opportunities': opportunities,
            'reason': f"AI Council consensus. Sentiment: {final_sentiment} ({final_confidence:.2%}). Top long candidate: {top_cryptos[0] if top_cryptos else 'N/A'}."
        }
        
        logging.info(f"Sintesis Dewan AI selesai. Sinyal akhir: {final_signal}")
        return final_signal

    def _is_report_valid(self, report: dict):
        """Memeriksa apakah laporan dari AI memiliki format dasar yang benar."""
        return isinstance(report, dict) and 'Overall Market Sentiment' in report

    def _aggregate_lists(self, reports: list, key: str):
        """Mengumpulkan item dari list di semua laporan dan mengurutkannya berdasarkan frekuensi."""
        all_items = []
        for report in reports:
            items = report.get(key, [])
            if isinstance(items, list):
                all_items.extend([item.strip() for item in items])
        
        # Menghitung frekuensi setiap item dan mengurutkannya
        if not all_items:
            return []
        return [item for item, count in Counter(all_items).most_common()]