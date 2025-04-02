import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

def build_faiss_index():
    """Loads SEO data, generates embeddings, and builds/saves a FAISS index."""
    print("\n🔨 Building FAISS index...")
    
    # ✅ Load the SEO data
    data_path = "data/seo_data.csv"
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"❌ SEO data file not found at {data_path}. Cannot build index.")
        return False
    except Exception as e:
        print(f"❌ Error loading SEO data CSV: {e}")
        return False

    # ✅ Ensure the DataFrame has valid data
    if df.empty or 'title' not in df.columns:
        print("❌ SEO data is empty or missing 'title' column. Cannot build index.")
        return False

    # ✅ Load the embedding model
    print("Loading sentence transformer model...")
    try:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    except Exception as e:
        print(f"❌ Error loading SentenceTransformer model: {e}")
        return False
    print("Model loaded.")

    # ✅ Use only the 'title' for embedding
    texts = df['title'].fillna("").astype(str).tolist() # Handle potential NaN/non-string values
    if not texts:
        print("❌ No valid titles found in data to build index from.")
        return False

    # ✅ Generate embeddings and convert to NumPy array
    print(f"Generating embeddings for {len(texts)} texts...")
    try:
        embeddings = np.array(embedder.encode(texts, convert_to_tensor=False, show_progress_bar=True), dtype='float32')
    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return False
    print("Embeddings generated.")

    # ✅ Create FAISS index
    dimension = embeddings.shape[1]  # Get the dimension from the NumPy array
    index = faiss.IndexFlatL2(dimension)

    # ✅ Add embeddings to the index
    index.add(embeddings)

    # ✅ Save the FAISS index and embeddings
    try:
        os.makedirs("models", exist_ok=True)
        index_path = "models/faiss_index.bin"
        embeddings_path = "models/embeddings.npy"
        faiss.write_index(index, index_path)
        np.save(embeddings_path, embeddings)
        print(f"✅ FAISS index saved to: {index_path}")
        print(f"✅ Embeddings saved to: {embeddings_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving FAISS index or embeddings: {e}")
        return False

if __name__ == "__main__":
    build_faiss_index()
