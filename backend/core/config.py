"""
Configuration settings for the AI Agent Platform
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "AI Agent Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000", "https://localhost:3000"],
        env="ALLOWED_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_ORGANIZATION: Optional[str] = Field(default=None, env="OPENAI_ORGANIZATION")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Google AI
    GOOGLE_AI_API_KEY: Optional[str] = Field(default=None, env="GOOGLE_AI_API_KEY")
    
    # Vector Database (Pinecone)
    PINECONE_API_KEY: Optional[str] = Field(default=None, env="PINECONE_API_KEY")
    PINECONE_ENVIRONMENT: Optional[str] = Field(default=None, env="PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME: str = Field(default="ai-agent-platform", env="PINECONE_INDEX_NAME")
    
    # Weaviate
    WEAVIATE_URL: Optional[str] = Field(default=None, env="WEAVIATE_URL")
    WEAVIATE_API_KEY: Optional[str] = Field(default=None, env="WEAVIATE_API_KEY")
    
    # ChromaDB
    CHROMA_HOST: str = Field(default="localhost", env="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8000, env="CHROMA_PORT")
    
    # LangChain
    LANGCHAIN_TRACING_V2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    LANGCHAIN_ENDPOINT: Optional[str] = Field(default=None, env="LANGCHAIN_ENDPOINT")
    LANGCHAIN_API_KEY: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: Optional[str] = Field(default=None, env="LANGCHAIN_PROJECT")
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Email
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # Monitoring
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    
    # Agent Configuration
    DEFAULT_AGENT_MODEL: str = Field(default="gpt-4", env="DEFAULT_AGENT_MODEL")
    MAX_AGENTS_PER_USER: int = Field(default=10, env="MAX_AGENTS_PER_USER")
    MAX_CONVERSATIONS_PER_USER: int = Field(default=100, env="MAX_CONVERSATIONS_PER_USER")
    
    # WebSocket
    WEBSOCKET_PING_INTERVAL: int = Field(default=30, env="WEBSOCKET_PING_INTERVAL")
    WEBSOCKET_PING_TIMEOUT: int = Field(default=10, env="WEBSOCKET_PING_TIMEOUT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # Performance
    WORKER_PROCESSES: int = Field(default=1, env="WORKER_PROCESSES")
    KEEP_ALIVE: int = Field(default=2, env="KEEP_ALIVE")
    
    # Agent Tools Configuration
    ENABLE_WEB_SEARCH: bool = Field(default=True, env="ENABLE_WEB_SEARCH")
    ENABLE_CODE_EXECUTION: bool = Field(default=False, env="ENABLE_CODE_EXECUTION")
    ENABLE_FILE_OPERATIONS: bool = Field(default=True, env="ENABLE_FILE_OPERATIONS")
    
    # Search Engine API Keys
    SERPER_API_KEY: Optional[str] = Field(default=None, env="SERPER_API_KEY")
    SERPAPI_API_KEY: Optional[str] = Field(default=None, env="SERPAPI_API_KEY")
    
    # Browser Automation
    PLAYWRIGHT_ENABLED: bool = Field(default=False, env="PLAYWRIGHT_ENABLED")
    
    # API Keys for external services
    HUGGING_FACE_API_KEY: Optional[str] = Field(default=None, env="HUGGING_FACE_API_KEY")
    COHERE_API_KEY: Optional[str] = Field(default=None, env="COHERE_API_KEY")
    
    # Model Configuration
    MODEL_TEMPERATURE: float = Field(default=0.7, env="MODEL_TEMPERATURE")
    MODEL_MAX_TOKENS: int = Field(default=4000, env="MODEL_MAX_TOKENS")
    MODEL_TOP_P: float = Field(default=1.0, env="MODEL_TOP_P")
    MODEL_FREQUENCY_PENALTY: float = Field(default=0.0, env="MODEL_FREQUENCY_PENALTY")
    MODEL_PRESENCE_PENALTY: float = Field(default=0.0, env="MODEL_PRESENCE_PENALTY")
    
    # Embeddings
    EMBEDDING_MODEL: str = Field(default="text-embedding-ada-002", env="EMBEDDING_MODEL")
    EMBEDDING_CHUNK_SIZE: int = Field(default=1000, env="EMBEDDING_CHUNK_SIZE")
    EMBEDDING_CHUNK_OVERLAP: int = Field(default=200, env="EMBEDDING_CHUNK_OVERLAP")
    
    # Security Settings
    BCRYPT_ROUNDS: int = Field(default=12, env="BCRYPT_ROUNDS")
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    
    # Session Management
    SESSION_COOKIE_NAME: str = Field(default="session", env="SESSION_COOKIE_NAME")
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True, env="SESSION_COOKIE_HTTPONLY")
    SESSION_COOKIE_SECURE: bool = Field(default=True, env="SESSION_COOKIE_SECURE")
    
    # CORS Settings
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    CORS_ALLOW_METHODS: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    CORS_ALLOW_HEADERS: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Development Settings
    RELOAD_ON_CHANGE: bool = Field(default=False, env="RELOAD_ON_CHANGE")
    AUTO_RELOAD: bool = Field(default=False, env="AUTO_RELOAD")
    
    # Metrics and Analytics
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Health Check
    HEALTH_CHECK_INTERVAL: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    
    # Backup Settings
    BACKUP_ENABLED: bool = Field(default=False, env="BACKUP_ENABLED")
    BACKUP_INTERVAL: int = Field(default=86400, env="BACKUP_INTERVAL")  # 24 hours
    BACKUP_RETENTION: int = Field(default=7, env="BACKUP_RETENTION")  # 7 days
    
    # Feature Flags
    FEATURE_MARKETPLACE: bool = Field(default=True, env="FEATURE_MARKETPLACE")
    FEATURE_TEAM_COLLABORATION: bool = Field(default=True, env="FEATURE_TEAM_COLLABORATION")
    FEATURE_ADVANCED_ANALYTICS: bool = Field(default=True, env="FEATURE_ADVANCED_ANALYTICS")
    FEATURE_CUSTOM_MODELS: bool = Field(default=False, env="FEATURE_CUSTOM_MODELS")
    
    # Timeout Settings
    HTTP_TIMEOUT: int = Field(default=30, env="HTTP_TIMEOUT")
    LLM_TIMEOUT: int = Field(default=120, env="LLM_TIMEOUT")
    WEBSOCKET_TIMEOUT: int = Field(default=300, env="WEBSOCKET_TIMEOUT")
    
    # Queue Settings
    QUEUE_MAX_SIZE: int = Field(default=1000, env="QUEUE_MAX_SIZE")
    QUEUE_TIMEOUT: int = Field(default=60, env="QUEUE_TIMEOUT")
    
    # Cache Settings
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    CACHE_MAX_SIZE: int = Field(default=1000, env="CACHE_MAX_SIZE")
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("CORS_ALLOW_METHODS", pre=True)
    def parse_cors_methods(cls, v):
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("CORS_ALLOW_HEADERS", pre=True)
    def parse_cors_headers(cls, v):
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create settings instance
settings = get_settings()

# Export commonly used settings
DATABASE_URL = settings.DATABASE_URL
REDIS_URL = settings.REDIS_URL
SECRET_KEY = settings.SECRET_KEY
OPENAI_API_KEY = settings.OPENAI_API_KEY
DEBUG = settings.DEBUG