"""
Configuration management using Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Union, Annotated


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_parse_none_str="null"
    )
    
    # Firebase Configuration
    firebase_credentials_path: str = ""  # Path to Firebase service account JSON (local dev)
    firebase_credentials: str = ""  # Base64-encoded JSON (Vercel deployment)
    firebase_project_id: str = ""  # Firebase project ID
    
    # Discord
    discord_token: str = ""
    discord_guild_id: str = ""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    api_title: str = "Warhammer Ranking System API"
    api_version: str = "2.0.0"
    
    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: Union[str, List[str]] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        validation_alias="cors_origins"
    )
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            # Handle comma-separated string
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Environment
    environment: str = "development"
    
    @property
    def is_development(self) -> bool:
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        return self.environment == "production"


# Global settings instance
settings = Settings()
