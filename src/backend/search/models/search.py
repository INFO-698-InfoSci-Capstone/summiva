from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from src.database.session import Base

class SearchIndex(Base):
    """Search index model for search service"""
    __tablename__ = "search_indices"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, index=True)  # Reference to document service
    vector = Column(Text)  # Store vectorized representation
    content = Column(Text)  # Store processed content for search
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class SearchHistory(Base):
    """Search history model for search service"""
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Reference to auth service
    query = Column(Text)
    results_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SearchResult(Base):
    """Search result model for search service"""
    __tablename__ = "search_results"
    
    id = Column(Integer, primary_key=True, index=True)
    search_id = Column(Integer, ForeignKey("search_history.id"))
    document_id = Column(String, index=True)  # Reference to document service
    relevance_score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 