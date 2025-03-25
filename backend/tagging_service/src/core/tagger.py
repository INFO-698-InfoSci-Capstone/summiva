from typing import List, Dict
import spacy

# Load spaCy's NER model (you can replace with transformers if needed)
nlp = spacy.load("en_core_web_sm")

def extract_tags(text: str) -> Dict[str, List[str]]:
    doc = nlp(text)
    entities = list(set(ent.text for ent in doc.ents))
    keywords = list(set(token.lemma_ for token in doc if token.is_alpha and not token.is_stop))
    return {
        "entities": entities,
        "topics": keywords[:10]  # top keywords
    }
