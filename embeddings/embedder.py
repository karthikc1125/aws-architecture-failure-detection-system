from sentence_transformers import SentenceTransformer
import os

# fallback if config is missing
try:
    from embeddings.embedding_config import MODEL_NAME
except ImportError:
    MODEL_NAME = "all-MiniLM-L6-v2"

class Embedder:
    def __init__(self):
        print(f"Loading embedding model: {MODEL_NAME}...")
        try:
            self.model = SentenceTransformer(MODEL_NAME, device='cpu')
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def embed_text(self, text: str):
        """Converts text to vector."""
        return self.model.encode(text)
