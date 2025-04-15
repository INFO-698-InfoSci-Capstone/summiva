from datetime import datetime
from bson import ObjectId
import celery

from src.core.tagger import extract_tags
from src.database.mongo_session import mongo_db
from src.database.postgres_session import get_pg_session, Tags
from src.config.config import settings

celery_app = celery.Celery(
    'summiva_tagger',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

@celery_app.task
def run_tagging(doc_id: str):
    doc = mongo_db["docs"].find_one({"_id": ObjectId(doc_id)})
    if not doc or not doc.get("summary_text"):
        return "Summary not found for tagging"

    summary = doc["summary_text"]
    tags = extract_tags(summary)

    # Update MongoDB
    mongo_db["docs"].update_one(
        {"_id": ObjectId(doc_id)},
        {"$set": {"tags": tags, "tagged_at": datetime.utcnow()}}
    )

    # Insert into PostgreSQL
    session = get_pg_session()
    pg_tag = Tags(
        doc_id=doc_id,
        entities=tags["entities"],
        topics=tags["topics"],
        created_at=datetime.utcnow()
    )
    session.add(pg_tag)
    session.commit()
    session.close()

    return tags
