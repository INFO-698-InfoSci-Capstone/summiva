from transformers import pipeline

# Load once globally (not inside the function)
summarizer_pipeline = pipeline("summarization", model="t5-small", tokenizer="t5-small")

def summarize_text(text: str, max_length: int = 130, min_length: int = 30) -> str:
    if not text.strip():
        return "No content to summarize."
    
    summary = summarizer_pipeline(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']
