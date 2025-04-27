from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class TagBase(BaseModel):
    name: str
    description: Optional[str] = None

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    name: Optional[str] = None

class TagInDB(TagBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class TaggedDocumentBase(BaseModel):
    document_id: int
    tag_id: int
    confidence_score: int

class TaggedDocumentCreate(TaggedDocumentBase):
    pass

class TaggedDocumentUpdate(TaggedDocumentBase):
    confidence_score: Optional[int] = None

class TaggedDocumentInDB(TaggedDocumentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class TaggingRequest(BaseModel):
    text: str
    max_tags: Optional[int] = 5
    min_confidence: Optional[int] = 70

class TaggingResponse(BaseModel):
    tags: List[dict]
    processing_time: float 