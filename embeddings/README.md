# Embeddings Pipeline
- **embedder.py**: Loads the SentenceTransformer model and converts text to vectors.
- **build_index.py**: Reads from `data/`, generates embeddings, and saves the FAISS index.
- **embedding_config.py**: Configuration for model names and embedding fields.
