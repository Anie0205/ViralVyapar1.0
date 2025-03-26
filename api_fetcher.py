import os
import requests
import pandas as pd
import random

API_KEY = os.getenv("SERPER_DEV_API_KEY")
API_URL = "https://google.serper.dev/search"
OUTPUT_DIR = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "seo_data.csv")

def fetch_seo_data(keywords):
    if not API_KEY:
        print("❌ SERPER_DEV_API_KEY is not set.")
        return

    data = []

    for keyword in keywords:
        print(f"🔍 Fetching data for: {keyword}")
        payload = {
            "q": keyword,
            "gl": "us",
            "hl": "en",
            "num": 10
        }
        headers = {
            "X-API-KEY": API_KEY,
            "Content-Type": "application/json"
        }

        response = requests.post(API_URL, json=payload, headers=headers)

        if response.status_code == 200:
            results = response.json().get("organic", [])

            for result in results:
                # Introduce more variation in difficulty and CTR scores
                data.append({
                    "keyword": keyword,
                    "title": result.get("title"),
                    "link": result.get("link"),
                    "snippet": result.get("snippet"),
                    "difficulty": random.randint(10, 90),   # More diverse difficulty values
                    "ctr": round(random.uniform(0.05, 0.85), 2)   # Random CTR between 5% and 85%
                })
        else:
            print(f"❌ Failed to fetch data: {response.status_code}")

    # Create the directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    df = pd.DataFrame(data)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Data saved to {OUTPUT_FILE}")

# Run the script
if __name__ == "__main__":
    keywords = [
        "best seo practices",
        "seo tools 2025",
        "keyword research tips",
        "backlink strategies",
        "content optimization"
    ]
    fetch_seo_data(keywords)
