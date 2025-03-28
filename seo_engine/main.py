import os
import json
import pandas as pd
from api_fetcher import fetch_seo_data
from train import train_models
from seo_analyser import analyze_seo
from rag_generator import generate_seo_content_rag  # Import without circular reference

# ✅ Constants
DATA_PATH = "data/seo_data.csv"
ANALYSIS_PATH = "data/seo_analysis_results.csv"
REPORT_PATH = "output/seo_report.txt"
JSON_OUTPUT_PATH = "output/seo_optimized_content.json"

# ✅ Ensure output directory exists
os.makedirs("output", exist_ok=True)

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

def save_report(query, content, report_path):
    """
    Save the SEO content to a text report file.

    Args:
        query (str): The SEO query.
        content (str): The generated content.
        report_path (str): Path to save the report.
    """
    with open(report_path, "w", encoding="utf-8") as report_file:
        report_file.write(f"SEO Report for: {query}\n")
        report_file.write("=" * 50 + "\n\n")
        report_file.write(content)

    print(f"\n✅ SEO report saved to: {report_path}")

def extract_top_keywords(csv_path, top_n=5):
    """
    Extracts top-performing keywords from SEO analysis results.

    Args:
        csv_path (str): Path to the SEO analysis results CSV.
        top_n (int): Number of top keywords to extract.

    Returns:
        list: List of top keywords.
    """
    df = pd.read_csv(csv_path)
    
    # Sort by CTR and Difficulty Score to get top-performing keywords
    df['score'] = df['Predicted CTR'] / (df['Difficulty Score'] + 1)  # Weighted score
    top_keywords = df.sort_values(by='score', ascending=False).head(top_n)['Keyword'].tolist()
    
    print(f"\n✅ Top {top_n} Keywords:\n{top_keywords}")
    return top_keywords

def optimize_content(content, keywords):
    """
    Optimizes the content by strategically inserting top keywords.

    Args:
        content (str): The original SEO content.
        keywords (list): List of top-performing keywords.

    Returns:
        str: Optimized content.
    """
    # Inserting top keywords at strategic positions
    optimized_content = content
    
    # Insert keywords at the beginning, middle, and end
    if len(keywords) >= 3:
        optimized_content = (
            f"{keywords[0]} - {optimized_content[:100]}\n\n"
            f"{optimized_content[100:-100]}\n\n"
            f"{keywords[1]} {keywords[2]} - {optimized_content[-100:]}"
        )
    else:
        for kw in keywords:
            optimized_content += f"\n\n{kw}"

    return optimized_content

def save_json_output(query, original_content, optimized_content, keywords, json_path):
    """
    Save the SEO-optimized content with keywords into a JSON file.

    Args:
        query (str): The SEO query.
        original_content (str): The original RAG-generated content.
        optimized_content (str): The content with keywords integrated.
        keywords (list): List of top-performing keywords.
        json_path (str): Path to save the JSON output.
    """
    output_data = {
        "query": query,
        "top_keywords": keywords,
        "original_content": original_content,
        "optimized_content": optimized_content
    }

    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(output_data, json_file, indent=4)

    print(f"\n✅ SEO-optimized content saved to: {json_path}")


# ✅ Extract top keywords
top_keywords = extract_top_keywords(ANALYSIS_PATH)

# ✅ Optimize the RAG-generated content
optimized_content = optimize_content(results, top_keywords)

# ✅ Save the report to a text file
save_report(query, results, REPORT_PATH)

# ✅ Save the optimized content to a JSON file
save_json_output(query, results, optimized_content, top_keywords, JSON_OUTPUT_PATH)

# ✅ Display and save the generated content
print("\n✅ Generated SEO content:\n")
print(results)

# ✅ Save the report to a `.txt` file
save_report(query, results, REPORT_PATH)