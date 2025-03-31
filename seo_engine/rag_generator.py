import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# ✅ Load API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Ensure you have Gemini key in env variables
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY is not set.")
    exit()
genai.configure(api_key=GEMINI_API_KEY)
# ✅ Configure Gemini client
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")  # Use the main Gemini model

# ✅ FAISS Index and Embedding Model Paths
INDEX_PATH = "models/faiss_index.bin"
EMBEDDINGS_PATH = "models/embeddings.npy"
DATA_PATH = "data/seo_data.csv"

# ✅ Load FAISS index and embeddings
print("\n🔍 Loading FAISS index and embeddings...")
index = faiss.read_index(INDEX_PATH)
embeddings = np.load(EMBEDDINGS_PATH)

# ✅ Reshape embeddings if necessary
if len(embeddings.shape) == 1:
    embeddings = embeddings.reshape(1, -1)

# ✅ Load SEO data
df = pd.read_csv(DATA_PATH)

# ✅ Verify FAISS index and dataset consistency
num_index_vectors = index.ntotal
num_dataset_rows = len(df)

if num_index_vectors != num_dataset_rows:
    print(f"⚠️ Mismatched FAISS index and dataset sizes! Index: {num_index_vectors}, Dataset: {num_dataset_rows}")
    print("❗ Please rebuild the FAISS index.")
    exit()

# ✅ Initialize the sentence embedder
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ FAISS Retriever Function
def retrieve_similar(query, top_k=5):
    """Retrieve top-k similar SEO entries"""
    
    # ✅ Encode the query
    query_embedding = embedder.encode([query], convert_to_tensor=False)
    query_embedding = np.array(query_embedding, dtype='float32').reshape(1, -1)

    # ✅ Perform FAISS search
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for i in range(top_k):
        if indices[0][i] < len(df):
            row = df.iloc[indices[0][i]]
            results.append({
                "title": row.get('title', ''),
                "snippet": row.get('snippet', ''),
                "link": row.get('link', ''),
                "difficulty": row.get('difficulty', ''),
                "ctr": row.get('ctr', ''),
                "score": distances[0][i]
            })
        else:
            print(f"⚠️ Index {indices[0][i]} out of bounds.")
    
    return results

# ✅ Gemini Inference Function
def generate_seo_content_rag(prompt, max_tokens=1500, top_k=5):
    """Generates SEO content using RAG with FAISS retrieval and Gemini inference."""

    # 🔍 Retrieve relevant SEO content
    print(f"\n🔍 Retrieving relevant SEO context for: {prompt}")
    retrieved = retrieve_similar(prompt, top_k)

    # ✅ Construct the RAG context
    context = "\n".join([
        f"Title: {r['title']}\nSnippet: {r['snippet']}\nLink: {r['link']}\n" 
        f"Difficulty: {r['difficulty']}\nCTR: {r['ctr']}\nScore: {r['score']}\n"
        for r in retrieved
    ])

    # ✅ Combine context with the prompt
    final_prompt = f"### Context:\n{context}\n\n### Instruction:\n{prompt}"

    try:
        # ✅ Use Gemini's SDK for text generation
        response = model.generate_content(final_prompt)

        if response and hasattr(response, 'text'):
            return response.text
        else:
            return "No content generated."

    except Exception as e:
        print(f"❌ Error during inference: {str(e)}")
        return "Error during inference."


# ✅ Test the RAG-enhanced generator
if __name__ == "__main__":
    query = "Best SEO strategies for e-commerce websites in 2025"
    print("\n🚀 Generating RAG-enhanced SEO content with Gemini...\n")

    # Generate the content
    content = generate_seo_content_rag(query, max_tokens=1500, top_k=5)

    # ✅ Display the generated content
    print("\n✅ Generated SEO Content:\n")
    print(content)
