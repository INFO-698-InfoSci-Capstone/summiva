from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.backend.core.database.database import Base

class DocumentTag(Base):
    __tablename__ = "document_tags"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    tag_id = Column(Integer, ForeignKey("tags.id"))

    document = relationship("Document", back_populates="document_tags")
    tag = relationship("Tag", back_populates="document_tags")