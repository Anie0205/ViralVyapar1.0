commands for now:
```
python api_fetcher.py
python train.py
python main.py
```
architecture for now:
```
seo-ai-tool/
├── seo_engine/
│   ├── __init__.py
│   ├── main.py                      # Main script
│   ├── api_fetcher.py               # Fetches SEO data
│   ├── seo_analyser.py              # Performs SEO analysis
│   ├── train.py                     # Trains ML models
│   ├── models/                      # Store ML models
│   │       ├── ctr_model.pkl
│   │       ├── keyword_difficulty.pkl
│   │       ├── faiss_index.bin      # FAISS index for RAG
│   │       ├── embeddings.npy       # Embeddings vectors
│   ├── data/                        # Data folder
│   │       ├── seo_data.csv
│   │       ├── seo_analysis_results.csv
│   ├── rag_retriever.py             # RAG retrieval logic
│   ├── rag_generator.py             # LLM content generation
├── requirements.txt
├── README.md

```
