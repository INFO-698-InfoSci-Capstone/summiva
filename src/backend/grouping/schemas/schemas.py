from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupCreate(GroupBase):
    pass

class GroupUpdate(GroupBase):
    name: Optional[str] = None

class GroupInDB(GroupBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class GroupMemberBase(BaseModel):
    document_id: int
    similarity_score: float

class GroupMemberCreate(GroupMemberBase):
    group_id: int

class GroupMemberInDB(GroupMemberBase):
    id: int
    group_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class GroupingResultBase(BaseModel):
    algorithm: str
    parameters: Dict[str, Any]

class GroupingResultCreate(GroupingResultBase):
    pass

class GroupingResultInDB(GroupingResultBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class GroupingRequest(BaseModel):
    algorithm: str
    parameters: Dict[str, Any]
    document_ids: List[int]

class GroupingResponse(BaseModel):
    groups: List[GroupInDB]
    members: List[GroupMemberInDB]
    processing_time: float 