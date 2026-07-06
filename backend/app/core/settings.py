import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Centralized configuration settings for the FinRelief AI Backend.
    Uses Pydantic Settings to automatically parse environment variables
    from a local .env file.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # General App Config
    APP_NAME: str = "FinRelief AI"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security Configuration
    SECRET_KEY: str = "placeholder_super_secret_signing_key_for_development_purposes_only"
    JWT_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./finrelief.db"

    # AI API Config
    GEMINI_API_KEY: str = "your_gemini_api_key_here"

    # CORS Configuration
    ALLOWED_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """
        Parses a comma-separated string into a list of origins if it's a string,
        otherwise returns the list directly.
        """
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

# Instantiate settings singleton
settings = Settings()
