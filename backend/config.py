import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Browser Automation Agent"
    VERSION: str = "1.0.0"

    # Environment & Server
    ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./agent.db"

    # LLM Settings
    LLM_PROVIDER: Literal["gemini", "openai", "mock"] = "gemini"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.5-flash"

    # Playwright Settings
    PLAYWRIGHT_HEADLESS: bool = True
    ACTION_TIMEOUT_MS: int = 15000
    NAVIGATION_TIMEOUT_MS: int = 30000

    # Agent Constraints
    MAX_TASK_STEPS: int = 20
    MAX_RETRY_ATTEMPTS: int = 3

    # Storage Paths
    STORAGE_DIR: str = os.path.join("backend", "storage")
    SCREENSHOTS_DIR: str = os.path.join("backend", "storage", "screenshots")
    DOWNLOADS_DIR: str = os.path.join("backend", "storage", "downloads")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def ensure_directories(self):
        os.makedirs(self.STORAGE_DIR, exist_ok=True)
        os.makedirs(self.SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(self.DOWNLOADS_DIR, exist_ok=True)


settings = Settings()
settings.ensure_directories()
