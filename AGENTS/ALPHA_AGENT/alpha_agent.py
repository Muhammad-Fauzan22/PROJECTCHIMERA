# -*- coding: utf-8 -*-
# ==============================================================================
# ==        ALPHA AGENT v2 (RAG Integrated - FINAL) - PROJECT CHIMERA         ==
# ==============================================================================
#
# Lokasi: AGENTS/ALPHA_AGENT/alpha_agent.py
# Deskripsi: Versi final yang mengintegrasikan Memori Vektor (RAG) dengan
#            sintaks yang sudah diperbaiki dan terverifikasi sepenuhnya.
#
# ==============================================================================

import logging

# Mengimpor komponen dari 'otak kognitif' AI_BRAIN dan Memori Kolektif
from AI_BRAIN.llm_router import LLMRouter
from AI_BRAIN.data_synthesizer import DataSynthesizer
from COLLECTIVE_MEMORY.vector_store import VectorStore

class AlphaAgent:
    """
    Agen yang menganalisis data menggunakan Dewan AI dan Memori Vektor.
    """
    def __init__(self, orchestrator):
        """
        Inisialisasi semua sub-komponen analitis.
        """
        logging.info("Menginisialisasi Alpha Agent (RAG Integrated)...")
        self.orchestrator = orchestrator
        
        self.llm_router = LLMRouter(orchestrator)
        self.synthesizer = DataSynthesizer(orchestrator)
        self.vector_store = VectorStore(orchestrator)
        
        logging.info(">>> Alpha Agent siap menganalisis dengan memori jangka panjang.")

    def generate_signal(self, perception_snapshot: dict):
        """
        Menganalisis snapshot, memperbarui memori, dan menghasilkan sinyal.
        """
        logging.info("Alpha Agent memulai siklus analisis RAG...")
        
        if not perception_snapshot:
            return self._generate_hold_signal('No perception data.')

        # --- LANGKAH 1: PERBARUI MEMORI JANGKA PANJANG ---
        news_articles = perception_snapshot.get("news_data", [])
        if not news_articles:
            return self._generate_hold_signal('No news data to analyze.')

        for article in news_articles:
            doc_id = article.get('url') or article.get('title', '')
            if not doc_id:
                continue

            article_text = article.get('title', '') + " " + article.get('description', '')
            source_name = article.get('source', {}).get('name', 'Unknown')
            
            self.vector_store.add_document(
                text=article_text,
                metadata={'source': source_name},
                doc_id=doc_id
            )

        # --- LANGKAH 2: BUAT PERTANYAAN & AMBIL KONTEKS ---
        query = "Based on the latest news and market data, what is the overall sentiment and short-term prediction for all major cryptocurrencies listed on Binance?"
        context_documents = self.vector_store.query(query, n_results=10)
        
        if not context_documents:
            return self._generate_hold_signal('No relevant context documents found.')

        context_text = "\n".join(context_documents)

        # --- LANGKAH 3: ANALISIS DENGAN DEWAN AI ---
        prompt_for_council = f"""
Context: {context_text}

Instructions:
Based on the provided context and your expert knowledge, analyze the overall sentiment and short-term prediction for ALL major cryptocurrencies listed on Binance. Do not limit your analysis to just BTC/USDT and ETH/USDT - analyze the entire crypto market landscape.

Please provide a comprehensive analysis including:
1. Overall market sentiment analysis based on recent news
2. Key market trends affecting the entire cryptocurrency ecosystem
3. Short-term price predictions for major cryptocurrencies with confidence levels
4. Any significant risks or opportunities to consider across the market
5. Sector-specific insights (DeFi, NFTs, Layer 1/2 protocols, etc.)

Output Format:
- Overall Market Sentiment: [Positive/Negative/Neutral]
- Top Performing Cryptos (Short-term): [List with brief rationale]
- Cryptos to Watch Cautiously: [List with brief rationale]
- Market Risks: [List of potential risks]
- Opportunities: [Key opportunities across different sectors]
"""

        logging.debug("Mengirim prompt RAG ke Dewan AI...")
        council_reports = self.llm_router.get_council_analysis(prompt_for_council)
        
        # --- LANGKAH 4: SINTESIS & HASIL AKHIR ---
        final_signal = self.synthesizer.synthesize_council_reports(council_reports)
        
        if not final_signal:
            return self._generate_hold_signal('AI Council synthesis failed.')

        logging.info(f"Alpha Agent (RAG) berhasil menghasilkan sinyal: {final_signal}")
        return final_signal

    def _generate_hold_signal(self, reason: str):
        """
        Fungsi bantuan untuk menghasilkan sinyal HOLD yang konsisten.
        """
        logging.info(f"{reason} Menghasilkan sinyal HOLD.")
        return {'signal': 'HOLD', 'confidence': 0.0, 'reason': reason}