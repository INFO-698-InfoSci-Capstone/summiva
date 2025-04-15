import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str) -> np.ndarray:
    return model.encode(text, convert_to_numpy=True)

def find_best_cluster(embedding: np.ndarray, existing: list[dict], threshold: float = 0.75):
    """Return best matching cluster_id if similarity is high enough, else None."""
    best_score = 0.0
    best_cluster = None
    for cluster in existing:
        sim = cosine_similarity([embedding], [cluster["centroid"]])[0][0]
        if sim > best_score and sim >= threshold:
            best_score = sim
            best_cluster = cluster
    return best_cluster
