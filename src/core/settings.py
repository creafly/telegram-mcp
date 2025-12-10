import logging
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Настройки приложения для работы с Telegram Bot API."""

    APP_NAME: str = Field(default="Telegram MCP Server", description="Название приложения")

    TELEGRAM_BOT_TOKEN: str = Field(
        default="", description="Токен бота Telegram, полученный от @BotFather"
    )
    TELEGRAM_API_BASE_URL: str = Field(
        default="https://api.telegram.org",
        description="Базовый URL для Telegram Bot API",
    )

    PORT: int = Field(default=8001, ge=1024, le=65535, description="Порт для запуска MCP сервера")
    HOST: str = Field(default="0.0.0.0", description="Хост для запуска MCP сервера")
    LOG_LEVEL: str = Field(default="INFO", description="Уровень логирования")

    MAX_MESSAGE_LENGTH: int = Field(
        default=4096,
        ge=1,
        le=4096,
        description="Максимальная длина сообщения в Telegram",
    )
    DEFAULT_PARSE_MODE: Optional[str] = Field(
        default="HTML",
        description="Режим парсинга по умолчанию (HTML, Markdown, MarkdownV2)",
    )
    REQUEST_TIMEOUT: int = Field(
        default=30,
        ge=5,
        le=120,
        description="Таймаут запросов к Telegram API в секундах",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def validate_required_fields(self) -> None:
        """Проверка обязательных полей."""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")

    @property
    def api_url(self) -> str:
        """Полный URL для API запросов."""
        return f"{self.TELEGRAM_API_BASE_URL}/bot{self.TELEGRAM_BOT_TOKEN}"


@lru_cache()
def get_settings() -> Settings:
    """Получить экземпляр настроек (с кешированием)."""
    return Settings()


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Настройка логирования."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    return logging.getLogger("mcp_telegram")
