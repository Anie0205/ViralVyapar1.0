from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd

# Load FAISS index and embeddings
index = faiss.read_index("models/faiss_index.bin")
embeddings = np.load("models/embeddings.npy")

# Load SEO data
df = pd.read_csv("data/seo_data.csv")

# Load the embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_similar(text, top_k=5):
    """Retrieve top-k similar SEO entries"""
    
    # ✅ Encode the query
    query_embedding = embedder.encode([text], convert_to_tensor=False)

    # ✅ Search FAISS index
    distances, indices = index.search(np.array(query_embedding, dtype='float32'), top_k)

    results = []
    for i in range(top_k):
        idx = indices[0][i]
        
        # ✅ Ensure index is in bounds
        if 0 <= idx < len(df):
            row = df.iloc[idx]  # Use index to access the DataFrame safely
            results.append({
                "title": row['title'],
                "snippet": row['snippet'],
                "link": row['link'],
                "difficulty": row['difficulty'],
                "ctr": row['ctr'],
                "score": distances[0][i]
            })
        else:
            print(f"❌ Invalid index: {idx} (out of bounds) - Skipping")

    return results

# Test retrieval
query = "Best SEO strategies for e-commerce websites in 2025"
results = retrieve_similar(query, top_k=5)

# Print the results
for res in results:
    print("\n🔹 Title:", res["title"])
    print("Snippet:", res["snippet"])
    print("Link:", res["link"])
    print("Difficulty:", res["difficulty"])
    print("CTR:", res["ctr"])
    print("Score:", res["score"])
