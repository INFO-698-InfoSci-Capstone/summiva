from sqlalchemy import Column, Integer, String, Text, DateTime, Table, ForeignKey, Float
from sqlalchemy.sql import func
from src.database.session import Base

class Tag(Base):
    """Tag model for tagging service"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TaggedDocument(Base):
    """Tagged document model for document-tag relationship"""
    __tablename__ = "tagged_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, index=True)  # Reference to document service
    tag_id = Column(Integer, ForeignKey("tags.id"))
    confidence_score = Column(Float, nullable=True)  # For ML-based tagging
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String)  # Reference to auth service user_id

class TaggingHistory(Base):
    """Tagging history model for audit trail"""
    __tablename__ = "tagging_history"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, index=True)  # Reference to document service
    tag_id = Column(Integer, ForeignKey("tags.id"))
    action = Column(String)  # add, remove, update
    user_id = Column(String)  # Reference to auth service
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 