"""
Application configuration using Pydantic settings.
"""
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow",
    )
    
    # Application
    PROJECT_NAME: str = "Multi-Agent RCA Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="development, staging, production")
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    API_V1_STR: str = "/api/v1"
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # Security
    JWT_SECRET_KEY: str = Field(description="256-bit secret key for JWT")
    JWT_ALGORITHM: str = "RS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # OAuth2/SSO
    OAUTH2_CLIENT_ID: Optional[str] = None
    OAUTH2_CLIENT_SECRET: Optional[str] = None
    OAUTH2_TENANT_ID: Optional[str] = None
    OAUTH2_AUTHORITY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://rca_user:password@localhost:5432/rca_platform",
        description="PostgreSQL connection string"
    )
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_DECODE_RESPONSES: bool = True
    
    # Vector Database (Qdrant)
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "rca_knowledge_base"
    QDRANT_EMBEDDING_DIM: int = 3072  # text-embedding-3-large
    
    # LLM Configuration
    OPENAI_API_KEY: str = Field(description="OpenAI API key")
    OPENAI_MODEL: str = "gpt-4-turbo-2024-04-09"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_TIMEOUT: int = 60
    
    # Anthropic (fallback)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    
    # LLM Usage Limits
    MAX_TOKENS_PER_RCA: int = 50000
    LLM_TEMPERATURE: float = 0.0
    LLM_STREAMING_ENABLED: bool = True
    
    # Object Storage (MinIO/S3)
    S3_ENDPOINT: str = Field(default="http://localhost:9000")
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_STDF: str = "stdf-files"
    S3_BUCKET_REPORTS: str = "rca-reports"
    S3_BUCKET_WAFER_MAPS: str = "wafer-maps"
    S3_SECURE: bool = False  # Use HTTPS
    
    # RCA Processing
    MAX_CONCURRENT_RCAS: int = 10
    RCA_TIMEOUT_MINUTES: int = 45
    RCA_QUEUE_MAX_DEPTH: int = 100
    AGENT_EXECUTION_TIMEOUT: int = 600  # 10 minutes per agent
    LANGGRAPH_MAX_ITERATIONS: int = 10
    
    # RAG Configuration
    RAG_TOP_K_RETRIEVAL: int = 20
    RAG_TOP_K_RERANK: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.6
    RAG_CHUNK_SIZE: int = 1000
    RAG_CHUNK_OVERLAP: int = 200
    
    # API Rate Limiting
    API_RATE_LIMIT: int = 100  # requests per minute per user
    RCA_SUBMISSION_LIMIT_PER_DAY: int = 50
    
    # Monitoring
    PROMETHEUS_PORT: int = 9090
    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    
    # Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "notifications@company.com"
    
    # Feature Flags
    ENABLE_WEBSOCKET: bool = True
    ENABLE_RAG: bool = True
    ENABLE_FEEDBACK: bool = True
    ENABLE_AUTO_RETRY: bool = True
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of {allowed}")
        return v
    
    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == "production"


# Global settings instance
settings = Settings()
