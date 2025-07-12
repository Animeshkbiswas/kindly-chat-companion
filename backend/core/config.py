"""
Application configuration using Pydantic Settings
Handles environment variables and configuration management.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Environment
    environment: str = Field(default="development", description="Environment (development/production)")
    debug: bool = Field(default=True, description="Debug mode")
    
    # Database
    database_url: str = Field(..., description="PostgreSQL database URL")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Token expiration time")
    
    # AI Services
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API key")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", description="DeepSeek API base URL")
    
    # Audio settings
    max_audio_file_size: int = Field(default=10 * 1024 * 1024, description="Max audio file size in bytes (10MB)")
    audio_upload_dir: str = Field(default="uploads/audio", description="Audio upload directory")
    
    # Therapy settings
    max_session_messages: int = Field(default=100, description="Maximum messages per therapy session")
    default_therapist_personality: str = Field(default="warm", description="Default therapist personality")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()