from fastapi import APIRouter, HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from bson.objectid import ObjectId
from datetime import datetime
import datetime as dt

from src.models.summary import SummarizeRequest
from src.config.settings import Settings
from src.utils.security import get_authenticated_user_id
from src.services.content_ingestion import get_raw_text
from src.database.mongo_session import mongo_db
from src.celery_tasks.worker import run_summarization

router = APIRouter()
security = HTTPBearer()

@router.post("/api/v1/summarize")
def enqueue_summarization(
    req: SummarizeRequest,
    creds: HTTPAuthorizationCredentials = Security(security),
    settings: Settings = Depends(Settings)
):
    user_id = get_authenticated_user_id(creds)

    # Fetch raw text from URL or provided text
    try:
        raw_text = get_raw_text(req.url, req.text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get content: {str(e)}")

    # Insert into MongoDB
    docs_col = mongo_db["docs"]
    doc_insert = docs_col.insert_one({
        "owner": user_id,
        "raw_text": raw_text,
        "summary_text": None,
        "status": "pending",
        "created_at": datetime.now(dt.timezone.utc)
    })
    doc_id = str(doc_insert.inserted_id)

    # Upsert into user_docs
    user_docs_col = mongo_db["user_docs"]
    user_docs_col.update_one(
        {"user_id": user_id},
        {"$addToSet": {"doc_ids": doc_id}},
        upsert=True
    )

    # Enqueue Celery task
    run_summarization.delay(doc_id, raw_text)

    return {
        "doc_id": doc_id,
        "status": "queued"
    }


@router.get("/api/v1/docs/{doc_id}")
def get_doc(
    doc_id: str,
    creds: HTTPAuthorizationCredentials = Security(security),
):
    user_id = get_authenticated_user_id(creds)

    # Check document ownership
    user_docs_col = mongo_db["user_docs"]
    record = user_docs_col.find_one({"user_id": user_id})
    if not record or doc_id not in record.get("doc_ids", []):
        raise HTTPException(status_code=403, detail="Document not owned by user")

    docs_col = mongo_db["docs"]
    doc_obj = docs_col.find_one(
        {"_id": ObjectId(doc_id)},
        {"raw_text": 1, "summary_text": 1, "status": 1}
    )

    if not doc_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "raw_text": doc_obj.get("raw_text"),
        "summary_text": doc_obj.get("summary_text"),
        "status": doc_obj.get("status", "unknown")
    }