import logging
from typing import Optional

from fastmcp import Context
from pydantic import Field

from src.core.settings import get_settings
from src.core.validators import TelegramAPIError, ValidationError
from src.entrypoints.mcp_instance import mcp
from src.services.telegram_service import TelegramService

logger = logging.getLogger("mcp_telegram")


@mcp.tool(
    name="send_message",
    description="""Отправка текстового сообщения в Telegram чат.

Этот инструмент позволяет отправлять текстовые сообщения в любой чат Telegram
(личные сообщения, группы, каналы). Поддерживает:
- Форматирование текста (HTML, Markdown)
- Ответ на конкретное сообщение
- Отключение уведомлений

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно отправить текстовое сообщение пользователю или в группу
- Когда нужно уведомить о каком-либо событии
- Когда нужно ответить на сообщение пользователя
""",
)
async def send_message(
    chat_id: str = Field(
        ...,
        description="ID чата или username (начинается с @). Например: '123456789' или '@mychannel'",
    ),
    text: str = Field(
        ...,
        description="Текст сообщения. Максимум 4096 символов. "
        "Поддерживает HTML и Markdown форматирование.",
    ),
    parse_mode: Optional[str] = Field(
        default=None,
        description="Режим парсинга: 'HTML', 'Markdown' или 'MarkdownV2'. "
        "Если не указан, используется значение по умолчанию из настроек.",
    ),
    disable_notification: bool = Field(
        default=False,
        description="Отключить звуковое уведомление о сообщении.",
    ),
    reply_to_message_id: Optional[int] = Field(
        default=None,
        description="ID сообщения, на которое нужно ответить.",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """Отправка текстового сообщения в Telegram."""
    if ctx:
        await ctx.info(f"Отправляем сообщение в чат: {chat_id}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(f"[send_message] chat_id={chat_id}")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = await service.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
        )

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Сообщение отправлено, message_id={result.get('message_id')}")

        return {
            "success": True,
            "message": "Сообщение успешно отправлено",
            "data": result,
        }

    except ValidationError as e:
        if ctx:
            await ctx.error(f"Ошибка валидации: {e}")
        return {"success": False, "error": "validation_error", "message": str(e)}
    except TelegramAPIError as e:
        if ctx:
            await ctx.error(f"Ошибка Telegram API: {e}")
        return {
            "success": False,
            "error": "telegram_api_error",
            "message": str(e),
            "error_code": e.error_code,
        }
    except Exception as e:
        if ctx:
            await ctx.error(f"Ошибка: {e}")
        return {"success": False, "error": "send_error", "message": str(e)}
