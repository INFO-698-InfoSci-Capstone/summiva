from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database.database import get_db
from .models import Group, GroupMember, GroupingResult
from .schemas import (
    GroupCreate, GroupUpdate, GroupInDB,
    GroupMemberInDB, GroupingRequest, GroupingResponse,
    GroupingResultInDB
)
from .services import GroupingService

router = APIRouter(prefix="/grouping", tags=["grouping"])

@router.post("/group", response_model=GroupInDB)
def create_group(
    group: GroupCreate,
    db: Session = Depends(get_db)
):
    """Create a new group."""
    db_group = Group(**group.dict())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/groups", response_model=List[GroupInDB])
def list_groups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all groups."""
    groups = db.query(Group).offset(skip).limit(limit).all()
    return groups

@router.get("/groups/{group_id}", response_model=GroupInDB)
def get_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific group by ID."""
    group = db.query(Group).filter(Group.id == group_id).first()
    if group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/groups/{group_id}", response_model=GroupInDB)
def update_group(
    group_id: int,
    group_update: GroupUpdate,
    db: Session = Depends(get_db)
):
    """Update a group."""
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    for field, value in group_update.dict(exclude_unset=True).items():
        setattr(db_group, field, value)
    
    db.commit()
    db.refresh(db_group)
    return db_group

@router.delete("/groups/{group_id}")
def delete_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Delete a group and its members."""
    db_group = db.query(Group).filter(Group.id == group_id).first()
    if db_group is None:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Delete all group members first
    db.query(GroupMember).filter(GroupMember.group_id == group_id).delete()
    db.delete(db_group)
    db.commit()
    return {"message": "Group deleted successfully"}

@router.get("/groups/{group_id}/members", response_model=List[GroupMemberInDB])
def list_group_members(
    group_id: int,
    db: Session = Depends(get_db)
):
    """List all members of a group."""
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    return members

@router.post("/group-documents", response_model=GroupingResponse)
def group_documents(
    request: GroupingRequest,
    db: Session = Depends(get_db)
):
    """Group documents using the specified algorithm."""
    grouping_service = GroupingService(db)
    return grouping_service.group_documents(request)

@router.get("/grouping-results", response_model=List[GroupingResultInDB])
def list_grouping_results(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all grouping results."""
    results = db.query(GroupingResult).offset(skip).limit(limit).all()
    return results

@router.get("/grouping-results/{result_id}", response_model=GroupingResultInDB)
def get_grouping_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific grouping result by ID."""
    result = db.query(GroupingResult).filter(GroupingResult.id == result_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Grouping result not found")
    return result 