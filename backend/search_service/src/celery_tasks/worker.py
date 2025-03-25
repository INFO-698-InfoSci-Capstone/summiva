import celery
from datetime import datetime
from backend.settings import Settings
from src.core.summarizer import summarize_text
from src.database.mongo_session import mongo_db
from bson.objectid import ObjectId

settings = Settings()

# Initialize Celery app
celery_app = celery.Celery(
    'summiva_summarizer',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
def run_summarization(doc_id_str: str, raw_text: str):
    """Celery task to do summarization asynchronously."""
    summary = summarize_text(raw_text)
    docs_collection = mongo_db['docs']
    
    # Update doc with summary
    docs_collection.update_one(
        {"_id": ObjectId(doc_id_str)},
        {"$set": {
            "summary_text": summary,
            "status": "completed",
            "updated_at": datetime.utcnow()
        }}
    )
    return summary