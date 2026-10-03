import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration from environment variables."""

    # Application
    app_name: str = "LegalLens"
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = app_env == "development"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://legallens:legallens_dev@localhost:5432/legallens")

    # LLM
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4")

    # Embeddings
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Upload constraints
    max_upload_size_mb: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "50"))

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
