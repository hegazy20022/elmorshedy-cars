from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/elmorshedy_cars"

    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_OWNER_CHAT_ID: int

    GEMINI_API_KEY: Optional[str] = None
    AI_PROVIDER: str = "rule_based"

    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    CACHE_TTL_SECONDS: int = 86400
    CACHE_REPEAT_THRESHOLD: int = 3
    TELEGRAM_DAILY_MESSAGE_LIMIT: int = 20

    TIMEZONE: str = "Africa/Cairo"

    WEBHOOK_URL: Optional[str] = None
    WEBHOOK_PATH: str = "/webhook/telegram"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
