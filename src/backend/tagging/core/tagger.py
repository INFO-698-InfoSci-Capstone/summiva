import time
import os
import torch
from typing import Dict, List, Any
from transformers import AutoModelForCausalLM, AutoTokenizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk

# Constants for the Phi-2 model
PHI2_MODEL_ID = "microsoft/phi-2"
LORA_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "../models/phi2_lora")

# Global variables to store the model and tokenizer
phi2_model = None
phi2_tokenizer = None

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

def load_phi2_model():
    """Load Phi-2 model with INT4 quantization and LoRA weights if available"""
    global phi2_model, phi2_tokenizer
    
    if phi2_model is not None and phi2_tokenizer is not None:
        return phi2_model, phi2_tokenizer
        
    try:
        from transformers import BitsAndBytesConfig
        import peft
        
        # Configure INT4 quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        
        # Load base model with quantization
        print("Loading Phi-2 base model with INT4 quantization...")
        phi2_model = AutoModelForCausalLM.from_pretrained(
            PHI2_MODEL_ID,
            device_map="auto",
            quantization_config=quantization_config
        )
        phi2_tokenizer = AutoTokenizer.from_pretrained(PHI2_MODEL_ID)
        
        # Load LoRA weights if available
        if os.path.exists(LORA_WEIGHTS_PATH):
            print(f"Loading LoRA weights from {LORA_WEIGHTS_PATH}")
            phi2_model = peft.PeftModel.from_pretrained(
                phi2_model,
                LORA_WEIGHTS_PATH
            )
        else:
            print("No LoRA weights found. Using base Phi-2 model.")
        
        return phi2_model, phi2_tokenizer
    except Exception as e:
        print(f"Error loading Phi-2 model: {str(e)}")
        print("Falling back to traditional NLP methods.")
        return None, None

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

def extract_tags_with_phi2(text: str, max_tags: int = 5) -> List[Dict[str, Any]]:
    """Extract tags using Phi-2 model with INT4 quantization and LoRA"""
    try:
        model, tokenizer = load_phi2_model()
        if model is None or tokenizer is None:
            raise ValueError("Phi-2 model not available")
        
        # Prepare prompt for tag extraction
        prompt = f"""
        Extract key tags from the following text. Return only the most important 
        concepts as tags with confidence scores.
        
        Text: {text}
        
        Tags (format: tag name - confidence):
        """
        
        # Generate tags
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.2,
                top_p=0.9,
                do_sample=True
            )
        
        generated_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        generated_tags = generated_text.split("Tags (format: tag name - confidence):")[1].strip()
        
        # Parse generated tags
        tags_list = []
        for line in generated_tags.split("\n"):
            line = line.strip()
            if not line or "-" not in line:
                continue
            
            try:
                tag, confidence_str = line.split("-", 1)
                tag = tag.strip()
                confidence_str = confidence_str.strip().rstrip("%")
                confidence = float(confidence_str) if confidence_str.replace(".", "", 1).isdigit() else 70
                
                if tag and confidence >= 0:
                    tags_list.append({
                        "text": tag,
                        "type": "phi2",
                        "confidence": min(confidence, 100)
                    })
            except Exception:
                continue
        
        # Sort by confidence and limit to max_tags
        tags_list.sort(key=lambda x: x["confidence"], reverse=True)
        return tags_list[:max_tags]
        
    except Exception as e:
        print(f"Error extracting tags with Phi-2: {str(e)}")
        return []

def extract_tags(
    text: str,
    max_tags: int = 5,
    min_confidence: int = 70
) -> Dict[str, Any]:
    """Extract tags from text using NLP techniques"""
    start_time = time.time()
    all_tags = []
    
    # Try Phi-2 first for advanced tagging
    phi2_tags = extract_tags_with_phi2(text, max_tags=max_tags)
    
    # If Phi-2 tagging succeeded, use those tags
    if phi2_tags:
        all_tags = phi2_tags
        
    # Otherwise, fall back to traditional NLP methods
    else:
        # Download NLTK data if not already downloaded
        try:
            download_nltk_data()
        except:
            pass
        
        # Load spaCy model
        try:
            import spacy
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
            
            # Add named entities with high confidence
            for entity in named_entities:
                all_tags.append({
                    'text': entity,
                    'type': 'named_entity',
                    'confidence': 90
                })
            
            # Add keywords
            all_tags.extend(keywords)
        except Exception as e:
            print(f"Error in traditional NLP tagging: {str(e)}")
    
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