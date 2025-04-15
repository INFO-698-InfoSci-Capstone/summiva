from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from src.database.session import Base

class Group(Base):
    """Group model for grouping service"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    algorithm = Column(String)  # Store which algorithm was used for grouping
    parameters = Column(JSON)  # Store algorithm-specific parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String)  # Reference to auth service user_id

class GroupMember(Base):
    """Group member model for document-group relationship"""
    __tablename__ = "group_members"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    document_id = Column(String, index=True)  # Reference to document service
    similarity_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class GroupingResult(Base):
    """Grouping result model for storing grouping operations"""
    __tablename__ = "grouping_results"
    
    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    document_count = Column(Integer)
    average_similarity = Column(Float)
    algorithm_metrics = Column(JSON)  # Store algorithm-specific metrics
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String)  # Reference to auth service user_id 