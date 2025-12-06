import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
from pathlib import Path
import json
from utils.logger import logger
from utils.config import config


class WebScraper:
    
    def __init__(self, base_url: Optional[str] = None, delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: str, retries: int = 3) -> Optional[str]:
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                logger.info(f"Successfully fetched: {url}")
                time.sleep(self.delay)
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(self.delay * 2)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, 'html.parser')
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> List[str]:
        elements = soup.select(selector)
        return [element.get_text(strip=True) for element in elements]
    
    def extract_links(self, soup: BeautifulSoup, selector: str = 'a') -> List[str]:
        links = []
        for element in soup.select(selector):
            href = element.get('href')
            if href:
                if href.startswith('http'):
                    links.append(href)
                elif self.base_url:
                    links.append(self.base_url.rstrip('/') + '/' + href.lstrip('/'))
        return links
    
    def scrape_page(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, any]:
        html = self.fetch_page(url)
        if not html:
            return {}
        
        soup = self.parse_html(html)
        
        data = {'url': url}
        for key, selector in selectors.items():
            data[key] = self.extract_text(soup, selector)
        
        return data
    
    def scrape_multiple_pages(
        self,
        urls: List[str],
        selectors: Dict[str, str]
    ) -> List[Dict[str, any]]:
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"Scraping page {i}/{len(urls)}: {url}")
            data = self.scrape_page(url, selectors)
            if data:
                results.append(data)
        
        logger.info(f"Scraped {len(results)} pages successfully")
        return results
    
    def save_results(
        self,
        data: List[Dict[str, any]],
        filename: str = "scraped_data.json"
    ):
        output_path = config.RAW_DATA_DIR / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved scraped data to {output_path}")
