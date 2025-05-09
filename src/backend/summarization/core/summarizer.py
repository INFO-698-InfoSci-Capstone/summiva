"""
Summarization Module

Primary entry point for summarization functionality.
Uses Mistral-7B with INT4 quantization and LoRA fine-tuning as the primary model,
with T5-small as a fallback option.
"""
from enum import Enum
from typing import Dict, Any, Optional, Union
from transformers import pipeline

# Import the Mistral-7B summarizer
try:
    from backend.summarization.core.mistral_summarizer import summarize_text as mistral_summarize
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False

# Load T5 model once globally (as fallback)
t5_summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")

class ModelType(str, Enum):
    MISTRAL_7B = "mistral-7b"
    T5_SMALL = "t5-small"
    DEFAULT = "default"

def summarize_text(
    text: str, 
    max_length: int = 150, 
    min_length: int = 30,
    model: Union[str, ModelType] = ModelType.DEFAULT
) -> Dict[str, Any]:
    """
    Generate a summary of the input text using the specified model
    
    Args:
        text: Text to summarize
        max_length: Maximum summary length
        min_length: Minimum summary length
        model: Model to use for summarization
        
    Returns:
        Dict with summary and metrics
    """
    if isinstance(model, str):
        try:
            model = ModelType(model)
        except ValueError:
            model = ModelType.DEFAULT
    
    # Use Mistral-7B as default when available
    if model == ModelType.DEFAULT:
        model = ModelType.MISTRAL_7B if MISTRAL_AVAILABLE else ModelType.T5_SMALL
    
    # Handle empty input
    if not text.strip():
        return {
            "summary": "No content to summarize.",
            "original_length": 0,
            "summary_length": 0,
            "compression_ratio": 0.0
        }
    
    # Calculate original text length (word count)
    original_length = len(text.split())
    
    # Generate summary with selected model
    if model == ModelType.MISTRAL_7B and MISTRAL_AVAILABLE:
        try:
            return mistral_summarize(text, max_length, min_length)
        except Exception as e:
            print(f"Error with Mistral-7B summarization: {str(e)}")
            print("Falling back to T5-small")
            model = ModelType.T5_SMALL
    
    # Fallback to T5 if Mistral-7B is not available or fails
    if model == ModelType.T5_SMALL or not MISTRAL_AVAILABLE:
        summary = t5_summarizer(
            text, 
            max_length=max_length, 
            min_length=min_length, 
            do_sample=False
        )[0]['summary_text']
        
        # Calculate summary length and compression ratio
        summary_length = len(summary.split())
        compression_ratio = summary_length / original_length if original_length > 0 else 0.0
        
        return {
            "summary": summary,
            "original_length": original_length,
            "summary_length": summary_length,
            "compression_ratio": compression_ratio
        }
