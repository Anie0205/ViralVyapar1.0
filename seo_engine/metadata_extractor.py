import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# ✅ User-Agent to prevent blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

def extract_metadata(url):
    """Extracts metadata from a given URL."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return {"title": "N/A", "meta_description": "N/A", "h1_tags": [], "canonical": "N/A"}

        soup = BeautifulSoup(response.content, "html.parser")

        # ✅ Extract Metadata
        title = soup.title.text.strip() if soup.title else "N/A"

        # ✅ Extract Meta Description
        meta_desc = "N/A"
        meta_tag = soup.find("meta", attrs={"name": "description"})
        if meta_tag and "content" in meta_tag.attrs:
            meta_desc = meta_tag["content"]

        # ✅ Extract H1 Tags
        h1_tags = [h1.text.strip() for h1 in soup.find_all("h1")]

        # ✅ Extract Canonical URL
        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag["href"] if canonical_tag else "N/A"

        return {
            "title": title,
            "meta_description": meta_desc,
            "h1_tags": h1_tags,
            "canonical": canonical
        }

    except Exception as e:
        print(f"❌ Error fetching {url}: {str(e)}")
        return {"title": "N/A", "meta_description": "N/A", "h1_tags": [], "canonical": "N/A"}


def extract_metadata_from_csv(csv_path, output_path):
    """Extracts metadata for all URLs in the CSV file."""
    print("\n🔍 Extracting Metadata from URLs...")

    # ✅ Load CSV
    df = pd.read_csv(csv_path)

    if "link" not in df.columns:
        print("❌ No 'link' column found in the dataset.")
        return

    metadata = []
    for idx, row in df.iterrows():
        url = row['link']
        print(f"🌐 Extracting: {url}")
        meta = extract_metadata(url)
        meta["url"] = url
        metadata.append(meta)

        # ✅ Add delay to prevent being blocked
        time.sleep(1)

    # ✅ Convert to DataFrame
    metadata_df = pd.DataFrame(metadata)

    # ✅ Save metadata to CSV
    metadata_df.to_csv(output_path, index=False)
    print(f"\n✅ Metadata saved to {output_path}")


# ✅ Main Execution
if __name__ == "__main__":
    CSV_PATH = "data/seo_data.csv"                  # Input data
    OUTPUT_PATH = "output/seo_metadata.csv"         # Output metadata
    extract_metadata_from_csv(CSV_PATH, OUTPUT_PATH)
