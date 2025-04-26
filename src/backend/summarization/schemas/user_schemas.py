from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Literal
from enum import Enum

# ------------------------
# Summarization Model Enum
# ------------------------


class ModelType(str, Enum):
    t5_small = "t5-small"
    bart_base = "bart-base"
    gpt_summary = "gpt-summary"
    custom_light = "custom-light"


# ------------------------
# Document Models
# ------------------------


class DocumentBase(BaseModel):
    title: str = Field(..., example="AI in Healthcare")
    content: str = Field(..., example="Full document content...")
    tags: Optional[List[str]] = Field(
        default_factory=list, example=["AI", "Medical", "2025"]
    )


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class DocumentInDB(DocumentBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# ------------------------
# Summary Models
# ------------------------


class SummaryBase(BaseModel):
    content: str
    length: int


class SummaryCreate(SummaryBase):
    document_id: int
    model: Optional[ModelType] = ModelType.t5_small


class SummaryInDB(SummaryBase):
    id: int
    document_id: int
    created_at: datetime
    model: Optional[ModelType]

    class Config:
        orm_mode = True


# ------------------------
# Summarization Workflow
# ------------------------


class SummarizationRequest(BaseModel):
    text: str = Field(..., example="Text to summarize goes here...")
    url: Optional[HttpUrl] = Field(
        None, example="https://example.com/article-to-summarize"
    )
    max_length: Optional[int] = Field(150, example=150)
    min_length: Optional[int] = Field(30, example=30)
    model: Optional[ModelType] = ModelType.t5_small


class SummarizationResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    status: Optional[str] = "success"


# ------------------------
# Pagination & Filtering
# ------------------------


class Pagination(BaseModel):
    page: int = Field(1, ge=1, example=1)
    limit: int = Field(10, ge=1, le=100, example=10)


class DocumentFilter(Pagination):
    tag: Optional[str] = Field(None, example="AI")
    title_contains: Optional[str] = Field(None, example="healthcare")


class SummaryFilter(Pagination):
    document_id: Optional[int] = None
    model: Optional[ModelType] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    status: Optional[Literal["pending", "completed", "failed"]] = None
    # Add more filters as needed
