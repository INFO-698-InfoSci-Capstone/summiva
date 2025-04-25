from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.backend.core.config.settings import settings

# Create SQLAlchemy engine for auth service
engine = create_engine(
    settings.AUTH_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for auth models
Base = declarative_base()

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize auth database tables"""
    Base.metadata.create_all(bind=engine)

# Run DB Initialization at Startup (optional)
init_db()
