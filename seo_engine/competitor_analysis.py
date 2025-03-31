import json
import requests
import time
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Constants
OUTPUT_PATH = "output/competitor_analysis.json"
DOMAIN_OUTPUT = "output/competitor_domains.json"
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

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

# ✅ Extract root domain from URL
def extract_root_domain(url):
    try:
        domain = url.split("//")[-1].split("/")[0]  # Extract domain
        domain = domain.replace("www.", "")          # Remove www
        return domain
    except Exception as e:
        print(f"Error extracting domain: {e}")
        return None

# ✅ Competitor Queries
queries = [
    "e-commerce competitor analysis report",
    "e-commerce rival domains",
    "top online stores by traffic",
    "e-commerce market share 2025"
]

# ✅ Store Results
all_results = []
domains = set()

print("\n🔍 Analyzing competitors...")
for query in queries:
    print(f"\nFetching data for: {query}")
    results = fetch_competitor_data(query)

    for result in results:
        url = result.get("link")
        domain = extract_root_domain(url)
        if domain:
            domains.add(domain)

        all_results.append({
            "title": result.get("title", "N/A"),
            "url": url,
            "snippet": result.get("snippet", ""),
            "position": result.get("position", "N/A"),
            "domain": domain
        })
    
    time.sleep(1)  # Rate limit handling

# ✅ Save Competitor Analysis
with open(OUTPUT_PATH, "w") as f:
    json.dump(all_results, f, indent=4)

# ✅ Save Unique Domains for Backlink Analysis
with open(DOMAIN_OUTPUT, "w") as f:
    json.dump(list(domains), f, indent=4)

print(f"\n✅ Competitor analysis saved to: {OUTPUT_PATH}")
print(f"✅ Competitor domains saved to: {DOMAIN_OUTPUT}")
