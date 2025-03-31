import json
import requests
import time
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Constants
DOMAIN_FILE = "output/competitor_domains.json"
OUTPUT_FILE = "output/openpagerank_analysis.json"
OPENPAGERANK_API_KEY = os.getenv("OPENPAGERANK_API_KEY")

# ✅ Load Competitor Domains
with open(DOMAIN_FILE, "r") as f:
    domains = json.load(f)

# ✅ OpenPageRank API
def fetch_openpagerank_data(domain):
    url = "https://openpagerank.com/api/v1.0/getPageRank"
    
    headers = {
        "API-OPR": OPENPAGERANK_API_KEY
    }

    params = {
        "domains[]": domain
    }

    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json().get("response", [])
        if data:
            return {
                "domain": domain,
                "page_rank": data[0].get("rank", "N/A"),
                "page_rank_decimal": data[0].get("rank_decimal", "N/A")
            }
    else:
        print(f"❌ Failed to fetch data for {domain}. Status: {response.status_code}")
        return {
            "domain": domain,
            "page_rank": "N/A",
            "page_rank_decimal": "N/A"
        }

# ✅ Fetch backlink metrics for each domain
backlink_metrics = []
print("\n🔍 Fetching backlink metrics...")
for domain in domains:
    print(f"Fetching data for {domain}...")
    metrics = fetch_openpagerank_data(domain)
    backlink_metrics.append(metrics)
    time.sleep(1)  # Rate limit handling

# ✅ Save Backlink Metrics
with open(OUTPUT_FILE, "w") as f:
    json.dump(backlink_metrics, f, indent=4)

print(f"\n✅ Backlink metrics saved to: {OUTPUT_FILE}")
