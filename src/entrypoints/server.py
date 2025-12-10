import traceback

from src.core.settings import get_settings, setup_logging
from src.entrypoints.mcp_instance import mcp

settings = get_settings()
logger = setup_logging(settings.LOG_LEVEL)


def main():
    from src.tools import (  # noqa: F401
        delete_message,
        edit_message,
        get_chat,
        get_me,
        get_updates,
        send_document,
        send_message,
        send_photo,
    )

    """Запуск MCP сервера с HTTP транспортом."""
    logger.info("=" * 60)
    logger.info(
        f"""Telegram Bot Token: {"*" * 10}...{
            settings.TELEGRAM_BOT_TOKEN[-4:] if len(settings.TELEGRAM_BOT_TOKEN) > 4 else "***"
        }"""
    )
    logger.info(f"API Base URL: {settings.TELEGRAM_API_BASE_URL}")

    tool_count = len(mcp._tool_manager._tools) if hasattr(mcp, "_tool_manager") else "unknown"
    logger.info(f"Зарегистрировано инструментов: {tool_count}")
    logger.info("=" * 60)

    try:
        mcp.run(
            transport="streamable-http",
            host=settings.HOST,
            port=settings.PORT,
        )
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
        logger.info("Выполняем graceful shutdown...")
        logger.info("Сервер остановлен")
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
