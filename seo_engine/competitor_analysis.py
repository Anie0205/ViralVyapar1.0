import json
import requests
import time
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Constants
DOMAIN_OUTPUT = "output/competitor_domains.json"
SEO_ANALYSIS_FILE = "output/seo_analysis.json"
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
NICHE_OUTPUT_FILE = "output/niche.txt"  # File to save the detected niche

def analyze_competitors(queries):
    """Analyze competitors based on the provided queries."""
    print(f"\n🔍 Analyzing competitors based on generated queries...")
    
    # ✅ Extract root domain from URL
    def extract_root_domain(url):
        try:
            domain = url.split("//")[-1].split("/")[0]  # Extract domain
            domain = domain.replace("www.", "")          # Remove www
            return domain
        except Exception as e:
            print(f"Error extracting domain: {e}")
            return None

    # ✅ SERPER API Request
    def fetch_competitor_data(query):
        url = "https://google.serper.dev/search"
        
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }

        payload = {
            "q": query,
            "num": 10
        }

        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"❌ Failed to fetch data for {query}. Status: {response.status_code}")
            return []
        
        data = response.json()
        return data.get("organic", [])

    # ✅ Store Results
    domains = set()

    # ✅ Fetch and save competitor data for each query
    for query in queries:
        print(f"\nFetching data for: {query}")
        results = fetch_competitor_data(query)

        for result in results:
            url = result.get("link")
            competitor_domain = extract_root_domain(url)
            # Simple check to avoid adding the primary domain itself if it appears
            # A more robust check might involve comparing against the initial domain passed to main.py
            if competitor_domain: # Ensure we have a valid domain
                domains.add(competitor_domain) 

        time.sleep(1)  # Rate limit handling

    # ✅ Save Unique Domains for Backlink Analysis
    with open(DOMAIN_OUTPUT, "w") as f:
        json.dump(list(domains), f, indent=4)

    print(f"\n✅ Found {len(domains)} unique competitor domains")
    print(f"✅ Competitor domains saved to: {DOMAIN_OUTPUT}")

    return list(domains)

if __name__ == "__main__":
    # Test the function with sample queries
    test_queries = [
        "best seo tools 2025",
        "ai content generation for websites",
        "competitor analysis techniques"
    ]
    analyze_competitors(test_queries)
