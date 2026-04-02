import os
import json
import faiss
import numpy as np
from embeddings.embedder import Embedder

# Paths
DATA_DIR = "data"
VECTOR_STORE_DIR = "vector_store"
INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "index.faiss")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.json")

def load_data():
    """Recursively load all supported files from data directory."""
    documents = []
    print(f"Scanning {DATA_DIR} for knowledge...")
    
    supported_extensions = ('.json', '.txt', '.md', '.yaml', '.yml')
    
    for root, dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.endswith(supported_extensions):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        if file.endswith(".json"):
                            data = json.load(f)
                            text_content = f"Title: {data.get('title', 'No Title')}\n"
                            text_content += f"Type: {data.get('incident_id', 'Lesson')}\n"
                            text_content += json.dumps(data, indent=2)
                            
                            documents.append({
                                "path": path,
                                "content": text_content,
                                "metadata": data
                            })
                        else:
                            # Handle text-based files
                            content = f.read()
                            title = os.path.basename(file)
                            doc_type = "Document"
                            if file.endswith((".yaml", ".yml")):
                                doc_type = "Pattern"
                            
                            text_content = f"Title: {title}\nType: {doc_type}\nContent:\n{content}"
                            
                            documents.append({
                                "path": path,
                                "content": text_content,
                                "metadata": {
                                    "title": title,
                                    "type": doc_type,
                                    "source": path
                                }
                            })
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    
    print(f"Found {len(documents)} documents.")
    return documents

def build_index():
    # 1. Ensure output directory exists
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    
    # 2. Load Documents
    docs = load_data()
    if not docs:
        print("No documents found to index.")
        return

    # 3. Initialize Embedder
    embedder = Embedder()
    
    # 4. Generate Embeddings
    print("Generating embeddings...")
    embeddings = []
    metadata_store = {}
    
    for i, doc in enumerate(docs):
        vector = embedder.embed_text(doc["content"])
        embeddings.append(vector)
        # Store metadata with ID matching the index in FAISS
        metadata_store[str(i)] = doc["metadata"]
        
    # Convert to numpy array for FAISS
    embedding_matrix = np.array(embeddings).astype("float32")
    dimension = embedding_matrix.shape[1]
    
    # 5. Create and Train FAISS Index
    print(f"Building FAISS index (Dimension: {dimension})...")
    index = faiss.IndexFlatL2(dimension)
    index.add(embedding_matrix)
    
    # 6. Save Index and Metadata
    print(f"Saving index to {INDEX_PATH}...")
    faiss.write_index(index, INDEX_PATH)
    
    print(f"Saving metadata to {METADATA_PATH}...")
    with open(METADATA_PATH, "w") as f:
        json.dump(metadata_store, f, indent=2)
        
    print(" Knowledge Base Building Complete! 🧠")

if __name__ == "__main__":
    build_index()
