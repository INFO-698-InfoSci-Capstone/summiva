import os, sys, yaml
from pathlib import Path
from functools import lru_cache
from typing import List, Any

try:
    from dotenv import load_dotenv
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

# -----------------------------
# Load .env file
# -----------------------------
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
    print(f"✅ Loaded env: {env_path}")

# -----------------------------
# Load settings.yaml
# -----------------------------
yaml_config = {}
yaml_path = Path(__file__).parent / "settings.yaml"
if yaml_path.exists():
    with open(yaml_path, "r") as f:
        full_yaml = yaml.safe_load(f)
        env = os.getenv("ENVIRONMENT", "development").lower()
        yaml_config = {**full_yaml.get("default", {}), **full_yaml.get(env, {})}

def get_config(key: str, default: Any = None) -> Any:
    keys = key.split(".")
    val = yaml_config
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            break
    if val not in [None, {}, ""]:
        return val
    env_key = key.upper().replace(".", "_")
    return os.getenv(env_key, default)

# -----------------------------
# Unified Settings Class
# -----------------------------
class Settings:
    # --- Environment ---
    ENVIRONMENT: str = get_config("environment", "development")
    DEBUG: bool = str(get_config("debug", ENVIRONMENT != "production")).lower() == "true"
    LOG_LEVEL: str = get_config("log_level", "DEBUG" if DEBUG else "INFO")

    # --- Application ---
    APP_NAME: str = get_config("app_name", "Summiva")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Summiva"
    APP_SERVICE_NAME: str = get_config("service_name", "backend")
    APP_SERVICE_VERSION: str = get_config("app_version", "1.0.0")

    # --- CORS ---
    CORS_ORIGINS: List[str] = get_config("cors_origins", "http://localhost:3000,http://localhost:8080").split(",")
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # --- Security ---
    SECRET_KEY: str = get_config("secret_key", "dev_secret_key")
    JWT_SECRET_KEY: str = get_config("jwt_secret_key", "dev_jwt_secret_key")
    JWT_ALGORITHM: str = get_config("jwt_algorithm", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_config("access_token_expire_minutes", 30))
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(get_config("auth_access_token_expire_minutes", 30))
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = int(get_config("auth_refresh_token_expire_days", 7))
    AUTH_PASSWORD_HASH_ALGORITHM: str = get_config("auth_password_hash_algorithm", "bcrypt")
    AUTH_PASSWORD_SALT_ROUNDS: int = int(get_config("auth_password_salt_rounds", 12))

    # --- PostgreSQL ---
    POSTGRES_USER: str = get_config("postgres_user", "summiva_user")
    POSTGRES_PASSWORD: str = get_config("postgres_password", "summiva_pass")
    POSTGRES_DB: str = get_config("postgres_db", "summiva_db")
    POSTGRES_HOST: str = get_config("postgres_host", "postgres")
    POSTGRES_PORT: int = int(get_config("postgres_port", 5432))
    DATABASE_URL: str = get_config("postgres.uri", f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    POSTGRES_DATABASE_URL: str = DATABASE_URL
    DATABASE_POOL_SIZE: int = int(get_config("database.pool_size", 10))
    DATABASE_MAX_OVERFLOW: int = int(get_config("database.max_overflow", 20))

    # --- MongoDB ---
    MONGODB_URI: str = get_config("mongodb.uri", "mongodb://mongodb:27017")

    # --- Redis ---
    REDIS_HOST: str = get_config("redis.host", "redis")
    REDIS_PORT: int = int(get_config("redis.port", 6379))
    REDIS_DB: int = int(get_config("redis.db", 0))
    REDIS_URL: str = get_config("redis.url", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")

    # --- Celery ---
    RABBITMQ_USER: str = get_config("rabbitmq_user", "guest")
    RABBITMQ_PASSWORD: str = get_config("rabbitmq_password", "guest")
    RABBITMQ_PORT: int = int(get_config("rabbitmq_port", 5672))
    CELERY_BROKER_URL: str = get_config("celery.broker_url", f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASSWORD}@rabbitmq:{RABBITMQ_PORT}//")

    CELERY_RESULT_BACKEND: str = get_config("celery.result_backend", "rpc://")

    # --- Search ---
    ELASTIC_URL: str = get_config("search.elastic_url", "http://elasticsearch:9200")
    FAISS_INDEX_PATH: str = get_config("search.faiss_index_path", "faiss/index")
    FAISS_DOC_MAP_PATH: str = get_config("search.faiss_doc_map_path", "faiss/doc_ids.npy")

    # --- Monitoring ---
    ENABLE_MONITORING: bool = str(get_config("enable_monitoring", "False")).lower() == "true"
    PROMETHEUS_PORT: int = int(get_config("prometheus_port", 9090))
    GRAFANA_PORT: int = int(get_config("grafana_port", 3000))

    # --- External Services ---
    AUTH_SERVICE_URL: str = get_config("auth_service_url", "http://auth:8000")
    SUMMARIZATION_SERVICE_URL: str = get_config("summarization_service_url", "http://summarization:8000")
    TAGGING_SERVICE_URL: str = get_config("tagging_service_url", "http://tagging:8000")
    GROUPING_SERVICE_URL: str = get_config("grouping_service_url", "http://grouping:8000")
    SEARCH_SERVICE_URL: str = get_config("search_service_url", "http://search:8000")
    CLUSTERING_SERVICE_URL: str = get_config("clustering_service_url", "http://clustering:8000")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()