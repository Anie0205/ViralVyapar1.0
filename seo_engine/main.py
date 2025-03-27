import os
from api_fetcher import fetch_seo_data
from train import train_models
from seo_analyser import analyze_seo
from rag_generator import generate_seo_content_rag  # Import without circular reference

# ✅ Constants
DATA_PATH = "data/seo_data.csv"
ANALYSIS_PATH = "data/seo_analysis_results.csv"

# ✅ Step 1: Fetch SEO data
print("\n🔍 Fetching SEO data...")
queries = [
    "SEO strategies for health blogs",
    "how to rank health tips on Google",
    "top health-related keywords 2025",
    "SEO optimization for medical websites",
    "backlink strategies for healthcare sites"
]

fetch_seo_data(queries)

# ✅ Step 2: Train Models
print("\n⚙️  Training models...")
train_models()

# ✅ Step 3: SEO Analysis
print("\n📊 Running SEO analysis...")
analyze_seo(DATA_PATH)

# ✅ Step 4: RAG-enhanced SEO content generation
print("\n🔍 Running RAG-enhanced SEO content generation...")

# Example RAG Query
query = "Effective healthcare SEO strategies in 2025"
print(f"\n🚀 Generating content for: {query}")

# ✅ Generate SEO content with RAG
results = generate_seo_content_rag(query, max_tokens=1000)

# ✅ Display the generated content
print("\n✅ Generated SEO content:\n")
print(results)
