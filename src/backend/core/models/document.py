from backend.core.models.base import BaseModel
from sqlalchemy import Column, String, Text

class Document(BaseModel):
    __tablename__ = "documents"

    user_id = Column(String, index=True)  # Reference to auth service
    title = Column(String, index=True)
    content = Column(Text)
