import requests
import pandas as pd

class SEOScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://serpapi.com/search"

    def fetch_results(self, query: str, num_results: int = 10):
        """Fetches search results from Google using SerpAPI."""
        params = {
            "engine": "google",
            "q": query,
            "num": num_results,
            "api_key": self.api_key
        }

        response = requests.get(self.base_url, params=params)
        data = response.json()

        results = []
        for item in data.get("organic_results", []):
            results.append({
                "query": query,
                "position": item.get("position"),
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })

        return results

    def save_to_csv(self, data, filename="seo_scraped_data.csv"):
        """Saves scraped data to a CSV file."""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"✅ Data saved to {filename}")

# Example usage
if __name__ == "__main__":
    scraper = SEOScraper(api_key="your_serpapi_key")
    results = scraper.fetch_results("best smartphones", num_results=10)
    scraper.save_to_csv(results)
