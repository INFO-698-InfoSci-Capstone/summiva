from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database settings
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
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