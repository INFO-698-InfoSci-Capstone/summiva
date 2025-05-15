from src.backend.core.models.base import BaseModel
from sqlalchemy import Column, Integer, String, Text, Float

class SearchIndex(BaseModel):
    __tablename__ = "search_indices"

    document_id = Column(String, index=True)  # Reference to document service
    vector = Column(Text)
    content = Column(Text)

class SearchHistory(BaseModel):
    __tablename__ = "search_history"

    user_id = Column(String, index=True)  # Reference to auth service
    query = Column(Text)
    results_count = Column(Integer)

class SearchResult(BaseModel):
    __tablename__ = "search_results"

    search_id = Column(Integer, index=True)  # Reference to search_history
    document_id = Column(String, index=True)
    relevance_score = Column(Float)
