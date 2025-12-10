import re


class ValidationError(Exception):
    """Ошибка валидации."""

    pass


class TelegramAPIError(Exception):
    """Ошибка Telegram API."""

    def __init__(self, message: str, error_code: int | None = None):
        super().__init__(message)
        self.error_code = error_code


def validate_chat_id(chat_id: str | int) -> int | str:
    """
    Валидация идентификатора чата.

    Args:
        chat_id: ID чата (число или username с @)

    Returns:
        Валидированный chat_id

    Raises:
        ValidationError: Если chat_id некорректен
    """
    if isinstance(chat_id, int):
        return chat_id

    if isinstance(chat_id, str):
        if chat_id.lstrip("-").isdigit():
            return int(chat_id)

        if chat_id.startswith("@"):
            if len(chat_id) < 2:
                raise ValidationError("Username слишком короткий")
            if not re.match(r"^@[a-zA-Z][a-zA-Z0-9_]{4,}$", chat_id):
                raise ValidationError(
                    "Некорректный username. Username должен начинаться с @, "
                    "содержать минимум 5 символов и состоять из букв, " + "цифр и подчёркиваний"
                )
            return chat_id

        raise ValidationError("chat_id должен быть числом или username, начинающимся с @")

    raise ValidationError("chat_id должен быть строкой или числом")


def validate_message_text(text: str, max_length: int = 4096) -> str:
    """
    Валидация текста сообщения.

    Args:
        text: Текст сообщения
        max_length: Максимальная длина

    Returns:
        Валидированный текст

    Raises:
        ValidationError: Если текст некорректен
    """
    if not text:
        raise ValidationError("Текст сообщения не может быть пустым")

    if not text.strip():
        raise ValidationError("Текст сообщения не может состоять только из пробелов")

    if len(text) > max_length:
        raise ValidationError(
            f"Текст сообщения превышает максимальную длину ({len(text)} > {max_length})"
        )

    return text


def validate_parse_mode(parse_mode: str | None) -> str | None:
    """
    Валидация режима парсинга.

    Args:
        parse_mode: Режим парсинга

    Returns:
        Валидированный режим парсинга

    Raises:
        ValidationError: Если режим некорректен
    """
    if parse_mode is None:
        return None

    allowed_modes = ["HTML", "Markdown", "MarkdownV2"]
    if parse_mode not in allowed_modes:
        raise ValidationError(
            f"Некорректный parse_mode: {parse_mode}. "
            f"Допустимые значения: {', '.join(allowed_modes)}"
        )

    return parse_mode


def validate_file_id(file_id: str) -> str:
    """
    Валидация file_id.

    Args:
        file_id: ID файла в Telegram

    Returns:
        Валидированный file_id

    Raises:
        ValidationError: Если file_id некорректен
    """
    if not file_id:
        raise ValidationError("file_id не может быть пустым")

    if not isinstance(file_id, str):
        raise ValidationError("file_id должен быть строкой")

    if len(file_id) < 10:
        raise ValidationError("file_id слишком короткий")

    return file_id


def validate_message_id(message_id: int | str) -> int:
    """
    Валидация ID сообщения.

    Args:
        message_id: ID сообщения

    Returns:
        Валидированный message_id

    Raises:
        ValidationError: Если message_id некорректен
    """
    if isinstance(message_id, str):
        if not message_id.isdigit():
            raise ValidationError("message_id должен быть положительным числом")
        message_id = int(message_id)

    if not isinstance(message_id, int):
        raise ValidationError("message_id должен быть числом")

    if message_id <= 0:
        raise ValidationError("message_id должен быть положительным числом")

    return message_id


def validate_limit(limit: int, min_value: int = 1, max_value: int = 100) -> int:
    """
    Валидация лимита.

    Args:
        limit: Значение лимита
        min_value: Минимальное значение
        max_value: Максимальное значение

    Returns:
        Валидированный лимит

    Raises:
        ValidationError: Если лимит некорректен
    """
    if not isinstance(limit, int):
        raise ValidationError("limit должен быть целым числом")

    if limit < min_value:
        raise ValidationError(f"limit не может быть меньше {min_value}")

    if limit > max_value:
        raise ValidationError(f"limit не может быть больше {max_value}")

    return limit
