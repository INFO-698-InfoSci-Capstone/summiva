import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load pre-built FAISS index and mapping
faiss_index = faiss.read_index("faiss/summiva.index")
doc_ids = np.load("faiss/doc_ids.npy")  # List of doc IDs in same order as FAISS vectors

def semantic_search(text: str, k=10):
    embedding = model.encode([text])
    distances, indices = faiss_index.search(embedding, k)
    return [{"doc_id": doc_ids[i], "score": float(1 - d)} for i, d in zip(indices[0], distances[0])]
