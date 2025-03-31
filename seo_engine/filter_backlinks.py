import os
import json
import requests
from time import sleep

# ✅ Load API keys from environment variables
OPENPAGERANK_API_KEY = os.getenv("OPENPAGERANK_API_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ✅ File paths
competitor_domains_file = "output/competitor_domains.json"
backlink_output_file = "output/high_authority_backlinks.json"

# ✅ Hugging Face API Config
GATED_MODEL = "Qwen/QwQ-32B"
HF_API_URL = f"https://api-inference.huggingface.co/models/{GATED_MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}


# ✅ Function to classify e-commerce competitors using LLM
def is_ecommerce(domain):
    """Uses Hugging Face LLM to classify if a domain is e-commerce or not."""
    prompt = f"Classify the following domain: {domain}. Is it an e-commerce platform? Answer only YES or NO."

    try:
        payload = {
            "inputs": prompt,
            "parameters": {"max_length": 20, "temperature": 0.2, "return_full_text": False}
        }

        response = requests.post(HF_API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            result = response.json()[0]['generated_text'].strip().lower()

            # ✅ Normalize the response for accuracy
            result_clean = result.strip(".,! ").lower()

            # ✅ Flexible check for "yes"
            if "yes" in result_clean:
                print(f"✅ {domain} classified as E-COMMERCE")
                return True
            else:
                print(f"🚫 {domain} classified as NON-E-COMMERCE")
                return False

        else:
            print(f"❌ LLM validation failed for {domain}. Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ LLM validation error for {domain}: {e}")
        return False


# ✅ Function to fetch backlink metrics
def fetch_backlinks(domains):
    """Fetches high-authority backlinks for e-commerce competitors."""
    backlinks = []

    for domain in domains:
        # ✅ LLM validation for e-commerce classification
        if not is_ecommerce(domain):
            print(f"🚫 Skipping non-e-commerce domain: {domain}")
            continue

        url = f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}"
        headers = {
            "API-OPR": OPENPAGERANK_API_KEY
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json().get("response", [])
                for item in data:
                    backlinks.append({
                        "domain": item.get("domain"),
                        "page_rank": item.get("page_rank"),
                        "page_rank_decimal": item.get("page_rank_decimal", "N/A")
                    })

                print(f"✅ Fetched backlink metrics for {domain}")

            else:
                print(f"❌ Failed to fetch data for {domain}. Status: {response.status_code}")

        except Exception as e:
            print(f"❌ Error fetching backlinks for {domain}: {e}")

        sleep(1)  # Prevent hitting rate limits

    # ✅ Save the filtered backlinks
    with open(backlink_output_file, "w") as f:
        json.dump(backlinks, f, indent=4)

    print(f"✅ High-authority backlinks saved to: {backlink_output_file}")


# ✅ Main Execution
def main():
    # ✅ Load competitor domains
    try:
        with open(competitor_domains_file, "r") as f:
            competitor_domains = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load competitor domains: {e}")
        return

    # ✅ Fetch backlinks only for e-commerce competitors
    fetch_backlinks(competitor_domains)


if __name__ == "__main__":
    main()
