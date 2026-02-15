import faiss
import json
import os
import numpy as np
from typing import List, Dict

# Paths
VECTOR_STORE_DIR = "vector_store"
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.json")

# Singleton globals to avoid reloading on every request
_INDEX = None
_METADATA = None
_EMBEDDER = None

def get_embedder():
    global _EMBEDDER
    if _EMBEDDER is None:
        from embeddings.embedder import Embedder
        _EMBEDDER = Embedder()
    return _EMBEDDER

def load_resources():
    global _INDEX, _METADATA
    if _INDEX is None:
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"Index not found at {INDEX_PATH}. Run build_index.py first.")
        _INDEX = faiss.read_index(INDEX_PATH)
    
    if _METADATA is None:
        if not os.path.exists(METADATA_PATH):
            raise FileNotFoundError(f"Metadata not found at {METADATA_PATH}")
        with open(METADATA_PATH, 'r') as f:
            _METADATA = json.load(f)

def search_by_failure(query: str, k: int = 3) -> List[Dict]:
    """
    Searches the vector memory for similar failure scenarios.
    
    Args:
        query: The failure description or search term.
        k: Number of results to return.
        
    Returns:
        List of metadata dictionaries for the top matches.
    """
    load_resources()
    embedder = get_embedder()
    
    # 1. Embed query
    vector = embedder.embed_text(query)
    # Reshape for FAISS (1, dimension)
    vector = np.array([vector]).astype("float32")
    
    # 2. Search index
    # D is distances, I is indices
    D, I = _INDEX.search(vector, k)
    
    results = []
    # 3. Retrieve metadata
    for i, idx in enumerate(I[0]):
        if idx != -1: # FAISS returns -1 if not enough neighbors
            str_idx = str(idx)
            if str_idx in _METADATA:
                item = _METADATA[str_idx]
                item['score'] = float(D[0][i]) # Add relevance score (distance)
                results.append(item)
                
    return results

if __name__ == "__main__":
    # Test run
    print("Testing search...")
    results = search_by_failure("s3 outage")
    print(json.dumps(results, indent=2))
