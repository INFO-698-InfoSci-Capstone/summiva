from config.settings import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from elasticsearch import AsyncElasticsearch

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Create Elasticsearch client
# The 'timeout' parameter has been removed in newer versions of the AsyncElasticsearch client
es_client = AsyncElasticsearch(
    hosts=[settings.ELASTICSEARCH_URL]
)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_es():
    """Get Elasticsearch client with timeout configuration"""
    # In newer versions, timeout is applied via the options method
    return es_client.options(
        request_timeout=settings.ELASTICSEARCH_TIMEOUT
    )