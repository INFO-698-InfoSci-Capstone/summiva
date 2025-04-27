from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class SearchIndexBase(BaseModel):
    document_id: int
    content: str
    vector: str

class SearchIndexCreate(SearchIndexBase):
    pass

class SearchIndexUpdate(SearchIndexBase):
    content: Optional[str] = None
    vector: Optional[str] = None

class SearchIndexInDB(SearchIndexBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class SearchHistoryBase(BaseModel):
    query: str
    results_count: int

class SearchHistoryCreate(SearchHistoryBase):
    pass

class SearchHistoryInDB(SearchHistoryBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SearchResultBase(BaseModel):
    search_id: int
    document_id: int
    relevance_score: float

class SearchResultCreate(SearchResultBase):
    pass

class SearchResultInDB(SearchResultBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class SearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10
    min_relevance: Optional[float] = 0.5

class SearchResponse(BaseModel):
    results: List[dict]
    total_results: int
    processing_time: float 