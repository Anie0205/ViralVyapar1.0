from api_fetcher import fetch_seo_data
from train import train_models
from seo_analyser import analyze_seo

# --- Step 1: Fetch SEO Data ---
print("Fetching SEO data...")
keywords = [
    "best seo practices",
    "seo tools 2025",
    "keyword research tips",
    "backlink strategies",
    "content optimization"
]
fetch_seo_data(keywords)

# --- Step 2: Train Models ---
print("Training models...")
train_models()

# --- Step 3: Run SEO Analysis ---
print("Running SEO analysis...")
analyze_seo("data/seo_data.csv")
