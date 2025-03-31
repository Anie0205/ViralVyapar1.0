import os
import requests
import json
import pandas as pd
from time import sleep

# ✅ API Constants
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
SERPER_URL = "https://google.serper.dev/search"
OUTPUT_FILE = "data/seo_data.csv"

def fetch_serper_results(query, num_results=10):
    """Fetches search results from Serper API."""
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "q": query,
        "num": num_results
    }
    
    try:
        response = requests.post(SERPER_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error: {response.status_code} for query: {query}")
            return None

    except Exception as e:
        print(f"❌ Exception while fetching results: {e}")
        return None


def extract_seo_data(query, results):
    """Extracts and structures SEO data from Serper API results."""
    seo_data = []

    if not results or "organic" not in results:
        print(f"❌ No results for {query}")
        return seo_data

    for result in results["organic"]:
        seo_data.append({
            "query": query,
            "title": result.get("title", "N/A"),
            "link": result.get("link", "N/A"),
            "snippet": result.get("snippet", "N/A"),
            "domain": result.get("domain", "N/A"),
            "displayed_link": result.get("displayedLink", "N/A"),
            "position": result.get("position", "N/A"),
            "date": result.get("date", "N/A")
        })
    
    return seo_data


def fetch_seo_data(queries, num_results=10):
    """Fetches SEO data for multiple queries and saves to CSV."""
    all_seo_data = []

    for query in queries:
        print(f"\n🔍 Fetching SEO data for: {query}...")
        
        results = fetch_serper_results(query, num_results)
        if results:
            seo_data = extract_seo_data(query, results)
            all_seo_data.extend(seo_data)
        
        # ✅ Sleep to avoid hitting rate limits
        sleep(2)

    if all_seo_data:
        # ✅ Convert to DataFrame and save to CSV
        df = pd.DataFrame(all_seo_data)
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n✅ SEO data saved to: {OUTPUT_FILE}")
    else:
        print("\n❌ No SEO data fetched.")


# ✅ Main Execution for testing
if __name__ == "__main__":
    queries = [
        "SEO strategies for health blogs",
        "how to rank health tips on Google",
        "top health-related keywords 2025",
        "SEO optimization for medical websites",
        "backlink strategies for healthcare sites"
    ]
    
    fetch_seo_data(queries)
