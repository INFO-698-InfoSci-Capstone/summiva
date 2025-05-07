import os
from typing import Any, Dict, List

# Simple settings class that reads from environment variables
class Settings:
    # --- Environment ---
    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
    DEBUG: bool = os.environ.get("DEBUG", "True") == "True"
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    # --- Application ---
    APP_NAME: str = os.environ.get("APP_NAME", "Summiva")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Summiva"
    APP_SERVICE_NAME: str = os.environ.get("SERVICE_NAME", "backend")
    APP_SERVICE_VERSION: str = "1.0.0"
    
    # --- CORS Settings ---
    CORS_ORIGINS: List[str] = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # --- Security ---
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "supersecretkey")
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "jwtsupersecretkey")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("AUTH_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    AUTH_PASSWORD_HASH_ALGORITHM: str = os.environ.get("AUTH_PASSWORD_HASH_ALGORITHM", "bcrypt")
    AUTH_PASSWORD_SALT_ROUNDS: int = int(os.environ.get("AUTH_PASSWORD_SALT_ROUNDS", "12"))
    USE_HTTPS: bool = os.environ.get("USE_HTTPS", "False") == "True"

    # --- Database ---
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "summiva_user")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "summiva_pass")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "summiva_db")
    POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.environ.get("POSTGRES_PORT", "5432"))
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", 
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    # --- Redis and Celery ---
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.environ.get("REDIS_DB", "0"))
    REDIS_URL: str = os.environ.get("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

    # --- Service URLs ---
    AUTH_SERVICE_URL: str = os.environ.get("AUTH_SERVICE_URL", "http://auth:8000")
    SUMMARIZATION_SERVICE_URL: str = os.environ.get("SUMMARIZATION_SERVICE_URL", "http://summarization:8000")
    TAGGING_SERVICE_URL: str = os.environ.get("TAGGING_SERVICE_URL", "http://tagging:8000")
    GROUPING_SERVICE_URL: str = os.environ.get("GROUPING_SERVICE_URL", "http://grouping:8000")
    SEARCH_SERVICE_URL: str = os.environ.get("SEARCH_SERVICE_URL", "http://search:8000")

    # --- Monitoring ---
    ENABLE_MONITORING: bool = os.environ.get("ENABLE_MONITORING", "False") == "True"
    PROMETHEUS_PORT: int = int(os.environ.get("PROMETHEUS_PORT", "9090"))
    GRAFANA_PORT: int = int(os.environ.get("GRAFANA_PORT", "3000"))
    
    # --- Rate limiting ---
    RATE_LIMIT_PER_MINUTE: int = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
    
    # --- Local Paths ---
    def __init__(self):
        # Docker paths
        self.PROJECT_ROOT = "/app"
        self.SRC_DIR = f"{self.PROJECT_ROOT}/src"
        self.CONFIG_DIR = f"{self.PROJECT_ROOT}/config"
        self.DATA_DIR = f"{self.PROJECT_ROOT}/data"
        self.LOGS_DIR = f"{self.PROJECT_ROOT}/logs"
        self.MODELS_DIR = f"{self.PROJECT_ROOT}/models"
        
        # Create these directories if they don't exist
        for path in [self.CONFIG_DIR, self.DATA_DIR, self.LOGS_DIR, self.MODELS_DIR]:
            os.makedirs(path, exist_ok=True)
    
    def __getattr__(self, name):
        """Return None for undefined attributes"""
        print(f"Warning: Accessing undefined setting '{name}'")
        return None

# Create a global settings instance
settings = Settings()