# -*- coding: utf-8 -*-
# ==============================================================================
# ==              WEB SCRAPER SOSIAL v2 - PROJECT CHIMERA                     ==
# ==============================================================================
#
# Lokasi: WEB_SCRAPERS/social_media_scraper.py
# Deskripsi: Versi dengan perbaikan koneksi proxy ScrapeOps.
#
# ==============================================================================

import requests
from bs4 import BeautifulSoup
import logging

class SocialMediaScraper:
    """
    Melakukan scraping data dari sumber web publik.
    """
    def __init__(self, orchestrator):
        logging.info("Inisialisasi Web Scraper v2...")
        self.orchestrator = orchestrator
        self.secrets = self.orchestrator.secrets
        self.scrapeops_key = self.secrets.get('tool_apis', {}).get('scrapeops_key')
        
        if not self.scrapeops_key:
            logging.warning("Kunci API ScrapeOps tidak ditemukan. Scraping akan dilakukan tanpa proksi.")
            self.proxy_url = None
        else:
            # --- PERBAIKAN KRUSIAL DI SINI ---
            # URL proxy yang benar menunjuk ke server ScrapeOps
            self.proxy_url = f'http://scrapeops.api_key={self.scrapeops_key}'
            logging.info("Scraper dikonfigurasi untuk menggunakan proksi ScrapeOps.")

    def scrape_coinmarketcap_trending(self):
        """
        Mengambil daftar 10 kripto yang sedang tren dari CoinMarketCap.
        """
        try:
            target_url = "https://coinmarketcap.com/trending-cryptocurrencies/"
            
            # Mengatur proksi jika tersedia
            proxies = {
               'http': self.proxy_url,
               'https': self.proxy_url,
            } if self.proxy_url else None

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            logging.info(f"Scraping CoinMarketCap Trending via {'Proxy' if proxies else 'Direct Connection'}...")
            # Menggunakan parameter `proxies` dari library requests
            response = requests.get(target_url, headers=headers, proxies=proxies, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            trending_coins = []
            table_body = soup.find('tbody')
            if not table_body:
                logging.warning("Tabel trending tidak ditemukan di CoinMarketCap.")
                return []

            rows = table_body.find_all('tr')
            for row in rows[:10]:
                coin_name_element = row.select_one('p.coin-item-symbol')
                if coin_name_element:
                    trending_coins.append(coin_name_element.text.strip())
            
            if not trending_coins:
                logging.warning("Tidak ada koin trending yang berhasil di-scrape dari CoinMarketCap.")
            else:
                logging.info(f"Kripto yang sedang tren: {trending_coins}")
            return trending_coins

        except Exception as e:
            logging.error(f"Gagal melakukan scraping CoinMarketCap: {e}")
            return []