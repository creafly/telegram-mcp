import pytest

from src.services.telegram_service import TelegramService


@pytest.fixture
def telegram_service(settings):
    """Фикстура TelegramService для тестов."""
    return TelegramService(settings)
