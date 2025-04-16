from pydantic import BaseSettings
import os
from src.backend.core.utils import generate_secure_token


class Settings(BaseSettings):
    # Database settings
    POSTGRES_DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # JWT settings
    JWT_SECRET_KEY: str = os.environ.get(
        "JWT_SECRET_KEY", generate_secure_token()
    )
    JWT_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security settings
    AUTH_PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    AUTH_PASSWORD_SALT_ROUNDS: int = 12

    # Service settings
    APP_SERVICE_NAME: str = "backend"
    APP_SERVICE_VERSION: str = "1.0.0"
    APP_DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()