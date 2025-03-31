import os
import json
import requests
import time
import re

# ✅ Load API Keys
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ✅ API Endpoints
SERPER_API_URL = "https://google.serper.dev/search"
QWEN_MODEL = "Qwen/QwQ-32B"
QWEN_API_URL = f"https://api-inference.huggingface.co/models/{QWEN_MODEL}"

# ✅ Fetch Results from Serper API
def fetch_serper_results(domain, retries=3, backoff=2):
    """Fetch organic results from Serper API"""
    queries = set()

    prompts = [
        f"{domain}",
        f"{domain} trends 2025",
        f"{domain} competitors",
        f"{domain} reviews"
    ]

    for prompt in prompts:
        for attempt in range(retries):
            try:
                payload = {
                    "q": prompt,
                    "num": 5  # Fetch top 5 results per query
                }
                headers = {
                    "X-API-KEY": SERPER_API_KEY,
                    "Content-Type": "application/json"
                }

                response = requests.post(SERPER_API_URL, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()

                    # ✅ Extracting titles and snippets
                    for item in data.get("organic", []):
                        title = item.get("title", "").strip()
                        snippet = item.get("snippet", "").strip()

                        query = f"{title} - {snippet}"
                        query = re.sub(r'\s+', ' ', query).strip()

                        if len(query) > 5:
                            queries.add(query)

                    break  # Move to the next prompt after success
                else:
                    print(f"❌ Error: {response.status_code} (Attempt {attempt + 1}/{retries})")

            except Exception as e:
                print(f"⚠️ Exception: {e} (Attempt {attempt + 1}/{retries})")

            time.sleep(backoff ** attempt)

    return list(queries)


# ✅ Generate Queries using Qwen API
def generate_queries_with_qwen(domain, serper_results):
    """Generate relevant search queries using Qwen"""

    # ✅ Prepare the Qwen prompt
    prompt = f"""
You are an SEO expert. Based on the domain "{domain}" and the following search results:

{json.dumps(serper_results, indent=2)}

Generate 10 realistic and natural search queries that potential visitors might use to find content related to this domain. 
- The queries should be diverse, clear, and natural language.
- Return the queries as a numbered list.
"""

    headers = {
        "Authorization": f"Bearer {HF_API_KEY}",
        "Content-Type": "application/json"
    }

    # ✅ Qwen generation parameters
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 400,
            "temperature": 0.5,
            "top_p": 0.9,
            "do_sample": True
        }
    }

    response = requests.post(QWEN_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            data = response.json()

            # ✅ Handle both list and dict formats
            raw_output = None
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                raw_output = data[0]["generated_text"]
            elif isinstance(data, dict) and "generated_text" in data:
                raw_output = data["generated_text"]

            if raw_output:
                # ✅ Extract queries from the output
                queries = extract_queries_from_output(raw_output)

                if queries:
                    return clean_and_deduplicate_queries(queries)
                else:
                    print("\n❌ No valid queries extracted.")
                    return []

            else:
                print("\n❌ Invalid Qwen response format.")
                return []

        except Exception as e:
            print(f"\n❌ Exception while parsing Qwen response: {e}")
            return []
    else:
        print(f"\n❌ Qwen Error: {response.status_code}")
        print(response.text)
        return []


# ✅ Extract Queries from Raw Output
def extract_queries_from_output(output):
    """Extract valid queries from Qwen raw output"""
    queries = []

    # ✅ Extract numbered queries
    numbered_queries = re.findall(r'\d+\.\s(.+)', output)

    if numbered_queries:
        queries.extend(numbered_queries)

    # ✅ Handle non-numbered format fallback
    if not queries:
        queries = output.split("\n")
        queries = [q.strip() for q in queries if len(q.strip()) > 5]

    return queries


# ✅ Clean and De-duplicate Queries
def clean_and_deduplicate_queries(queries):
    """Cleans and de-duplicates queries"""
    
    clean_queries = set()

    for query in queries:
        # ✅ Remove garbled and invalid characters
        query = re.sub(r'[\u00b7\\,]', '', query).strip()

        # ✅ Remove trailing dots and redundant characters
        query = query.rstrip('.,')

        # ✅ Remove incomplete or corrupted queries
        if len(query) > 5 and "..." not in query:
            clean_queries.add(query)

    return sorted(clean_queries)


# ✅ Execution flow
def generate_queries(domain):
    """Generate queries for the given domain"""

    print("\n🔍 Fetching Serper results...")
    serper_data = fetch_serper_results(domain)

    if serper_data:
        print("\n✅ SERPER extracted queries:")
        for idx, query in enumerate(serper_data, start=1):
            print(f"{idx}. {query}")

        print("\n🔍 Generating queries with Qwen...")
        qwen_queries = generate_queries_with_qwen(domain, serper_data)

        # ✅ Combine Serper and Qwen queries with de-duplication
        combined_queries = clean_and_deduplicate_queries(serper_data + qwen_queries)

        if combined_queries:
            print("\n✅ Final Cleaned Queries for Integration:")
            for idx, query in enumerate(combined_queries, start=1):
                print(f"{idx}. {query}")
            return combined_queries
        else:
            print("\n❌ No valid queries generated.")
            return []
    else:
        print("\n❌ Serper failed to fetch relevant results.")
        return []


# ✅ Main Execution
if __name__ == "__main__":
    domain = input("\n🌐 Enter domain: ").strip()
    queries = generate_queries(domain)

    # ✅ Display final cleaned queries
    if queries:
        print("\n🎯 Final Cleaned Queries for Integration:\n")
        for idx, query in enumerate(queries, start=1):
            print(f"{idx}. {query}")
