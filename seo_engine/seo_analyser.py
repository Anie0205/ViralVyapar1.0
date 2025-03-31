import pandas as pd
import numpy as np
import random

# ✅ Paths
SEO_CSV_PATH = "data/seo_data.csv"
ANALYSIS_OUTPUT_PATH = "output/seo_analysis.json"

# ✅ Simulated difficulty and CTR estimation functions
def estimate_difficulty(query):
    """Simulate keyword difficulty estimation (ML placeholder)."""
    return round(np.random.uniform(10, 90), 2)  # Simulate difficulty score

def estimate_ctr(position):
    """Simulate CTR estimation based on position."""
    base_ctr = {1: 30, 2: 20, 3: 15, 4: 10, 5: 7, 6: 5, 7: 4, 8: 3, 9: 2, 10: 1}
    return base_ctr.get(position, np.random.uniform(0.5, 5))

# ✅ SEO Analysis Function
def analyze_seo(csv_file):
    """Analyzes SEO data and appends difficulty & CTR to the dataset."""
    df = pd.read_csv(csv_file)
    
    if "difficulty" not in df.columns or "ctr" not in df.columns:
        print("\n🔍 Adding difficulty and CTR columns...")

        # ✅ Add missing columns
        df["difficulty"] = df["query"].apply(estimate_difficulty)
        df["ctr"] = df["position"].apply(estimate_ctr)
    
    # ✅ Save to CSV
    df.to_csv(SEO_CSV_PATH, index=False)
    
    # ✅ Save to JSON
    df.to_json(ANALYSIS_OUTPUT_PATH, orient="records", indent=4)
    
    print(f"✅ SEO analysis saved to: {ANALYSIS_OUTPUT_PATH}")

# ✅ Main Execution
if __name__ == "__main__":
    analyze_seo(SEO_CSV_PATH)
