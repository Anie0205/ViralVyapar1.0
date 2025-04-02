import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
import time
from typing import List, Dict
import os

class SEOScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def load_competitor_domains(self) -> List[str]:
        """Load competitor domains from JSON file."""
        try:
            with open('output/competitor_domains.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Error loading competitor domains: {e}")
            return []

    def scrape_page(self, url: str) -> Dict:
        """Scrape a single page for SEO data."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract meta tags
            meta_tags = {}
            for tag in soup.find_all('meta'):
                name = tag.get('name', tag.get('property', ''))
                content = tag.get('content', '')
                if name and content:
                    meta_tags[name] = content

            # Extract schema data
            schema_data = []
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    schema_data.append(json.loads(script.string))
                except:
                    continue

            # Extract main content
            main_content = ''
            for tag in ['article', 'main', 'div']:
                content = soup.find(tag, class_=['content', 'post', 'article'])
                if content:
                    main_content = content.get_text(strip=True)
                    break

            return {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'meta_tags': meta_tags,
                'schema_data': schema_data,
                'main_content': main_content,
                'h1_tags': [h1.get_text() for h1 in soup.find_all('h1')],
                'h2_tags': [h2.get_text() for h2 in soup.find_all('h2')],
                'images': [img.get('alt', '') for img in soup.find_all('img') if img.get('alt')]
            }
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None

    def scrape_competitors(self):
        """Scrape all competitor domains."""
        domains = self.load_competitor_domains()
        scraped_data = []

        for domain in domains:
            print(f"\n🔍 Scraping: {domain}")
            
            # Add protocol if missing
            if not domain.startswith(('http://', 'https://')):
                domain = 'https://' + domain

            data = self.scrape_page(domain)
            if data:
                scraped_data.append(data)
            
            # Rate limiting
            time.sleep(2)

        # Save raw scraped data
        self.save_raw_data(scraped_data)
        return scraped_data

    def save_raw_data(self, data: List[Dict]):
        """Save raw scraped data to JSON file."""
        try:
            os.makedirs('output', exist_ok=True)
            with open('output/scraped_seo_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✅ Raw scraped data saved to output/scraped_seo_data.json")
        except Exception as e:
            print(f"❌ Error saving scraped data: {e}")

if __name__ == "__main__":
    scraper = SEOScraper()
    scraper.scrape_competitors()
