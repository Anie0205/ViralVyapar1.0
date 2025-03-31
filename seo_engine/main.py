import os
import json
import pandas as pd
from api_fetcher import fetch_seo_data
from train import train_models
from seo_analyser import analyze_seo
from rag_generator import generate_seo_content_rag
from query_generator import generate_queries

# ✅ Constants
SEO_DATA_FILE = "output/seo_analysis.json"
SEO_QUERIES_DIR = "output"
DATA_PATH = "data/seo_data.csv"

def main():
    """Main workflow execution"""

    # ✅ Get Domain from User
    domain = input("\n🌐 Enter the domain for SEO analysis (e.g., example.com): ").strip()

    # ✅ Step 1: Generate Queries
    print(f"\n🔍 Generating SEO queries for domain: {domain}")
    
    # Directly generate and retrieve the queries
    queries = generate_queries(domain)

    # ✅ Save Queries to JSON
    queries_file = f"{SEO_QUERIES_DIR}/{domain}_queries.json"
    os.makedirs(SEO_QUERIES_DIR, exist_ok=True)  # Ensure output directory exists

    with open(queries_file, "w", encoding="utf-8") as f:
        json.dump(queries, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Queries saved to: {queries_file}")

    # ✅ Step 2: Fetch SEO Data
    print("\n🔍 Fetching SEO data...")
    fetch_seo_data(queries)

    # ✅ Step 3: Run SEO Analysis
    print("\n⚙️ Running SEO analysis...")
    analyze_seo(DATA_PATH)

    # ✅ Step 4: Train Models
    print("\n⚙️ Training models...")
    train_models()

    # ✅ Step 5: Generate RAG-enhanced Content
    print("\n🚀 Generating RAG-enhanced content...")
    content = generate_seo_content_rag("Latest industry insights", max_tokens=1000)

    print("\n✅ Generated SEO Content:\n")
    print(content)

    # ✅ Save analysis results
    print(f"\n✅ SEO analysis results saved to: {SEO_DATA_FILE}")


if __name__ == "__main__":
    main()
