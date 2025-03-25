from fastapi import APIRouter, Depends, Security, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from bson import ObjectId
from src.utils.security import get_authenticated_user_id
from src.database.mongo_session import mongo_db

router = APIRouter()
security = HTTPBearer()

@router.get("/api/v1/documents/{doc_id}/tags")
def get_tags(doc_id: str, creds: HTTPAuthorizationCredentials = Security(security)):
    user_id = get_authenticated_user_id(creds)
    user_docs = mongo_db["user_docs"].find_one({"user_id": user_id})
    if not user_docs or doc_id not in user_docs.get("doc_ids", []):
        raise HTTPException(status_code=403, detail="Unauthorized")

    doc = mongo_db["docs"].find_one({"_id": ObjectId(doc_id)}, {"tags": 1})
    if not doc or "tags" not in doc:
        raise HTTPException(status_code=404, detail="Tags not found")

    return doc["tags"]
