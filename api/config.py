"""
Configuration management for production deployment
"""
import os
from enum import Enum
from pydantic_settings import BaseSettings

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # App Configuration
    ENVIRONMENT: Environment = Environment(os.getenv("ENVIRONMENT", "development"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    AUTO_OPEN_BROWSER: bool = os.getenv("AUTO_OPEN_BROWSER", "true").lower() == "true"
    
    # Security
    CORS_ORIGINS: list = ["*"]  # Configure based on environment
    ALLOWED_HOSTS: list = ["*"]
    
    # API Configuration
    API_PREFIX: str = "/api"
    API_TITLE: str = "Failure-Driven AWS Architect"
    API_VERSION: str = "1.0"
    
    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp:free")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # RAG Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    VECTOR_STORE_PATH: str = os.getenv("VECTOR_STORE_PATH", "vector_store")
    
    # Timeouts
    LLM_TIMEOUT: int = int(os.getenv("LLM_TIMEOUT", "30"))
    ANALYSIS_TIMEOUT: int = int(os.getenv("ANALYSIS_TIMEOUT", "60"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env

# Create global settings instance
settings = Settings()

# Override CORS based on environment
if settings.ENVIRONMENT == "production":
    settings.CORS_ORIGINS = [
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ]
    settings.DEBUG = False
