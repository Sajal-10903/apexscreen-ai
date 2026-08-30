"""Application configuration loaded from environment variables."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for the AI Interview System."""

    # --- Project Paths ---
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).resolve().parent.parent.parent.parent
    )

    # --- LLM Providers ---
    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-3.6-flash", alias="GEMINI_MODEL")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", alias="OPENAI_BASE_URL"
    )

    # --- Database ---
    database_url: str = Field(
        default="sqlite:///./data/interview.db", alias="DATABASE_URL"
    )

    # --- Embeddings ---
    embedding_model: str = Field(
        default="all-MiniLM-L6-v2", alias="EMBEDDING_MODEL"
    )

    # --- Vector Database ---
    chroma_persist_directory: str = Field(
        default="./chroma_db", alias="CHROMA_PERSIST_DIRECTORY"
    )

    # --- RAG ---
    top_k: int = Field(default=5, alias="TOP_K")
    chunk_size: int = Field(default=500, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")

    # --- Interview ---
    interview_question_count: int = Field(
        default=8, alias="INTERVIEW_QUESTION_COUNT"
    )
    max_resume_size_mb: int = Field(default=5, alias="MAX_RESUME_SIZE_MB")

    # --- Rate limiting (0 disables) ---
    rate_limit_upload_per_minute: int = Field(
        default=10, alias="RATE_LIMIT_UPLOAD_PER_MINUTE"
    )
    rate_limit_answer_per_minute: int = Field(
        default=30, alias="RATE_LIMIT_ANSWER_PER_MINUTE"
    )

    # --- Server ---
    backend_host: str = Field(default="0.0.0.0", alias="BACKEND_HOST")
    backend_port: int = Field(default=8000, alias="BACKEND_PORT")
    frontend_url: str = Field(
        default="http://localhost:5173", alias="FRONTEND_URL"
    )

    @property
    def cors_allowed_origins(self) -> list[str]:
        """Parse FRONTEND_URL as a comma-separated list of allowed origins."""
        return [o.strip() for o in self.frontend_url.split(",") if o.strip()]

    # --- Logging ---
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def is_llm_available(self) -> bool:
        """Check if a real LLM API key (Gemini or OpenAI) is configured."""
        return bool(
            (self.gemini_api_key and self.gemini_api_key.strip()) or
            (self.openai_api_key and self.openai_api_key.strip())
        )

    @property
    def upload_directory(self) -> Path:
        """Directory for uploaded resumes."""
        upload_dir = self.project_root / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        return upload_dir

    @property
    def data_directory(self) -> Path:
        """Directory for database files."""
        data_dir = self.project_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @property
    def chroma_directory(self) -> Path:
        """Absolute path to ChromaDB persistence directory."""
        chroma_path = Path(self.chroma_persist_directory)
        if not chroma_path.is_absolute():
            chroma_path = self.project_root / chroma_path
        chroma_path.mkdir(parents=True, exist_ok=True)
        return chroma_path

    @property
    def max_resume_size_bytes(self) -> int:
        return self.max_resume_size_mb * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
        "populate_by_name": True,
    }


# Singleton instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create the settings singleton."""
    global _settings
    if _settings is None:
        # Try loading .env from the project root
        env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
        if env_path.exists():
            os.environ.setdefault("ENV_FILE", str(env_path))
        _settings = Settings(
            _env_file=str(env_path) if env_path.exists() else None
        )
    return _settings


def reset_settings() -> None:
    """Reset settings singleton (for testing)."""
    global _settings
    _settings = None
