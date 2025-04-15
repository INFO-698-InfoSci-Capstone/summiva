from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class DocumentBase(BaseModel):
    title: str
    content: str

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    title: Optional[str] = None
    content: Optional[str] = None

class DocumentInDB(DocumentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class SummaryBase(BaseModel):
    content: str
    length: int

class SummaryCreate(SummaryBase):
    document_id: int

class SummaryInDB(SummaryBase):
    id: int
    document_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SummarizationRequest(BaseModel):
    text: str
    max_length: Optional[int] = 150
    min_length: Optional[int] = 30

class SummarizationResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float 