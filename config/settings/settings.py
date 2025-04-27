import os
import yaml
from typing import Any, Dict
from pydantic import BaseSettings, PostgresDsn, RedisDsn, AnyUrl
from utils.paths import path_manager

class Settings(BaseSettings):
    # --- Environment ---
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # --- Application ---
    APP_NAME: str = "Summiva"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Summiva"
    APP_SERVICE_NAME: str = "backend"
    APP_SERVICE_VERSION: str = "1.0.0"

    # --- Security ---
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUTH_PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    AUTH_PASSWORD_SALT_ROUNDS: int = 12

    # --- Database ---
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    DATABASE_URL: PostgresDsn = None

    # --- Redis and Celery ---
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_URL: RedisDsn = None

    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # --- AWS S3 ---
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str

    # --- Service URLs ---
    SUMMARIZATION_SERVICE_URL: AnyUrl
    TAGGING_SERVICE_URL: AnyUrl
    SEARCH_SERVICE_URL: AnyUrl
    GROUPING_SERVICE_URL: AnyUrl
    AUTH_SERVICE_URL: AnyUrl

    # --- Search Services ---
    ELASTIC_URL: AnyUrl
    SOLR_HOST: str
    SOLR_PORT: int
    FAISS_INDEX_PATH: str

    # --- AI Model Config ---
    MODEL_PATH: str
    MODEL_DEVICE: str
    BATCH_SIZE: int

    # --- Monitoring ---
    ENABLE_MONITORING: bool = False
    PROMETHEUS_PORT: int
    GRAFANA_PORT: int

    # --- Local Paths (loaded dynamically) ---
    DATA_DIR: str = ""
    MODELS_DIR: str = ""
    LOGS_DIR: str = ""
    MODEL_CACHE_DIR: str = ""
    MODEL_DOWNLOAD_DIR: str = ""
    FAISS_DOC_MAP_PATH: str = ""
    LOG_FILE: str = ""
    ERROR_LOG_FILE: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

    def assemble_urls(self):
        """If DATABASE_URL or REDIS_URL is missing, assemble from parts."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if not self.REDIS_URL:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def load_yaml_configs(self):
        """Load additional path configs from YAML."""
        config_path = path_manager.get_path('settings.yaml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"YAML config file not found at {config_path}")

        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)

        # Setup paths
        self.DATA_DIR = path_manager.ensure_dir('data')
        self.MODELS_DIR = path_manager.ensure_dir('models')
        self.LOGS_DIR = path_manager.ensure_dir('logs')
        self.MODEL_CACHE_DIR = path_manager.ensure_dir('models', 'cache')
        self.MODEL_DOWNLOAD_DIR = path_manager.ensure_dir('models', 'downloads')

        # FAISS and DOC map paths
        self.FAISS_DOC_MAP_PATH = path_manager.get_path(yaml_config.get('faiss_doc_map_path', 'models/doc_map.json'))

        # Logs
        self.LOG_FILE = path_manager.get_path('logs', 'app.log')
        self.ERROR_LOG_FILE = path_manager.get_path('logs', 'error.log')

        # Debug mode switch
        if self.ENVIRONMENT == "production":
            self.DEBUG = False
        else:
            self.DEBUG = True

# Instantiate and initialize
settings = Settings()
settings.assemble_urls()
settings.load_yaml_configs()
