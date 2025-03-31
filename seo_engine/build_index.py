import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

# ✅ Load the SEO data
data_path = "data/seo_data.csv"
df = pd.read_csv(data_path)

# ✅ Ensure the DataFrame has valid data
if df.empty or 'title' not in df.columns:
    print("❌ SEO data is empty or missing 'title' column. Please fetch new SEO data.")
    exit()

# ✅ Load the embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Use only the 'title' for embedding
texts = df['title'].tolist()

# ✅ Generate embeddings and convert to NumPy array
embeddings = np.array(embedder.encode(texts, convert_to_tensor=False), dtype='float32')

# ✅ Create FAISS index
dimension = embeddings.shape[1]  # Get the dimension from the NumPy array
index = faiss.IndexFlatL2(dimension)

# ✅ Add embeddings to the index
index.add(embeddings)

# ✅ Save the FAISS index and embeddings
os.makedirs("models", exist_ok=True)
faiss.write_index(index, "models/faiss_index.bin")
np.save("models/embeddings.npy", embeddings)

print("✅ FAISS index and embeddings saved successfully!")
