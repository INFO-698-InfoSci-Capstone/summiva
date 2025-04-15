from utils.paths import path_manager
import os
from typing import Dict, Any
import yaml
from pydantic import BaseSettings, PostgresDsn, RedisDsn

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Summiva"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: PostgresDsn
    
    # Redis
    REDIS_URL: RedisDsn
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str
    
    # Services
    SUMMARIZATION_SERVICE_URL: str
    TAGGING_SERVICE_URL: str
    SEARCH_SERVICE_URL: str
    GROUPING_SERVICE_URL: str
    
    # Celery
    CELERY_BROKER_URL: RedisDsn
    CELERY_RESULT_BACKEND: RedisDsn
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    env_file = f".env.{env}"
    
    if os.path.exists(env_file):
        os.environ["ENV_FILE"] = env_file
    
    return Settings()

settings = get_settings()

class Settings:
    def __init__(self):
        self.config = self._load_config()
        self._setup_paths()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML files."""
        config_path = path_manager.get_path('config', 'settings.yaml')
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _setup_paths(self):
        """Setup and ensure all required paths exist."""
        # Data paths
        self.DATA_DIR = path_manager.ensure_dir('data')
        self.MODELS_DIR = path_manager.ensure_dir('models')
        self.LOGS_DIR = path_manager.ensure_dir('logs')
        
        # Model paths
        self.MODEL_DOWNLOAD_DIR = path_manager.ensure_dir('models/downloads')
        self.FAISS_INDEX_PATH = path_manager.get_path(self.config['faiss_index_path'])
        self.FAISS_DOC_MAP_PATH = path_manager.get_path(self.config['faiss_doc_map_path'])
        
        # Log paths
        self.LOG_FILE = path_manager.get_path('logs', 'app.log')
        self.ERROR_LOG_FILE = path_manager.get_path('logs', 'error.log')

# Global settings instance
settings = Settings() 