from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Search settings
    ELASTICSEARCH_URL: str
    ELASTICSEARCH_INDEX: str = "documents"
    ELASTICSEARCH_TIMEOUT: int = 30
    
    # Search algorithm settings
    SIMILARITY_THRESHOLD: float = 0.7
    MAX_RESULTS: int = 100
    FUZZY_SEARCH_ENABLED: bool = True
    
    # Service settings
    SERVICE_NAME: str = "search"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 