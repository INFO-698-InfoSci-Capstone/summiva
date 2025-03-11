from fastapi import APIRouter, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import requests
from pydantic import BaseModel
from datetime import datetime
from bson.objectid import ObjectId

from src.config.settings import Settings
from src.database.mongo_session import mongo_db
# from src.celery_tasks.worker import run_summarization

router = APIRouter()
security = HTTPBearer()
settings = Settings()

def fetch_user_from_auth(bearer_token: str):
    """Call external Auth Service /user/me, passing Bearer token."""
    url = f"{settings.AUTH_SERVICE_URL}/user/me"
    headers = {"Authorization": f"Bearer {bearer_token}"}
    resp = requests.get(url, headers=headers, timeout=5)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="Auth /user/me call failed")
    return resp.json()

class SummarizeRequest(BaseModel):
    url: str | None = None
    text: str | None = None

@router.post("/api/v1/summarize")
def enqueue_summarization(req: SummarizeRequest, creds: HTTPAuthorizationCredentials = Security(security)):
    user_data = fetch_user_from_auth(creds.credentials)
    user_id = str(user_data.get("id", ""))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Retrieve raw text from URL or request.text
    if req.url:
        resp = requests.get(req.url)
        raw_text = resp.text
    elif req.text:
        raw_text = req.text
    else:
        raise HTTPException(status_code=400, detail="No valid text or URL provided")

    docs_col = mongo_db["docs"]
    # Insert doc with status= 'pending'
    doc_insert = docs_col.insert_one({
        "owner": user_id,
        "raw_text": raw_text,
        "summary_text": None,
        "status": "pending",
        "created_at": datetime.utcnow()
    })
    doc_id = doc_insert.inserted_id

    # Upsert user_docs record
    user_docs_col = mongo_db["user_docs"]
    record = user_docs_col.find_one({"user_id": user_id})
    if not record:
        user_docs_col.insert_one({
            "user_id": user_id,
            "doc_ids": [str(doc_id)]
        })
    else:
        user_docs_col.update_one(
            {"user_id": user_id},
            {"$push": {"doc_ids": str(doc_id)}}
        )

    # Enqueue Celery task
    # run_summarization.delay(str(doc_id), raw_text)

    return {
        "doc_id": str(doc_id),
        "status": "queued"
    }

@router.get("/api/v1/docs/{doc_id}")
def get_doc(doc_id: str, creds: HTTPAuthorizationCredentials = Security(security)):
    # Validate user via Auth
    user_data = fetch_user_from_auth(creds.credentials)
    user_id = str(user_data.get("id", ""))
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")

    # Check doc ownership in user_docs
    user_docs_col = mongo_db["user_docs"]
    record = user_docs_col.find_one({"user_id": user_id})
    if not record or doc_id not in record.get("doc_ids", []):
        raise HTTPException(status_code=403, detail="Document not owned by user")

    docs_col = mongo_db["docs"]
    doc_obj = docs_col.find_one({"_id": ObjectId(doc_id)})
    if not doc_obj:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "raw_text": doc_obj.get("raw_text"),
        "summary_text": doc_obj.get("summary_text"),
        "status": doc_obj.get("status", "unknown")
    }
