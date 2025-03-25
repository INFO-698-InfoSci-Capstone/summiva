from fastapi import APIRouter, Security, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.utils.security import get_authenticated_user_id
from src.database.mongo_session import mongo_db

router = APIRouter()
security = HTTPBearer()

@router.get("/api/v1/groups")
def list_groups(creds: HTTPAuthorizationCredentials = Security(security)):
    user_id = get_authenticated_user_id(creds)

    docs = mongo_db["docs"].find({"owner": user_id})
    group_map = {}
    for doc in docs:
        gid = doc.get("group_id", "unassigned")
        group_map.setdefault(gid, []).append({
            "doc_id": str(doc["_id"]),
            "title": doc.get("title", "Untitled"),
            "summary": doc.get("summary_text", "")
        })
    return {"groups": group_map}