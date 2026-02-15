import faiss
import os

INDEX_PATH = "vector_store/index.faiss"

def load_index(path=INDEX_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Index not found at {path}")
    return faiss.read_index(path)
