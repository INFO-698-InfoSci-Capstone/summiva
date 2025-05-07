from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.backend.auth.config import settings

# Create database engine
engine = create_engine(
    settings.POSTGRES_DATABASE_URL,
    pool_size=settings.POSTGRES_DATABASE_POOL_SIZE,
    max_overflow=settings.POSTGRES_DATABASE_MAX_OVERFLOW
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 