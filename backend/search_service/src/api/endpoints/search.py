from fastapi import APIRouter, Query, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.utils.security import get_authenticated_user_id
from src.core.elastic_client import keyword_search
from src.core.faiss_index import semantic_search
from src.database.mongo_session import mongo_db

router = APIRouter()
security = HTTPBearer()

@router.get("/api/v1/search")
def search(
    q: str = Query(...),
    semantic: bool = False,
    creds: HTTPAuthorizationCredentials = Security(security)
):
    user_id = get_authenticated_user_id(creds)

    keyword_results = keyword_search(q)
    semantic_results = semantic_search(q) if semantic else []

    merged = {res["doc_id"]: res for res in keyword_results}
    for res in semantic_results:
        if res["doc_id"] in merged:
            merged[res["doc_id"]]["score"] += res["score"]
        else:
            merged[res["doc_id"]] = res

    # Enrich results from Mongo
    docs_col = mongo_db["docs"]
    hydrated = []
    for doc_id, res in merged.items():
        doc = docs_col.find_one({"_id": doc_id, "owner": user_id})
        if not doc:
            continue
        hydrated.append({
            "doc_id": doc_id,
            "title": doc.get("title", "Untitled"),
            "summary": doc.get("summary_text", ""),
            "tags": doc.get("tags", {}),
            "group_id": doc.get("group_id", None),
            "score": res["score"]
        })

    # Sort by score descending
    sorted_results = sorted(hydrated, key=lambda x: x["score"], reverse=True)
    return {"query": q, "results": sorted_results[:10]}
