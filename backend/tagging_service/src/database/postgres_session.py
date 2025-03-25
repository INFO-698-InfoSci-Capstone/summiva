from sqlalchemy import create_engine, Column, String, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.config import settings
import datetime

Base = declarative_base()

class Tags(Base):
    __tablename__ = "tags"
    doc_id = Column(String, primary_key=True)
    entities = Column(ARRAY(String))
    topics = Column(ARRAY(String))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

engine = create_engine(settings.POSTGRES_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_pg_session():
    return SessionLocal()
