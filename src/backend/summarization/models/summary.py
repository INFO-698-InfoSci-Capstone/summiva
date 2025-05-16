from src.backend.core.models.base import BaseModel
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime

class Document(BaseModel):
    __tablename__ = "documents"

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(ARRAY(String), nullable=True, default=[])
    user_id = Column(Integer, nullable=False, index=True)
    
    # Relationship with summaries (one document can have multiple summaries)
    summaries = relationship("Summary", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', user_id={self.user_id})>"

class Summary(BaseModel):
    __tablename__ = "summaries"

    document_id = Column(Integer, ForeignKey("documents.id"), index=True)
    content = Column(Text)
    length = Column(Integer)
    model = Column(String, default="t5-small")
    
    # Relationship with document (each summary belongs to one document)
    document = relationship("Document", back_populates="summaries")
