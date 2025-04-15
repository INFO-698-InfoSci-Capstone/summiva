from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from src.database.session import get_db
from src.models.group import Group, GroupMember, GroupingResult
from src.schemas.group import (
    GroupCreate,
    GroupUpdate,
    GroupInDB,
    GroupMemberInDB,
    GroupingRequest,
    GroupingResponse,
    GroupingResultInDB
)
from src.services.grouping import GroupingService
from core.dependencies import get_auth_client, get_document_client
from core.api.auth_client import AuthAPIClient
from core.api.document_client import DocumentAPIClient
from ..database import get_db
from ..models import DocumentGroup, GroupHistory
from ..schemas import (
    DocumentGroupCreate, DocumentGroupResponse,
    GroupHistoryResponse
)
from ..auth import verify_token

router = APIRouter()
grouping_service = GroupingService()

@router.post("/groups", response_model=GroupInDB)
async def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Create a new document group"""
    try:
        # Verify user token
        await auth_client.verify_token(group.token)
        
        # Create group
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/group", response_model=GroupingResponse)
async def group_documents(
    request: GroupingRequest,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client),
    document_client: DocumentAPIClient = Depends(get_document_client)
):
    """Group documents using specified algorithm"""
    try:
        # Verify user token
        await auth_client.verify_token(request.token)
        
        # Validate algorithm
        if not grouping_service.is_valid_algorithm(request.algorithm):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid algorithm: {request.algorithm}"
            )
        
        # Get document contents
        documents = []
        for doc_id in request.document_ids:
            try:
                doc = await document_client.get_document_content(doc_id)
                if not doc or 'content' not in doc:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Document {doc_id} not found or has no content"
                    )
                documents.append({
                    'id': doc_id,
                    'content': doc['content']
                })
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error fetching document {doc_id}: {str(e)}"
                )
        
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid documents found to group"
            )
        
        # Perform grouping
        groups = await grouping_service.group_documents(
            documents=documents,
            algorithm=request.algorithm,
            parameters=request.parameters
        )
        
        if not groups:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Grouping algorithm failed to produce results"
            )
        
        # Create group and members
        group = Group(
            name=f"Group {request.algorithm}",
            algorithm=request.algorithm,
            parameters=request.parameters,
            created_by=request.user_id
        )
        db.add(group)
        db.commit()
        
        # Create group members
        for group_data in groups:
            for doc_id in group_data['document_ids']:
                member = GroupMember(
                    group_id=group.id,
                    document_id=doc_id,
                    similarity_score=group_data.get('similarity_score')
                )
                db.add(member)
        
        db.commit()
        
        # Create grouping result
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/groups/{group_id}", response_model=GroupInDB)
async def get_group(
    group_id: int,
    token: str,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Get group details"""
    try:
        # Verify user token
        await auth_client.verify_token(token)
        
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        return group
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/groups/{group_id}/members", response_model=List[GroupMemberInDB])
async def get_group_members(
    group_id: int,
    token: str,
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Get documents in a group"""
    try:
        # Verify user token
        await auth_client.verify_token(token)
        
        members = db.query(GroupMember)\
            .filter(GroupMember.group_id == group_id)\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return members
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/groups/{group_id}", response_model=GroupInDB)
async def update_group(
    group_id: int,
    group_update: GroupUpdate,
    token: str,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Update group details"""
    try:
        # Verify user token
        await auth_client.verify_token(token)
        
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        for field, value in group_update.dict(exclude_unset=True).items():
            setattr(group, field, value)
        
        db.commit()
        db.refresh(group)
        
        return group
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: int,
    token: str,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Delete a group"""
    try:
        # Verify user token
        await auth_client.verify_token(token)
        
        group = db.query(Group).filter(Group.id == group_id).first()
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Delete group members
        db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
        
        # Delete group
        db.delete(group)
        db.commit()
        
        return {"message": "Group deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/groups/{group_id}/similar", response_model=List[GroupInDB])
async def get_similar_groups(
    group_id: int,
    token: str,
    limit: int = 5,
    db: Session = Depends(get_db),
    auth_client: AuthAPIClient = Depends(get_auth_client)
):
    """Get similar groups based on content"""
    try:
        # Verify user token
        await auth_client.verify_token(token)
        
        similar_groups = await grouping_service.find_similar_groups(
            group_id=group_id,
            limit=limit
        )
        
        return similar_groups
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/groups/{group_id}/documents", response_model=DocumentGroupResponse)
async def add_document_to_group(
    group_id: int,
    document_group: DocumentGroupCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    # Verify group exists
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.is_deleted == False
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if document is already in group
    existing = db.query(DocumentGroup).filter(
        DocumentGroup.group_id == group_id,
        DocumentGroup.document_id == document_group.document_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Document already in group")
    
    db_document_group = DocumentGroup(
        group_id=group_id,
        document_id=document_group.document_id,
        added_by=user_id
    )
    db.add(db_document_group)
    db.commit()
    db.refresh(db_document_group)
    return db_document_group

@router.delete("/groups/{group_id}/documents/{document_id}")
async def remove_document_from_group(
    group_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    document_group = db.query(DocumentGroup).filter(
        DocumentGroup.group_id == group_id,
        DocumentGroup.document_id == document_id
    ).first()
    if not document_group:
        raise HTTPException(status_code=404, detail="Document not found in group")
    
    db.delete(document_group)
    db.commit()
    return {"message": "Document removed from group successfully"}

@router.get("/groups/{group_id}/documents", response_model=List[DocumentGroupResponse])
async def get_group_documents(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.is_deleted == False
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    document_groups = db.query(DocumentGroup).filter(
        DocumentGroup.group_id == group_id
    ).all()
    return document_groups

@router.get("/documents/{document_id}/groups", response_model=List[GroupInDB])
async def get_document_groups(
    document_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    groups = db.query(Group).join(DocumentGroup).filter(
        DocumentGroup.document_id == document_id,
        Group.is_deleted == False
    ).all()
    return groups

@router.get("/groups/{group_id}/history", response_model=List[GroupHistoryResponse])
async def get_group_history(
    group_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(verify_token)
):
    group = db.query(Group).filter(
        Group.id == group_id,
        Group.is_deleted == False
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    history = db.query(GroupHistory).filter(
        GroupHistory.group_id == group_id
    ).order_by(GroupHistory.created_at.desc()).all()
    return history 