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
    name="edit_message",
    description="""Редактирование текстового сообщения в Telegram.

Этот инструмент позволяет изменить текст ранее отправленного сообщения.
Можно редактировать только сообщения, отправленные ботом.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно исправить опечатку в отправленном сообщении
- Когда нужно обновить информацию в сообщении
- Когда нужно изменить статус в сообщении (например, "Обработка..." -> "Готово!")
""",
)
async def edit_message(
    chat_id: str = Field(
        ...,
        description="ID чата или username (начинается с @).",
    ),
    message_id: int = Field(
        ...,
        description="ID сообщения для редактирования.",
    ),
    text: str = Field(
        ...,
        description="Новый текст сообщения (максимум 4096 символов).",
    ),
    parse_mode: Optional[str] = Field(
        default=None,
        description="Режим парсинга: 'HTML', 'Markdown' или 'MarkdownV2'.",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """Редактирование сообщения в Telegram."""
    if ctx:
        await ctx.info(f"Редактируем сообщение {message_id} в чате: {chat_id}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(f"[edit_message] chat_id={chat_id}, message_id={message_id}")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = await service.edit_message(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=parse_mode,
        )

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Сообщение {message_id} отредактировано")

        return {
            "success": True,
            "message": "Сообщение успешно отредактировано",
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
        return {"success": False, "error": "edit_message_error", "message": str(e)}
