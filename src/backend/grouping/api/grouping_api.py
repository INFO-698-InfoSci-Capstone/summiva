from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List

from src.database.session import get_db
from src.database.mongo_session import mongo_db
from src.models.group import Group, GroupMember, GroupingResult
from src.schemas.group import (
    GroupCreate, GroupUpdate, GroupInDB, GroupMemberInDB,
    GroupingRequest, GroupingResponse, GroupingResultInDB
)
from src.services.grouping import GroupingService
from core.dependencies import get_auth_client, get_document_client
from core.api.auth_client import AuthAPIClient
from core.api.document_client import DocumentAPIClient
from src.utils.security import get_authenticated_user_id
from ..models import DocumentGroup, GroupHistory
from ..schemas import DocumentGroupCreate, DocumentGroupResponse, GroupHistoryResponse
from backend.grouping.main import verify_token

router = APIRouter()
security = HTTPBearer()
grouping_service = GroupingService()

# ---------------- Helper functions ---------------- #

async def verify_user_token(token: str, auth_client: AuthAPIClient = Depends(get_auth_client)):
    await auth_client.verify_token(token)
    return token

def get_group_or_404(group_id: int, db: Session) -> Group:
    group = db.query(Group).filter(Group.id == group_id, Group.is_deleted == False).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

# ---------------- Routes ---------------- #

@router.post("/groups", response_model=GroupInDB)
async def create_group(group: GroupCreate, db: Session = Depends(get_db), token: str = Depends(verify_user_token)):
    db_group = Group(
        name=group.name,
        description=group.description,
        algorithm=group.algorithm,
        parameters=group.parameters,
        created_by=group.user_id
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/groups", response_model=List[GroupInDB])
async def list_groups(skip: int = 0, limit: int = 100, token: str = Depends(verify_user_token), db: Session = Depends(get_db)):
    """List all groups with pagination"""
    groups = db.query(Group).offset(skip).limit(limit).all()
    return groups


@router.post("/group", response_model=GroupingResponse)
async def group_documents(
    request: GroupingRequest,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client),
    document_client: DocumentAPIClient = Depends(get_document_client)
):
    await auth_client.verify_token(request.token)

    if not grouping_service.is_valid_algorithm(request.algorithm):
        raise HTTPException(status_code=400, detail=f"Invalid algorithm: {request.algorithm}")

    documents = []
    for doc_id in request.document_ids:
        doc = await document_client.get_document_content(doc_id)
        if not doc or 'content' not in doc:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found or has no content")
        documents.append({'id': doc_id, 'content': doc['content']})

    groups = await grouping_service.group_documents(documents, request.algorithm, request.parameters)
    if not groups:
        raise HTTPException(status_code=500, detail="Grouping failed")

    group = Group(
        name=f"Group {request.algorithm}",
        algorithm=request.algorithm,
        parameters=request.parameters,
        created_by=request.user_id
    )
    db.add(group)
    db.commit()

    for group_data in groups:
        for doc_id in group_data['document_ids']:
            db.add(GroupMember(group_id=group.id, document_id=doc_id, similarity_score=group_data.get('similarity_score')))

    db.commit()

    result = GroupingResult(
        group_id=group.id,
        document_count=len(request.document_ids),
        average_similarity=sum(g['similarity_score'] for g in groups) / len(groups),
        algorithm_metrics=groups[0].get('metrics', {}) if groups else {},
        created_by=request.user_id
    )
    db.add(result)
    db.commit()

    return GroupingResponse(
        group_id=group.id,
        document_count=result.document_count,
        average_similarity=result.average_similarity,
        algorithm_metrics=result.algorithm_metrics
    )

@router.get("/groups/{group_id}", response_model=GroupInDB)
async def get_group(group_id: int, token: str = Depends(verify_user_token), db: Session = Depends(get_db)):
    return get_group_or_404(group_id, db)

@router.get("/groups/{group_id}/members", response_model=List[GroupMemberInDB])
async def get_group_members(group_id: int, token: str = Depends(verify_user_token), db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    get_group_or_404(group_id, db)
    return db.query(GroupMember).filter(GroupMember.group_id == group_id).offset(offset).limit(limit).all()

@router.put("/groups/{group_id}", response_model=GroupInDB)
async def update_group(group_id: int, group_update: GroupUpdate, token: str = Depends(verify_user_token), db: Session = Depends(get_db)):
    group = get_group_or_404(group_id, db)
    for field, value in group_update.dict(exclude_unset=True).items():
        setattr(group, field, value)
    db.commit()
    db.refresh(group)
    return group

@router.delete("/groups/{group_id}")
async def delete_group(group_id: int, token: str = Depends(verify_user_token), db: Session = Depends(get_db)):
    group = get_group_or_404(group_id, db)
    db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
    db.delete(group)
    db.commit()
    return {"message": "Group deleted successfully"}

@router.get("/groups/{group_id}/similar", response_model=List[GroupInDB])
async def get_similar_groups(group_id: int, token: str = Depends(verify_user_token), limit: int = 5, db: Session = Depends(get_db)):
    return await grouping_service.find_similar_groups(group_id, limit)

@router.post("/groups/{group_id}/documents", response_model=DocumentGroupResponse)
async def add_document_to_group(group_id: int, document_group: DocumentGroupCreate, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    get_group_or_404(group_id, db)
    existing = db.query(DocumentGroup).filter(DocumentGroup.group_id == group_id, DocumentGroup.document_id == document_group.document_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Document already in group")

    db_document_group = DocumentGroup(group_id=group_id, document_id=document_group.document_id, added_by=user_id)
    db.add(db_document_group)
    db.commit()
    db.refresh(db_document_group)
    return db_document_group

@router.delete("/groups/{group_id}/documents/{document_id}")
async def remove_document_from_group(group_id: int, document_id: int, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    doc_group = db.query(DocumentGroup).filter(DocumentGroup.group_id == group_id, DocumentGroup.document_id == document_id).first()
    if not doc_group:
        raise HTTPException(status_code=404, detail="Document not found in group")

    db.delete(doc_group)
    db.commit()
    return {"message": "Document removed from group successfully"}

@router.get("/groups/{group_id}/documents", response_model=List[DocumentGroupResponse])
async def get_group_documents(group_id: int, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    get_group_or_404(group_id, db)
    return db.query(DocumentGroup).filter(DocumentGroup.group_id == group_id).all()

@router.get("/documents/{document_id}/groups", response_model=List[GroupInDB])
async def get_document_groups(document_id: int, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    return db.query(Group).join(DocumentGroup).filter(DocumentGroup.document_id == document_id, Group.is_deleted == False).all()

@router.get("/groups/{group_id}/history", response_model=List[GroupHistoryResponse])
async def get_group_history(group_id: int, db: Session = Depends(get_db), user_id: int = Depends(verify_token)):
    get_group_or_404(group_id, db)
    return db.query(GroupHistory).filter(GroupHistory.group_id == group_id).order_by(GroupHistory.created_at.desc()).all()

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


@router.get("/grouping-results", response_model=List[GroupingResultInDB])
async def list_grouping_results(skip: int = 0, limit: int = 100, token: str = Depends(verify_user_token), db: Session = Depends(get_db)):
    """List all grouping results"""
    results = db.query(GroupingResult).offset(skip).limit(limit).all()
    return results

@router.get("/grouping-results/{result_id}", response_model=GroupingResultInDB)
async def get_grouping_result(result_id: int, token: str = Depends(verify_user_token), db: Session = Depends(get_db)):
    """Get specific grouping result"""
    result = db.query(GroupingResult).filter(GroupingResult.id == result_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Grouping result not found")
    return result