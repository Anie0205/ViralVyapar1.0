import json
import requests
import time
import os
from dotenv import load_dotenv
from time import sleep

# ✅ Load environment variables
load_dotenv()

# ✅ Constants
DOMAIN_FILE = "output/competitor_domains.json"
OUTPUT_FILE = "output/pagerank_scores.json"
OPENPAGERANK_API_KEY = os.getenv("OPENPAGERANK_API_KEY")

def analyze_pagerank(competitor_domains):
    """Analyze PageRank scores for competitor domains."""
    print("\n🔍 Analyzing PageRank scores...")
    
    # ✅ Load competitor domains if not provided
    if not competitor_domains:
        try:
            with open(DOMAIN_FILE, "r") as f:
                competitor_domains = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load competitor domains: {e}")
            return {}

    # ✅ Fetch PageRank data for each domain
    pagerank_data = {}
    for domain in competitor_domains:
        url = f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}"
        headers = {
            "API-OPR": OPENPAGERANK_API_KEY
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json().get("response", [])
                if data:
                    pagerank_data[domain] = {
                        "page_rank": data[0].get("page_rank", "N/A"),
                        "page_rank_decimal": data[0].get("page_rank_decimal", "N/A")
                    }
                    print(f"✅ Fetched PageRank for {domain}")
                else:
                    print(f"⚠️ No PageRank data found for {domain}")

            else:
                print(f"❌ Failed to fetch data for {domain}. Status: {response.status_code}")

        except Exception as e:
            print(f"❌ Error fetching PageRank for {domain}: {e}")

        sleep(1)  # Prevent hitting rate limits

    # ✅ Save the PageRank data
    with open(OUTPUT_FILE, "w") as f:
        json.dump(pagerank_data, f, indent=4)

    print(f"✅ PageRank scores saved to: {OUTPUT_FILE}")
    return pagerank_data

if __name__ == "__main__":
    # Test the PageRank analysis
    test_domains = ["example.com", "google.com"]
    results = analyze_pagerank(test_domains)
    print("\nPageRank Results:")
    for domain, data in results.items():
        print(f"{domain}: {data}")
