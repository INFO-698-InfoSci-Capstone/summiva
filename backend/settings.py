from pydantic import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"
    DB_URL: str
    AUTH_SERVICE_URL: str
    # ...

    class Config:
        env_file = ".env"