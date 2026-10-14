import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = f"sqlite+aiosqlite:///{BACKEND_DIR.as_posix()}/auracfo.db"

class Settings(BaseSettings):
    # Operating Mode
    MOCK_LLM: bool = True
    
    # Database
    DATABASE_URL: str = DEFAULT_DB
    
    # LLM Settings
    LLM_PROVIDER: str = "gemini"
    LLM_MODEL: str = "gemini-3.1-flash-lite"
    LLM_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    @property
    def active_llm_key(self) -> str:
        return self.GEMINI_API_KEY or self.LLM_API_KEY
    
    # Security & PII
    HMAC_SECRET_KEY: str = "auracfo-super-secret-hmac-salt-key-2026"
    
    # Server & Networking
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
