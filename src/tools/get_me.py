import logging
from typing import Optional

from fastmcp import Context

from src.core.settings import get_settings
from src.core.validators import TelegramAPIError
from src.entrypoints.mcp_instance import mcp
from src.services.telegram_service import TelegramService

logger = logging.getLogger("mcp_telegram")


@mcp.tool(
    name="get_me",
    description="""Получение информации о текущем боте.

Возвращает информацию о боте: username, имя, может ли читать сообщения в группах и т.д.
Полезно для проверки работоспособности бота и получения его идентификатора.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно проверить, что бот работает
- Когда нужно узнать username или ID бота
- Когда нужно проверить права бота
""",
)
async def get_me(
    ctx: Optional[Context] = None,
) -> dict:
    """Получение информации о боте."""
    if ctx:
        await ctx.info("Получаем информацию о боте...")
        await ctx.report_progress(progress=0, total=100)

    logger.info("[get_me] Запрос информации о боте")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = await service.get_me()

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Бот: @{result.get('username')}")

        return {
            "success": True,
            "message": f"Информация о боте @{result.get('username')} получена",
            "data": result,
        }

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
        return {"success": False, "error": "get_me_error", "message": str(e)}
