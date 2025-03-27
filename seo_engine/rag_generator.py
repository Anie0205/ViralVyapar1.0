import os
import requests
import json
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ✅ Load API Keys
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HF_API_KEY:
    print("❌ HUGGINGFACE_API_KEY is not set.")
    exit()

# ✅ Hugging Face Inference API Endpoint
GATED_MODEL = "meta-llama/Llama-3.2-3B-Instruct"
API_URL = f"https://api-inference.huggingface.co/models/{GATED_MODEL}"
HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# ✅ FAISS Index and Embedding Model Paths
INDEX_PATH = "models/faiss_index.bin"
EMBEDDINGS_PATH = "models/embeddings.npy"
DATA_PATH = "data/seo_data.csv"

# ✅ Load FAISS index and embeddings
print("\n🔍 Loading FAISS index and embeddings...")
index = faiss.read_index(INDEX_PATH)
embeddings = np.load(EMBEDDINGS_PATH)

# ✅ Load SEO data
df = pd.read_csv(DATA_PATH)

# ✅ Initialize the sentence embedder
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# ✅ FAISS Retriever Function
def retrieve_similar(query, top_k=5):
    """Retrieve top-k similar SEO entries"""
    query_embedding = embedder.encode([query], convert_to_tensor=False)
    distances, indices = index.search(np.array(query_embedding, dtype='float32'), top_k)

    results = []
    for i in range(top_k):
        row = df.iloc[indices[0][i]]
        results.append({
            "title": row['title'],
            "snippet": row['snippet'],
            "link": row['link'],
            "difficulty": row['difficulty'],
            "ctr": row['ctr'],
            "score": distances[0][i]
        })

    return results


# ✅ Generate SEO Content with RAG
def generate_seo_content_rag(prompt, max_tokens=1000, top_k=5):
    """Generates SEO content using RAG with FAISS retrieval and HF inference."""

    # 🔍 Retrieve relevant SEO content
    print(f"\n🔍 Retrieving relevant SEO context for: {prompt}")
    retrieved = retrieve_similar(prompt, top_k)

    # ✅ Construct the RAG Context
    context = "\n".join([
        f"Title: {r['title']}\nSnippet: {r['snippet']}\nLink: {r['link']}\n" 
        f"Difficulty: {r['difficulty']}\nCTR: {r['ctr']}\nScore: {r['score']}\n"
        for r in retrieved
    ])

    # ✅ Combine context with the prompt
    final_prompt = f"### Context:\n{context}\n\n### Instruction:\n{prompt}"

    # ✅ Prepare the request payload
    payload = {
        "inputs": final_prompt,
        "parameters": {
            "max_tokens": max_tokens,
            "return_full_text": True
        }
    }

    # ✅ Make POST request to HF Inference API
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            # Extract and return the generated content
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
                return result[0]['generated_text']
            else:
                return "No content generated."
        
        elif response.status_code == 401:
            return f"❌ Unauthorized: Check your HF API key."

        elif response.status_code == 403:
            return f"❌ Forbidden: Model access issue. Verify you have gated access."

        else:
            return f"❌ API Error {response.status_code}: {response.text}"

    except Exception as e:
        print(f"❌ Error during inference: {str(e)}")
        return "Error during inference."


# ✅ Test the RAG-enhanced generator
if __name__ == "__main__":
    query = "Best SEO strategies for e-commerce websites in 2025"
    print("\n🚀 Generating RAG-enhanced SEO content...\n")

    # Generate the content
    content = generate_seo_content_rag(query, max_tokens=1500, top_k=5)

    # ✅ Display the generated content
    print("\n✅ Generated SEO Content:\n")
    print(content)
