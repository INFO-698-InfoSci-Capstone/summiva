from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Function to create tables
def init_db():
    from src.models.user import User  # Ensure the model is imported
    Base.metadata.create_all(bind=engine)

# Run DB Initialization at Startup (optional)
init_db()
