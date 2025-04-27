from backend.core.models.base import BaseModel
from sqlalchemy import Column, Integer, String, Text

class Summary(BaseModel):
    __tablename__ = "summaries"

    document_id = Column(String, index=True)  # Reference to document service
    content = Column(Text)
    length = Column(Integer)
    model = Column(String, default="t5-small")
