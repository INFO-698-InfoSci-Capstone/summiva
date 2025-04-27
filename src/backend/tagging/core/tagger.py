import time
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from typing import Dict, List, Any
import spacy

def download_nltk_data():
    """Download required NLTK data"""
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('maxent_ne_chunker')
    nltk.download('words')
    nltk.download('stopwords')

def preprocess_text(text: str) -> str:
    """Preprocess text by removing stopwords and converting to lowercase"""
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    return ' '.join([word for word in words if word not in stop_words])

def extract_named_entities(text: str) -> List[str]:
    """Extract named entities from text using NLTK"""
    words = word_tokenize(text)
    tagged = pos_tag(words)
    named_entities = ne_chunk(tagged)
    
    entities = []
    for chunk in named_entities:
        if hasattr(chunk, 'label'):
            entities.append(' '.join(c[0] for c in chunk))
    
    return entities

def extract_keywords(text: str, nlp) -> List[Dict[str, Any]]:
    """Extract keywords using spaCy"""
    doc = nlp(text)
    keywords = []
    
    for token in doc:
        if (token.pos_ in ['NOUN', 'PROPN'] and 
            not token.is_stop and 
            len(token.text) > 2):
            keywords.append({
                'text': token.text,
                'pos': token.pos_,
                'lemma': token.lemma_,
                'confidence': 100  # Placeholder confidence score
            })
    
    return keywords

def extract_tags(
    text: str,
    max_tags: int = 5,
    min_confidence: int = 70
) -> Dict[str, Any]:
    """Extract tags from text using NLP techniques"""
    start_time = time.time()
    
    # Download NLTK data if not already downloaded
    try:
        download_nltk_data()
    except:
        pass
    
    # Load spaCy model
    try:
        nlp = spacy.load('en_core_web_sm')
    except:
        spacy.cli.download('en_core_web_sm')
        nlp = spacy.load('en_core_web_sm')
    
    # Preprocess text
    preprocessed_text = preprocess_text(text)
    
    # Extract named entities
    named_entities = extract_named_entities(text)
    
    # Extract keywords
    keywords = extract_keywords(text, nlp)
    
    # Combine and rank tags
    all_tags = []
    
    # Add named entities with high confidence
    for entity in named_entities:
        all_tags.append({
            'text': entity,
            'type': 'named_entity',
            'confidence': 90
        })
    
    # Add keywords
    all_tags.extend(keywords)
    
    # Sort by confidence and limit to max_tags
    all_tags.sort(key=lambda x: x['confidence'], reverse=True)
    selected_tags = all_tags[:max_tags]
    
    # Filter by minimum confidence
    selected_tags = [tag for tag in selected_tags if tag['confidence'] >= min_confidence]
    
    processing_time = time.time() - start_time
    
    return {
        'tags': selected_tags,
        'processing_time': processing_time
    } 