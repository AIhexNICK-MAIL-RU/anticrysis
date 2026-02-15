from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Антикризисное управление"
    secret_key: str = "change-me-in-production-secret-key-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    database_url: str = "sqlite+aiosqlite:///./anticrisis.db"
    # CORS: через запятую, например "https://your-app.twc1.net" или "*" (без credentials)
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
