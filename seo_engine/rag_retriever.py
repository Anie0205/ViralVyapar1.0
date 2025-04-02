import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import os

class RAGRetriever:
    def __init__(self):
        # ✅ Load the SEO data
        self.data_path = "data/seo_data.csv"
        try:
            self.df = pd.read_csv(self.data_path)
        except FileNotFoundError:
            print(f"❌ RAG Retriever: SEO data file not found at {self.data_path}")
            self.df = pd.DataFrame() # Use empty dataframe
        except Exception as e:
            print(f"❌ RAG Retriever: Error loading SEO data CSV: {e}")
            self.df = pd.DataFrame()
            
        # ✅ Load the embedding model
        try:
            self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            print(f"❌ RAG Retriever: Error loading SentenceTransformer model: {e}")
            self.embedder = None

        # ✅ Load FAISS index and embeddings
        try:
            self.index = faiss.read_index("models/faiss_index.bin")
            self.embeddings = np.load("models/embeddings.npy")
        except FileNotFoundError:
            print("❌ RAG Retriever: FAISS index or embeddings not found. Index needs to be built.")
            self.index = None
            self.embeddings = None
        except Exception as e:
            print(f"❌ RAG Retriever: Error loading FAISS index or embeddings: {e}")
            self.index = None
            self.embeddings = None
            
        # NOTE: Consistency check removed as index is built by main.py now.

    def retrieve_similar(self, query, top_k=5):
        """Retrieve top-k similar SEO entries based on query"""
        
        # Check if index or embedder failed to load
        if self.index is None or self.embeddings is None or self.embedder is None:
            print("❌ RAG Retriever not properly initialized. Cannot retrieve.")
            return []
        if self.df.empty:
            print("❌ RAG Retriever: No SEO data loaded. Cannot retrieve.")
            return []
        
        # ✅ Encode the query
        query_embedding = self.embedder.encode([query], convert_to_tensor=False)

        # ✅ Perform the FAISS search
        # Ensure query_embedding is float32 and 2D
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        query_embedding = query_embedding.astype(np.float32)
            
        distances, indices = self.index.search(query_embedding, top_k)

        # ✅ Collect results
        results = []
        for i in range(top_k):
            idx = indices[0][i]
            
            # Ensure the index is within bounds
            if 0 <= idx < len(self.df):
                row = self.df.iloc[idx]
                results.append({
                    "title": row.get('title', 'N/A'), # Use .get() for safety
                    "snippet": row.get('snippet', 'N/A'), # Use .get() for safety
                    "link": row.get('link', 'N/A'), # Use .get() for safety
                    "difficulty": row.get('difficulty', 'N/A'), # Use .get() to avoid KeyError
                    "ctr": row.get('ctr', 'N/A'), # Use .get() to avoid KeyError
                    "score": distances[0][i]
                })
            else:
                print(f"⚠️ Invalid index {idx}, skipping...")
        
        return results

    def refine_content(self, content, seo_analysis):
        """Refine the generated content based on SEO analysis and retrieved similar content."""
        # Create a prompt for refinement
        prompt = f"Refine the following content based on SEO analysis:\n\n"
        prompt += f"Content to refine:\n{content}\n\n"
        prompt += f"SEO Analysis:\n{seo_analysis}\n\n"
        prompt += "Please improve the content while maintaining its core message and incorporating SEO best practices."

        # Retrieve similar content for context
        similar_content = self.retrieve_similar(prompt, top_k=3)
        
        # Combine context with the prompt
        context = "\n".join([
            f"Title: {r['title']}\nSnippet: {r['snippet']}\n"
            for r in similar_content
        ])
        
        final_prompt = f"### Context:\n{context}\n\n### Instruction:\n{prompt}"
        
        # For now, return the original content with a note about refinement
        # In a real implementation, you would use an LLM here to refine the content
        refined_content = f"Refined content based on SEO analysis:\n\n{content}"
        
        return refined_content

if __name__ == "__main__":
    # Test the retriever
    query = "Effective healthcare SEO strategies in 2025"
    retriever = RAGRetriever()
    results = retriever.retrieve_similar(query, top_k=5)

    print("\n🔍 Retrieved SEO Results:\n")
    for i, result in enumerate(results):
        print(f"{i + 1}. {result['title']}")
        print(f"   Snippet: {result['snippet']}")
        print(f"   Link: {result['link']}")
        print(f"   Difficulty: {result['difficulty']}")
        print(f"   CTR: {result['ctr']}")
        print(f"   Score: {result['score']:.4f}\n")
