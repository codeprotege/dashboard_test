from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional # Optional is not needed here if all fields are required

class Settings(BaseSettings):
    PROJECT_NAME: str = "Financial Dashboard API"
    ALPHA_VANTAGE_API_KEY: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Pydantic V2 way to specify .env file
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
