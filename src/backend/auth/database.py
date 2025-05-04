from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Create database engine
engine = create_engine(\
    settings.POSTGRES_DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()