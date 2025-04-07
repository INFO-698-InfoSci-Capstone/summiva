from celery_tasks.worker.celery_app import celery_app
import time

@celery_app.task(name='summarize_text', queue='summarization')
def summarize_text(text: str):
    """
    Example task for text summarization
    """
    # Simulate processing time
    time.sleep(2)
    return f"Summary of: {text[:100]}..."

@celery_app.task(name='tag_text', queue='tagging')
def tag_text(text: str):
    """
    Example task for text tagging
    """
    # Simulate processing time
    time.sleep(1)
    return ["tag1", "tag2", "tag3"] 