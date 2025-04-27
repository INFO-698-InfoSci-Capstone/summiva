from typing import Dict, Any
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def download_nltk_data():
    """Download required NLTK data"""
    nltk.download('punkt')
    nltk.download('stopwords')

def preprocess_text(text: str) -> str:
    """Preprocess text by removing stopwords and converting to lowercase"""
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    return ' '.join([word for word in words if word not in stop_words])

def calculate_sentence_scores(sentences: List[str], preprocessed_text: str) -> Dict[str, float]:
    """Calculate importance scores for each sentence"""
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([preprocessed_text] + sentences)
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    return {sentences[i]: float(similarity_matrix[0][i]) for i in range(len(sentences))}

def summarize_text(
    text: str,
    max_length: int = 150,
    min_length: int = 30
) -> Dict[str, Any]:
    """Generate a summary of the input text"""
    # Download NLTK data if not already downloaded
    try:
        download_nltk_data()
    except:
        pass
    
    # Tokenize sentences
    sentences = sent_tokenize(text)
    if not sentences:
        return {
            "summary": "",
            "original_length": 0,
            "summary_length": 0,
            "compression_ratio": 0.0
        }
    
    # Preprocess text
    preprocessed_text = preprocess_text(text)
    
    # Calculate sentence scores
    sentence_scores = calculate_sentence_scores(sentences, preprocessed_text)
    
    # Sort sentences by score
    ranked_sentences = sorted(
        sentence_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Generate summary
    summary_length = 0
    summary_sentences = []
    
    for sentence, score in ranked_sentences:
        sentence_length = len(word_tokenize(sentence))
        if summary_length + sentence_length <= max_length:
            summary_sentences.append(sentence)
            summary_length += sentence_length
        if summary_length >= min_length:
            break
    
    # Sort summary sentences by original order
    summary_sentences = sorted(
        summary_sentences,
        key=lambda x: sentences.index(x)
    )
    
    summary = ' '.join(summary_sentences)
    original_length = len(word_tokenize(text))
    
    return {
        "summary": summary,
        "original_length": original_length,
        "summary_length": summary_length,
        "compression_ratio": summary_length / original_length if original_length > 0 else 0.0
    } 