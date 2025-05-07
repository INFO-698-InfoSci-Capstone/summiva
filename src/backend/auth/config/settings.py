from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    POSTGRES_USER: str = "summiva_user"
    POSTGRES_PASSWORD: str = "summiva_pass"
    POSTGRES_DB: str = "summiva_db"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: str = "5432"
    # Fixed connection string to ensure correct database name is used
    POSTGRES_DATABASE_URL:str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    POSTGRES_DATABASE_POOL_SIZE: int = 5
    POSTGRES_DATABASE_MAX_OVERFLOW: int = 10
    
    # JWT settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security settings
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    PASSWORD_SALT_ROUNDS: int = 12
    
    # Service settings
    SERVICE_NAME: str = "auth"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()