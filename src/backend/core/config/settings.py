import os
import yaml
from typing import Dict, Any
from pydantic import BaseSettings, PostgresDsn, RedisDsn
from utils.paths import path_manager

class Settings(BaseSettings):
    # --- Application ---
    APP_NAME: str = "Summiva"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # --- Database ---
    DATABASE_URL: PostgresDsn
    
    # --- Redis ---
    REDIS_URL: RedisDsn
    
    # --- JWT Authentication ---
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUTH_REFRESH_TOKEN_EXPIRE_MINUTES: int = 30
    
    # --- AWS ---
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str
    
    # --- Services ---
    SUMMARIZATION_SERVICE_URL: str
    TAGGING_SERVICE_URL: str
    SEARCH_SERVICE_URL: str
    GROUPING_SERVICE_URL: str
    
    # --- Celery ---
    CELERY_BROKER_URL: RedisDsn
    CELERY_RESULT_BACKEND: RedisDsn

    # --- Paths loaded from YAML ---
    DATA_DIR: str = ""
    MODELS_DIR: str = ""
    LOGS_DIR: str = ""
    MODEL_DOWNLOAD_DIR: str = ""
    FAISS_INDEX_PATH: str = ""
    FAISS_DOC_MAP_PATH: str = ""
    LOG_FILE: str = ""
    ERROR_LOG_FILE: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

    def load_yaml_configs(self):
        """Load additional config values from YAML file."""
        config_path = path_manager.get_path('config', 'settings.yaml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"YAML config file not found at {config_path}")

        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)

        # Setup and ensure required directories
        self.DATA_DIR = path_manager.ensure_dir('data')
        self.MODELS_DIR = path_manager.ensure_dir('models')
        self.LOGS_DIR = path_manager.ensure_dir('logs')
        self.MODEL_DOWNLOAD_DIR = path_manager.ensure_dir('models', 'downloads')
        
        # Specific paths from YAML
        self.FAISS_INDEX_PATH = path_manager.get_path(yaml_config.get('faiss_index_path', 'models/faiss.index'))
        self.FAISS_DOC_MAP_PATH = path_manager.get_path(yaml_config.get('faiss_doc_map_path', 'models/doc_map.json'))

        # Log files
        self.LOG_FILE = path_manager.get_path('logs', 'app.log')
        self.ERROR_LOG_FILE = path_manager.get_path('logs', 'error.log')


# Global settings instance
settings = Settings()
settings.load_yaml_configs()
