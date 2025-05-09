"""
Mistral-7B Summarizer Module

This module provides summarization functionality using the Mistral-7B model
with INT4 quantization and LoRA fine-tuning for optimal performance
with reduced memory footprint.
"""

import os
import torch
from typing import Dict, Any, Union
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig
)

# Configuration constants
MISTRAL_MODEL_ID = "mistralai/Mistral-7B-v0.1"
LORA_WEIGHTS_PATH = os.path.join(os.path.dirname(__file__), "../models/mistral_lora")
DEFAULT_MAX_LENGTH = 150
DEFAULT_MIN_LENGTH = 30

# Global variables for model and tokenizer
mistral_model = None
mistral_tokenizer = None

def load_mistral_model() -> tuple:
    """
    Load Mistral-7B model with INT4 quantization and LoRA weights
    
    Returns:
        tuple: (model, tokenizer) or (None, None) if loading fails
    """
    global mistral_model, mistral_tokenizer
    
    # Return cached model and tokenizer if already loaded
    if mistral_model is not None and mistral_tokenizer is not None:
        return mistral_model, mistral_tokenizer
        
    try:
        import peft
        
        # Configure INT4 quantization
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True
        )
        
        # Load base model with quantization
        print("Loading Mistral-7B base model with INT4 quantization...")
        mistral_model = AutoModelForCausalLM.from_pretrained(
            MISTRAL_MODEL_ID,
            device_map="auto",
            quantization_config=quantization_config,
            trust_remote_code=True
        )
        mistral_tokenizer = AutoTokenizer.from_pretrained(
            MISTRAL_MODEL_ID, 
            use_fast=True
        )
        
        # Apply padding config
        mistral_tokenizer.pad_token = mistral_tokenizer.eos_token
        mistral_tokenizer.padding_side = "right"
        
        # Load LoRA weights if available
        if os.path.exists(LORA_WEIGHTS_PATH):
            print(f"Loading LoRA weights from {LORA_WEIGHTS_PATH}")
            mistral_model = peft.PeftModel.from_pretrained(
                mistral_model,
                LORA_WEIGHTS_PATH
            )
        else:
            print("No LoRA weights found. Using base Mistral-7B model.")
        
        return mistral_model, mistral_tokenizer
        
    except Exception as e:
        print(f"Error loading Mistral-7B model: {str(e)}")
        print("Falling back to T5 summarization.")
        return None, None

def generate_summary_with_mistral(
    text: str, 
    max_length: int = DEFAULT_MAX_LENGTH,
    min_length: int = DEFAULT_MIN_LENGTH
) -> Union[str, None]:
    """
    Generate a summary using Mistral-7B with INT4 quantization and LoRA
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        min_length: Minimum length of summary
        
    Returns:
        str: Generated summary or None if generation fails
    """
    try:
        model, tokenizer = load_mistral_model()
        if model is None or tokenizer is None:
            raise ValueError("Mistral-7B model not available")
            
        # Prepare prompt for summarization
        prompt = f"""
        Please summarize the following text concisely while preserving the key information:
        
        {text}
        
        Summary:
        """
        
        # Tokenize input with appropriate padding and truncation
        inputs = tokenizer(
            prompt, 
            return_tensors="pt",
            truncation=True,
            max_length=4096
        ).to(model.device)
        
        # Generate summary
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                min_new_tokens=min_length,
                temperature=0.6,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Extract generated text
        generated_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        summary = generated_text.split("Summary:")[1].strip()
        
        return summary
        
    except Exception as e:
        print(f"Error generating summary with Mistral-7B: {str(e)}")
        return None

def summarize_text(
    text: str,
    max_length: int = DEFAULT_MAX_LENGTH,
    min_length: int = DEFAULT_MIN_LENGTH,
    model: str = "mistral-7b"
) -> Dict[str, Any]:
    """
    Generate a summary of the input text using Mistral-7B
    
    Args:
        text: Text to summarize
        max_length: Maximum length of summary
        min_length: Minimum length of summary
        model: Model name (for compatibility with existing code)
        
    Returns:
        Dict with summary and metrics
    """
    if not text.strip():
        return {
            "summary": "",
            "original_length": 0,
            "summary_length": 0,
            "compression_ratio": 0.0
        }
    
    # Calculate original text length (word count)
    original_length = len(text.split())
    
    # Generate summary with Mistral-7B
    summary = generate_summary_with_mistral(text, max_length, min_length)
    
    # If Mistral summarization fails, fall back to the existing summarizer
    if summary is None:
        from summarizer import summarize_text as fallback_summarize
        return fallback_summarize(text, max_length, min_length)
    
    # Calculate summary length (word count)
    summary_length = len(summary.split())
    
    # Calculate compression ratio
    compression_ratio = summary_length / original_length if original_length > 0 else 0.0
    
    return {
        "summary": summary,
        "original_length": original_length,
        "summary_length": summary_length,
        "compression_ratio": compression_ratio
    }