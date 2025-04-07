from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Summiva"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/summiva")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://mongodb:27017/summiva")
    
    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # RabbitMQ settings
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
    
    # Search settings
    SOLR_URL: str = os.getenv("SOLR_URL", "http://solr:8983/solr/summiva")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()