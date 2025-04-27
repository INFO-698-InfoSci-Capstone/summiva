import time
import json
import numpy as np
from typing import Dict, List, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

def load_models():
    """Load required NLP models"""
    try:
        nlp = spacy.load('en_core_web_sm')
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return nlp, model
    except:
        spacy.cli.download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
        model = SentenceTransformer('all-MiniLM-L6-v2')
        return nlp, model

def preprocess_text(text: str, nlp) -> str:
    """Preprocess text using spaCy"""
    doc = nlp(text)
    # Remove stop words and punctuation, lemmatize
    tokens = [token.lemma_.lower() for token in doc 
              if not token.is_stop and not token.is_punct]
    return ' '.join(tokens)

def vectorize_text(text: str, model) -> np.ndarray:
    """Convert text to vector using sentence transformer"""
    return model.encode(text)

def calculate_relevance(query_vector: np.ndarray, document_vectors: List[np.ndarray]) -> List[float]:
    """Calculate relevance scores using cosine similarity"""
    similarities = cosine_similarity([query_vector], document_vectors)[0]
    return similarities.tolist()

def search_documents(
    query: str,
    limit: int = 10,
    min_relevance: float = 0.5
) -> List[Dict[str, Any]]:
    """Search documents using semantic similarity"""
    start_time = time.time()
    
    # Load models
    nlp, model = load_models()
    
    # Preprocess query
    preprocessed_query = preprocess_text(query, nlp)
    
    # Vectorize query
    query_vector = vectorize_text(preprocessed_query, model)
    
    # Get all document vectors from database
    # This is a placeholder - in production, you'd use a proper vector database
    document_vectors = []
    document_ids = []
    
    # Calculate relevance scores
    relevance_scores = calculate_relevance(query_vector, document_vectors)
    
    # Combine results
    results = []
    for i, score in enumerate(relevance_scores):
        if score >= min_relevance:
            results.append({
                'document_id': document_ids[i],
                'relevance_score': float(score),
                'processing_time': time.time() - start_time
            })
    
    # Sort by relevance and limit results
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    results = results[:limit]
    
    return results 