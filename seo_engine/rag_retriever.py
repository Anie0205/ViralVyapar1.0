import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

# ✅ Load the SEO data
data_path = "data/seo_data.csv"
df = pd.read_csv(data_path)

# ✅ Load the embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Load FAISS index and embeddings
index = faiss.read_index("models/faiss_index.bin")
embeddings = np.load("models/embeddings.npy")

def retrieve_similar(query, top_k=5):
    """Retrieve top-k similar SEO entries based on query"""
    
    # ✅ Encode the query
    query_embedding = embedder.encode([query], convert_to_tensor=False)

    # ✅ Perform the FAISS search
    distances, indices = index.search(np.array(query_embedding, dtype='float32'), top_k)

    # ✅ Collect results
    results = []
    for i in range(top_k):
        idx = indices[0][i]
        
        # Ensure the index is within bounds
        if 0 <= idx < len(df):
            row = df.iloc[idx]
            results.append({
                "title": row['title'],
                "snippet": row['snippet'],
                "link": row['link'],
                "difficulty": row['difficulty'],
                "ctr": row['ctr'],
                "score": distances[0][i]
            })
        else:
            print(f"⚠️ Invalid index {idx}, skipping...")
    
    return results

# ✅ Example usage
if __name__ == "__main__":
    query = "Effective healthcare SEO strategies in 2025"
    results = retrieve_similar(query, top_k=5)

    print("\n🔍 Retrieved SEO Results:\n")
    for i, result in enumerate(results):
        print(f"{i + 1}. {result['title']}")
        print(f"   Snippet: {result['snippet']}")
        print(f"   Link: {result['link']}")
        print(f"   Difficulty: {result['difficulty']}")
        print(f"   CTR: {result['ctr']}")
        print(f"   Score: {result['score']:.4f}\n")
