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
    name="get_chat",
    description="""Получение информации о чате Telegram.

Этот инструмент возвращает подробную информацию о чате:
название, тип, описание, количество участников и т.д.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно узнать информацию о чате или канале
- Когда нужно проверить тип чата (группа, канал, личный)
- Когда нужно получить описание или название чата
""",
)
async def get_chat(
    chat_id: str = Field(
        ...,
        description="ID чата или username (начинается с @). Например: '123456789' или '@mychannel'",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """Получение информации о чате."""
    if ctx:
        await ctx.info(f"Получаем информацию о чате: {chat_id}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(f"[get_chat] chat_id={chat_id}")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = await service.get_chat(chat_id=chat_id)

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(
                f"""Получена информация о чате: {
                    result.get("title", result.get("username", chat_id))
                }"""
            )

        return {
            "success": True,
            "message": "Информация о чате получена",
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
        return {"success": False, "error": "get_chat_error", "message": str(e)}
