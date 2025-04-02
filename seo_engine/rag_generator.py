import os
import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

class RAGGenerator:
    def __init__(self):
        # ✅ Load API Keys
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if not self.GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY is not set.")
            raise ValueError("GEMINI_API_KEY is not set")
        
        # ✅ Configure Gemini client
        genai.configure(api_key=self.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-pro")

        # ✅ FAISS Index and Embedding Model Paths
        self.INDEX_PATH = "models/faiss_index.bin"
        self.EMBEDDINGS_PATH = "models/embeddings.npy"
        self.DATA_PATH = "data/seo_data.csv"

        # ✅ Load FAISS index and embeddings
        print("\n🔍 Loading FAISS index and embeddings...")
        self.index = faiss.read_index(self.INDEX_PATH)
        self.embeddings = np.load(self.EMBEDDINGS_PATH)

        # ✅ Reshape embeddings if necessary
        if len(self.embeddings.shape) == 1:
            self.embeddings = self.embeddings.reshape(1, -1)

        # ✅ Load SEO data
        self.df = pd.read_csv(self.DATA_PATH)

        # ✅ Initialize the sentence embedder
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def retrieve_similar(self, query, top_k=5):
        """Retrieve top-k similar SEO entries"""
        
        # ✅ Encode the query
        query_embedding = self.embedder.encode([query], convert_to_tensor=False)
        query_embedding = np.array(query_embedding, dtype='float32').reshape(1, -1)

        # ✅ Perform FAISS search
        distances, indices = self.index.search(query_embedding, top_k)

        results = []
        for i in range(top_k):
            if indices[0][i] < len(self.df):
                row = self.df.iloc[indices[0][i]]
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

    def generate_content(self, seo_analysis, keyword_data):
        """Generates SEO content using RAG with FAISS retrieval and Gemini inference."""
        # Create a prompt based on SEO analysis and keyword data
        prompt = f"Generate SEO-optimized content based on the following analysis:\n\n"
        prompt += f"SEO Analysis: {seo_analysis}\n\n"
        prompt += f"Keywords: {keyword_data}\n\n"
        prompt += "Please create comprehensive, engaging content that incorporates these insights."

        # 🔍 Retrieve relevant SEO content
        print(f"\n🔍 Retrieving relevant SEO context...")
        retrieved = self.retrieve_similar(prompt, top_k=5)

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
            response = self.model.generate_content(final_prompt)

            if response and hasattr(response, 'text'):
                return response.text
            else:
                return "No content generated."

        except Exception as e:
            print(f"❌ Error during inference: {str(e)}")
            return "Error during inference."

if __name__ == "__main__":
    # Test the RAG-enhanced generator
    query = "Best SEO strategies for e-commerce websites in 2025"
    print("\n🚀 Generating RAG-enhanced SEO content with Gemini...\n")

    # Initialize the generator
    generator = RAGGenerator()

    # Generate the content
    content = generator.generate_content(
        seo_analysis="Sample SEO analysis",
        keyword_data="Sample keyword data"
    )

    # ✅ Display the generated content
    print("\n✅ Generated SEO Content:\n")
    print(content)
