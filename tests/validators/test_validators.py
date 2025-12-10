import pytest

from src.core.validators import (
    ValidationError,
    validate_chat_id,
    validate_limit,
    validate_message_id,
    validate_message_text,
    validate_parse_mode,
)


class TestValidateChatId:
    """Тесты для validate_chat_id."""

    def test_valid_integer_chat_id(self):
        """Проверка валидного числового chat_id."""
        assert validate_chat_id(123456789) == 123456789

    def test_valid_negative_integer_chat_id(self):
        """Проверка валидного отрицательного chat_id (группы)."""
        assert validate_chat_id(-123456789) == -123456789

    def test_valid_string_integer_chat_id(self):
        """Проверка строкового числового chat_id."""
        assert validate_chat_id("123456789") == 123456789

    def test_valid_username_chat_id(self):
        """Проверка валидного username."""
        assert validate_chat_id("@mychannel") == "@mychannel"

    def test_invalid_short_username(self):
        """Проверка слишком короткого username."""
        with pytest.raises(ValidationError):
            validate_chat_id("@abc")

    def test_invalid_username_format(self):
        """Проверка некорректного формата username."""
        with pytest.raises(ValidationError):
            validate_chat_id("@123abc")


class TestValidateMessageText:
    """Тесты для validate_message_text."""

    def test_valid_text(self):
        """Проверка валидного текста."""
        assert validate_message_text("Hello, World!") == "Hello, World!"

    def test_empty_text(self):
        """Проверка пустого текста."""
        with pytest.raises(ValidationError):
            validate_message_text("")

    def test_whitespace_only_text(self):
        """Проверка текста только из пробелов."""
        with pytest.raises(ValidationError):
            validate_message_text("   ")

    def test_text_too_long(self):
        """Проверка слишком длинного текста."""
        long_text = "a" * 5000
        with pytest.raises(ValidationError):
            validate_message_text(long_text, max_length=4096)


class TestValidateParseMode:
    """Тесты для validate_parse_mode."""

    def test_valid_html(self):
        """Проверка HTML режима."""
        assert validate_parse_mode("HTML") == "HTML"

    def test_valid_markdown(self):
        """Проверка Markdown режима."""
        assert validate_parse_mode("Markdown") == "Markdown"

    def test_valid_markdown_v2(self):
        """Проверка MarkdownV2 режима."""
        assert validate_parse_mode("MarkdownV2") == "MarkdownV2"

    def test_none_parse_mode(self):
        """Проверка None значения."""
        assert validate_parse_mode(None) is None

    def test_invalid_parse_mode(self):
        """Проверка некорректного режима."""
        with pytest.raises(ValidationError):
            validate_parse_mode("InvalidMode")


class TestValidateMessageId:
    """Тесты для validate_message_id."""

    def test_valid_integer_message_id(self):
        """Проверка валидного числового message_id."""
        assert validate_message_id(123) == 123

    def test_valid_string_message_id(self):
        """Проверка строкового message_id."""
        assert validate_message_id("123") == 123

    def test_invalid_zero_message_id(self):
        """Проверка нулевого message_id."""
        with pytest.raises(ValidationError):
            validate_message_id(0)

    def test_invalid_negative_message_id(self):
        """Проверка отрицательного message_id."""
        with pytest.raises(ValidationError):
            validate_message_id(-1)


class TestValidateLimit:
    """Тесты для validate_limit."""

    def test_valid_limit(self):
        """Проверка валидного лимита."""
        assert validate_limit(50) == 50

    def test_min_limit(self):
        """Проверка минимального лимита."""
        assert validate_limit(1) == 1

    def test_max_limit(self):
        """Проверка максимального лимита."""
        assert validate_limit(100) == 100

    def test_limit_below_min(self):
        """Проверка лимита ниже минимума."""
        with pytest.raises(ValidationError):
            validate_limit(0)

    def test_limit_above_max(self):
        """Проверка лимита выше максимума."""
        with pytest.raises(ValidationError):
            validate_limit(101)
