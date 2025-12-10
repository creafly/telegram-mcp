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
    name="send_photo",
    description="""Отправка фотографии в Telegram чат.

Этот инструмент позволяет отправлять фотографии по URL или file_id.
Поддерживает добавление подписи к фото.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно отправить изображение пользователю
- Когда нужно поделиться скриншотом или графиком
- Когда нужно отправить фото с подписью
""",
)
async def send_photo(
    chat_id: str = Field(
        ...,
        description="ID чата или username (начинается с @).",
    ),
    photo: str = Field(
        ...,
        description="URL фотографии или file_id ранее загруженного фото.",
    ),
    caption: Optional[str] = Field(
        default=None,
        description="Подпись к фотографии (максимум 1024 символа).",
    ),
    parse_mode: Optional[str] = Field(
        default=None,
        description="Режим парсинга подписи: 'HTML', 'Markdown' или 'MarkdownV2'.",
    ),
    disable_notification: bool = Field(
        default=False,
        description="Отключить звуковое уведомление.",
    ),
    ctx: Optional[Context] = None,
) -> dict:
    """Отправка фотографии в Telegram."""
    if ctx:
        await ctx.info(f"Отправляем фото в чат: {chat_id}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(f"[send_photo] chat_id={chat_id}")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = await service.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
        )

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Фото отправлено, message_id={result.get('message_id')}")

        return {
            "success": True,
            "message": "Фото успешно отправлено",
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
        return {"success": False, "error": "send_photo_error", "message": str(e)}
