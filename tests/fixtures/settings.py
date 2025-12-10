import pytest

from src.core.settings import Settings


@pytest.fixture
def settings():
    """Фикстура настроек для тестов."""
    return Settings(
        TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890",
        TELEGRAM_API_BASE_URL="https://api.telegram.org",
        PORT=8001,
        HOST="0.0.0.0",
        LOG_LEVEL="DEBUG",
        MAX_MESSAGE_LENGTH=4096,
        DEFAULT_PARSE_MODE="HTML",
        REQUEST_TIMEOUT=30,
    )
