from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config.settings.settings import settings

# Get environment-specific database connection parameters
def get_db_config():
    """Get database connection parameters based on environment"""
    # Basic config present in all environments
    db_config = {
        'pool_pre_ping': True,
        'pool_recycle': 1800,
    }
    
    # Environment-specific configurations
    if settings.ENVIRONMENT == "production":
        db_config.update({
            'pool_size': 20,
            'max_overflow': 40,
            'pool_timeout': 60,
        })
    elif settings.ENVIRONMENT == "staging":
        db_config.update({
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 45,
        })
    else:  # development and testing
        db_config.update({
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
        })
        
    return db_config

# Create SQLAlchemy engine with environment-specific configuration
engine = create_engine(
    str(settings.DATABASE_URL),
    **get_db_config()
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database with all models"""
    Base.metadata.create_all(bind=engine)