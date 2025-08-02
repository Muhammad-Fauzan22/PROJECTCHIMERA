# Lokasi: AGENTS/PERCEPTION_AGENT/perception_agent.py
import logging
from PERCEPTION_SYSTEM.platform_integrations.intelligence_aggregator import IntelligenceAggregator
from WEB_SCRAPERS.social_media_scraper import SocialMediaScraper
from GLOBAL_ANALYZER.ONCHAIN_INTELLIGENCE.onchain_collector import OnChainCollector

class PerceptionAgent:
    
    def __init__(self, orchestrator):
        logging.info("Menginisialisasi Perception Agent...")
        self.orchestrator = orchestrator
        self.intelligence_aggregator = IntelligenceAggregator(orchestrator)
        self.social_scraper = SocialMediaScraper(orchestrator)
        self.onchain_collector = OnChainCollector(orchestrator)
        logging.info(">>> Perception Agent siap beroperasi.")

    def run_perception_cycle(self):
        
        logging.info("Perception Agent memulai siklus pengumpulan data...")
        
        # Mengumpulkan data dari berbagai sumber secara paralel (konseptual)
        market_prices = self.intelligence_aggregator.get_all_market_prices()
        news_articles = self.intelligence_aggregator.get_latest_news()
        social_trends = self.social_scraper.scrape_coinmarketcap_trending()
        onchain_data = self.onchain_collector.collect_all_onchain_data()

        snapshot = {
            "market_data": market_prices,
            "news_data": news_articles,
            "social_data": {"trending_coins": social_trends},
            "onchain_data": onchain_data
        }
        
        logging.info("Snapshot persepsi berhasil dibuat.")
        return snapshot