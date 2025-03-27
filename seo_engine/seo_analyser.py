import os
import pandas as pd
from transformers import pipeline
from joblib import load

MODEL_DIR = "models"

# Load the ML models
ctr_model = load(os.path.join(MODEL_DIR, "ctr_model.pkl"))
difficulty_model = load(os.path.join(MODEL_DIR, "keyword_difficulty.pkl"))

# Sentiment analysis pipeline (for content evaluation)
sentiment_analyzer = pipeline("sentiment-analysis")

def analyze_seo(file_path):
    """Analyze SEO data from the provided CSV file."""
    
    print(f"✅ Analyzing SEO data from {file_path}...")

    # Load the dataset
    df = pd.read_csv(file_path)
    
    if df.empty:
        print("❗ No data found in the CSV file.")
        return
    
    # Analyze each row
    results = []
    for _, row in df.iterrows():
        keyword = row['keyword']
        title = row['title']
        snippet = row['snippet']

        # --- Sentiment Analysis ---
        sentiment = sentiment_analyzer(snippet)[0]
        
        # --- CTR & Difficulty Prediction ---
        features = pd.DataFrame([[row['difficulty'], row['ctr']]], columns=['difficulty', 'ctr'])
        predicted_ctr = ctr_model.predict(features)[0]
        difficulty_score = difficulty_model.predict(features)[0]

        # Store results
        results.append({
            "Keyword": keyword,
            "Title": title,
            "Snippet": snippet,
            "Sentiment": sentiment['label'],
            "Sentiment Score": sentiment['score'],
            "Predicted CTR": predicted_ctr,
            "Difficulty Score": difficulty_score
        })

    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save the analysis results
    output_file = "data/seo_analysis_results.csv"
    results_df.to_csv(output_file, index=False)
    print(f"✅ SEO analysis saved to {output_file}")

    # Display sample results
    print("\n🔍 Sample Results:")
    print(results_df.head())

# Only run when executed directly
if __name__ == "__main__":
    analyze_seo("data/seo_data.csv")
