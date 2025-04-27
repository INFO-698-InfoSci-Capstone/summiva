from backend.core.models.base import BaseModel
from sqlalchemy import Column, Integer, String, Text, Float, JSON

class Group(BaseModel):
    __tablename__ = "groups"

    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    algorithm = Column(String)
    parameters = Column(JSON)

class GroupMember(BaseModel):
    __tablename__ = "group_members"

    group_id = Column(Integer, index=True)
    document_id = Column(String, index=True)
    similarity_score = Column(Float, nullable=True)

class GroupingResult(BaseModel):
    __tablename__ = "grouping_results"

    group_id = Column(Integer, index=True)
    document_count = Column(Integer)
    average_similarity = Column(Float)
    algorithm_metrics = Column(JSON)