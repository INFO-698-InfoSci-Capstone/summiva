from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Table
from sqlalchemy.sql import func
from core.database.database import Base

class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(BaseModel):
    """User model for authentication"""
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

class Document(BaseModel):
    """Base document model"""
    __tablename__ = "documents"
    
    title = Column(String, index=True)
    content = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))

class Tag(BaseModel):
    """Tag model for document tagging"""
    __tablename__ = "tags"
    
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)

# Association table for document-tag many-to-many relationship
document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class SearchIndex(BaseModel):
    """Search index model"""
    __tablename__ = "search_indices"
    
    document_id = Column(Integer, ForeignKey("documents.id"))
    vector = Column(Text)  # Store vectorized representation
    content = Column(Text)  # Store processed content for search

class Group(BaseModel):
    """Group model for document grouping"""
    __tablename__ = "groups"
    
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    algorithm = Column(String)  # Store which algorithm was used for grouping

class GroupMember(BaseModel):
    """Group member model for document-group relationship"""
    __tablename__ = "group_members"
    
    group_id = Column(Integer, ForeignKey("groups.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    similarity_score = Column(Float, nullable=True) 