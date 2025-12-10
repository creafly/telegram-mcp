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
    name="delete_message",
    description="""Удаление сообщения в Telegram.

Этот инструмент позволяет удалить сообщение из чата.
Бот может удалять только свои сообщения или сообщения в группах,
где у него есть права администратора.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно удалить устаревшее сообщение
- Когда нужно очистить чат от ненужных сообщений
- Когда нужно удалить сообщение с ошибкой

ВАЖНО: Удаление необратимо!
""",
)
async def delete_message(
    chat_id: str = Field(
        ...,
        description="ID чата или username (начинается с @).",
    ),
    message_id: int = Field(
        ...,
        description="ID сообщения для удаления.",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """Удаление сообщения в Telegram."""
    if ctx:
        await ctx.info(f"Удаляем сообщение {message_id} из чата: {chat_id}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(f"[delete_message] chat_id={chat_id}, message_id={message_id}")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        await service.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Сообщение {message_id} удалено")

        return {
            "success": True,
            "message": f"Сообщение {message_id} успешно удалено",
            "data": {"chat_id": chat_id, "message_id": message_id, "deleted": True},
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
        return {"success": False, "error": "delete_message_error", "message": str(e)}
