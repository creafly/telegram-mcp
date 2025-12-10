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
    name="send_document",
    description="""Отправка документа в Telegram чат.

Этот инструмент позволяет отправлять файлы любого типа по URL или file_id.
Поддерживает добавление подписи к документу.

КОГДА ИСПОЛЬЗОВАТЬ:
- Когда нужно отправить файл пользователю (PDF, DOC, и т.д.)
- Когда нужно поделиться документом
- Когда нужно отправить файл с описанием
""",
)
async def send_document(
    chat_id: str = Field(
        ...,
        description="ID чата или username (начинается с @).",
    ),
    document: str = Field(
        ...,
        description="URL документа или file_id ранее загруженного файла.",
    ),
    caption: Optional[str] = Field(
        default=None,
        description="Подпись к документу (максимум 1024 символа).",
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
    """Отправка документа в Telegram."""
    if ctx:
        await ctx.info(f"Отправляем документ в чат: {chat_id}")
        await ctx.report_progress(progress=0, total=100)

    logger.info(f"[send_document] chat_id={chat_id}")

    try:
        settings = get_settings()
        settings.validate_required_fields()

        service = TelegramService(settings)

        if ctx:
            await ctx.report_progress(progress=50, total=100)

        result = await service.send_document(
            chat_id=chat_id,
            document=document,
            caption=caption,
            parse_mode=parse_mode,
            disable_notification=disable_notification,
        )

        await service.close()

        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Документ отправлен, message_id={result.get('message_id')}")

        return {
            "success": True,
            "message": "Документ успешно отправлен",
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
        return {"success": False, "error": "send_document_error", "message": str(e)}
