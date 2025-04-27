from backend.core.models.base import BaseModel
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Tag(BaseModel):
    __tablename__ = "tags"

    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    user_id = Column(String, nullable=True)  # Creator's user_id

    tagged_documents = relationship("TaggedDocument", back_populates="tag", cascade="all, delete-orphan")

class TaggedDocument(BaseModel):
    __tablename__ = "tagged_documents"

    document_id = Column(String, index=True)  # Reference to document service
    tag_id = Column(Integer, ForeignKey("tags.id"))
    confidence_score = Column(Float, nullable=True)

    tag = relationship("Tag", back_populates="tagged_documents")

class TaggingHistory(BaseModel):
    __tablename__ = "tagging_history"

    document_id = Column(String, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"))
    action = Column(String)  # "add", "remove", "update"
    user_id = Column(String)
