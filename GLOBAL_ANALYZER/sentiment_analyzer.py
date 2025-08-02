# -*- coding: utf-8 -*-
# ==============================================================================
# ==                ANALISIS SENTIMEN v2 - PROJECT CHIMERA                    ==
# ==============================================================================
#
# Lokasi: GLOBAL_ANALYZER/sentiment_analyzer.py
# Deskripsi: Menggunakan armada model AI untuk menganalisis sentimen berita
#            secara cerdas dan efisien.
#
# ==============================================================================

import logging
from AI_BRAIN.llm_router import LLMRouter
from AI_BRAIN.model_wrappers.gemini_wrapper import GeminiWrapper
from AI_BRAIN.model_wrappers.openrouter_wrapper import OpenRouterWrapper

class SentimentAnalyzer:
    """
    Menganalisis sentimen berita menggunakan armada model AI yang dikelola oleh LLMRouter.
    """
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.llm_router = LLMRouter(self.orchestrator)

    def analyze_article_sentiment(self, article_text: str):
        """
        Menganalisis sentimen satu artikel berita.
        """
        try:
            # 1. Pilih model AI terbaik untuk tugas ini
            model_name, api_key = self.llm_router.select_model("fast_sentiment_analysis")

            # 2. Buat prompt yang dioptimalkan
            prompt = f"""
            As a senior financial analyst specializing in cryptocurrency, analyze the sentiment of the following news article.
            Your analysis must focus on the potential impact on the crypto market, specifically Bitcoin and Ethereum.
            Provide your output ONLY in a valid JSON format with the following three keys:
            1. "sentiment": A string, must be one of 'BULLISH', 'BEARISH', or 'NEUTRAL'.
            2. "confidence": A float between 0.0 and 1.0, representing your certainty.
            3. "summary": A concise, one-sentence summary explaining the key takeaway for a trader.

            Article Text (first 2000 characters):
            ---
            {article_text[:2000]}
            ---
            """

            # 3. Inisialisasi wrapper yang sesuai dan panggil
            wrapper = None
            if model_name == "google":
                wrapper = GeminiWrapper(api_key)
            else:
                # Asumsikan semua model lain diakses via OpenRouter
                wrapper = OpenRouterWrapper(api_key, model_name)
            
            if wrapper:
                result = wrapper.generate(prompt)
            else:
                raise ValueError("Wrapper model tidak dapat diinisialisasi.")

            if result and all(k in result for k in ['sentiment', 'confidence', 'summary']):
                logging.info(f"Analisis sentimen selesai menggunakan model {model_name}: {result}")
                return result
            else:
                logging.warning(f"Hasil analisis dari {model_name} tidak valid atau kosong.")
                return None

        except Exception as e:
            logging.error(f"Gagal menganalisis sentimen: {e}", exc_info=True)
            return None