"""
AgentCrashLab — Core Configuration

Loads all settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- Application ---
    app_name: str = "AgentCrashLab"
    app_version: str = "0.1.0"
    debug: bool = True

    # --- Database ---
    database_url: str = "postgresql://agentcrash:agentcrash_dev@db:5432/agentcrashlab"

    # --- Server ---
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # --- LLM Providers ---
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_api_key: str = ""

    # --- Agent Defaults ---
    default_model_provider: str = "mock"
    default_model_name: str = "gpt-4o"

    # --- Sandbox ---
    sandbox_timeout_seconds: int = 30
    sandbox_max_tool_calls: int = 20

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
