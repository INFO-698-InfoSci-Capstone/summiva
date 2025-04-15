from pydantic_settings import BaseSettings
from typing import Optional

class BaseConfig(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Summiva"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/summiva"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Model Settings
    MODEL_CACHE_DIR: str = "models/cache"
    MODEL_DOWNLOAD_DIR: str = "models/downloads"
    
    # Monitoring
    ENABLE_MONITORING: bool = False
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3000
    
    class Config:
        env_file = ".env"
        case_sensitive = True 