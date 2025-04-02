import os
import json
import requests
from time import sleep
import google.generativeai as genai
from typing import List

# ✅ Load API keys from environment variables
OPENPAGERANK_API_KEY = os.getenv("OPENPAGERANK_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Added Gemini Key

# ✅ Configure Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-pro") # Or another suitable model
except Exception as e:
    print(f"❌ Failed to configure Gemini: {e}")
    gemini_model = None # Set to None if configuration fails

# ✅ File paths
competitor_domains_file = "output/competitor_domains.json"
backlink_output_file = "output/high_authority_backlinks.json"
# niche_file = "output/niche.txt" # Removed as niche is now an input

# --- REMOVED Hugging Face API Config ---
# GATED_MODEL = "Qwen/QwQ-32B"
# HF_API_URL = f"https://api-inference.huggingface.co/models/{GATED_MODEL}"
# HEADERS = {
#     "Authorization": f"Bearer {HF_API_KEY}",
#     "Content-Type": "application/json"
# }
# --- END REMOVED Hugging Face API Config ---

def filter_backlinks(competitor_domains, niche):
    """Filter and analyze backlinks for competitor domains based on the provided niche."""
    print(f"\n🔍 Filtering and analyzing backlinks for niche: {niche}...")
    
    # ✅ Load competitor domains if not provided
    if not competitor_domains:
        try:
            with open(competitor_domains_file, "r") as f:
                competitor_domains = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load competitor domains: {e}")
            return {}

    # ✅ Fetch backlinks only for relevant domains
    backlinks = fetch_backlinks(competitor_domains, niche)
    return backlinks

# ✅ Function to classify domains based on niche using LLM (Now Gemini - Batched)
def classify_domains_for_niche_batch(domains: List[str], niche: str) -> List[str]:
    """Uses Gemini LLM to check which domains in a batch are relevant to the given niche."""
    relevant_domains = []
    if not gemini_model:
        print("❌ Gemini model not configured. Skipping niche relevance check.")
        return domains # Default to all relevant if model isn't available
        
    if not domains:
        return []
        
    # Create a numbered list of domains for the prompt
    domain_list_str = "\n".join([f"{i+1}. {domain}" for i, domain in enumerate(domains)])
        
    prompt = f"Consider the niche: '{niche}'.\n\nWhich of the following domains are relevant to this niche?\n{domain_list_str}\n\nRespond *only* with a comma-separated list of the *numbers* corresponding to the relevant domains. Example: 1, 3, 7"

    print(f"\n🤖 Sending batch of {len(domains)} domains to Gemini for niche relevance check...")
    
    try:
        # Use Gemini API call
        response = gemini_model.generate_content(prompt)
        
        if response and hasattr(response, 'text'):
            response_text = response.text.strip()
            print(f"♊ Gemini Response: '{response_text}'")
            
            # Parse the comma-separated numbers
            try:
                relevant_indices = [int(num.strip()) - 1 for num in response_text.split(',') if num.strip().isdigit()]
                relevant_domains = [domains[i] for i in relevant_indices if 0 <= i < len(domains)]
                print(f"✅ Identified {len(relevant_domains)} relevant domains from batch.")
            except ValueError:
                print(f"⚠️ Could not parse Gemini response into numbers: '{response_text}'")
                # Fallback or alternative handling? For now, assume none are relevant on bad parse.
                relevant_domains = []
            except Exception as parse_e:
                 print(f"⚠️ Error parsing Gemini response: {parse_e}")
                 relevant_domains = []

        else:
            print(f"❌ Gemini validation failed for batch. Empty response.")
            # Fallback: Assume all are relevant to avoid losing data?
            relevant_domains = domains 
            print("⚠️ Assuming all domains in batch are relevant due to Gemini failure.")

    except Exception as e:
        print(f"❌ Gemini validation error for batch: {e}")
        # Fallback: Assume all are relevant?
        relevant_domains = domains
        print("⚠️ Assuming all domains in batch are relevant due to Gemini error.")
        
    return relevant_domains

# ✅ Function to fetch backlink metrics for relevant domains
def fetch_backlinks(domains, niche):
    """Fetches high-authority backlinks for domains relevant to a specific niche."""
    
    # Classify domains in a batch first
    relevant_domains = classify_domains_for_niche_batch(domains, niche)
    
    if not relevant_domains:
        print("🚫 No relevant domains identified by Gemini. Skipping backlink fetching.")
        return {}
        
    print(f"\n🔗 Fetching backlinks for {len(relevant_domains)} relevant domains identified by Gemini...")
    backlinks = {}

    # Only iterate through relevant domains
    for domain in relevant_domains:
        # --- LLM validation is already done via batch --- 
        # if not is_relevant_for_niche(domain, niche):
        #     print(f"🚫 Skipping irrelevant domain: {domain}")
        #     continue

        # --- Rest of the function remains the same (using OpenPageRank API) ---
        url = f"https://openpagerank.com/api/v1.0/getPageRank?domains[]={domain}"
        headers = {
            "API-OPR": OPENPAGERANK_API_KEY
        }

        try:
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json().get("response", [])
                domain_backlinks = []
                for item in data:
                    domain_backlinks.append({
                        "domain": item.get("domain"),
                        "page_rank": item.get("page_rank"),
                        "page_rank_decimal": item.get("page_rank_decimal", "N/A")
                    })
                backlinks[domain] = domain_backlinks
                print(f"✅ Fetched backlink metrics for {domain}")

            else:
                print(f"❌ Failed to fetch data for {domain}. Status: {response.status_code}")

        except Exception as e:
            print(f"❌ Error fetching backlinks for {domain}: {e}")

        sleep(1)  # Prevent hitting rate limits
        # --- End of unchanged part ---

    # ✅ Save the filtered backlinks
    with open(backlink_output_file, "w") as f:
        json.dump(backlinks, f, indent=4)

    print(f"✅ High-authority backlinks saved to: {backlink_output_file}")
    return backlinks

if __name__ == "__main__":
    # Example usage for testing - Load domains from file
    test_niche = "Education" # Provide a sample niche for testing
    
    # Check for API Key
    if not GEMINI_API_KEY:
        print("⚠️ GEMINI_API_KEY environment variable not set. Cannot run test.")
    else:
        # Load competitor domains from the JSON file
        try:
            with open(competitor_domains_file, "r") as f:
                test_domains = json.load(f)
            print(f"Loaded {len(test_domains)} domains from {competitor_domains_file} for testing.")
            if test_domains: # Proceed only if domains were loaded
                filter_backlinks(test_domains, test_niche)
            else:
                print("⚠️ No domains found in the file to test.")
        except FileNotFoundError:
            print(f"❌ Competitor domains file not found: {competitor_domains_file}. Cannot run test.")
        except Exception as e:
            print(f"❌ Error loading competitor domains file for testing: {e}")
