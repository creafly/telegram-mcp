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
    name="get_updates",
    description="""Получение обновлений (входящих сообщений) от Telegram.

Этот инструмент позволяет получить список последних сообщений и событий,
отправленных боту. Используется для чтения входящих сообщений.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно узнать, какие сообщения пришли боту
- Когда нужно получить chat_id для ответа пользователю
- Когда нужно обработать входящие команды
""",
)
async def get_updates(
    offset: Optional[int] = Field(
        default=None,
        description="Идентификатор первого обновления. "
        "Обновления с меньшим ID будут игнорироваться.",
    ),
    limit: int = Field(
        default=100,
        description="Максимальное количество обновлений (1-100).",
    ),
    timeout: int = Field(
        default=0,
        description="Таймаут для long polling в секундах (0 для немедленного ответа).",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """Получение обновлений от Telegram."""
    if ctx:
        await ctx.info("Получаем обновления...")
        await ctx.report_progress(progress=0, total=100)

    logger.info(f"[get_updates] offset={offset}, limit={limit}")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = await service.get_updates(
            offset=offset,
            limit=limit,
            timeout=timeout,
        )

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Получено {len(result)} обновлений")

        return {
            "success": True,
            "message": f"Получено {len(result)} обновлений",
            "data": {"updates": result, "count": len(result)},
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
        return {"success": False, "error": "get_updates_error", "message": str(e)}
