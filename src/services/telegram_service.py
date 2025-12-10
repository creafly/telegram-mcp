import logging
from typing import Any

import httpx

from src.core.settings import Settings
from src.core.validators import (
    TelegramAPIError,
    validate_chat_id,
    validate_limit,
    validate_message_id,
    validate_message_text,
    validate_parse_mode,
)

logger = logging.getLogger("mcp_telegram")


class TelegramService:
    """Сервис для работы с Telegram Bot API."""

    def __init__(self, settings: Settings):
        """
        Инициализация Telegram сервиса.

        Args:
            settings: Настройки приложения
        """
        self.settings = settings
        self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Lazy инициализация HTTP клиента."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=self.settings.REQUEST_TIMEOUT,
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def _request(
        self,
        method: str,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Выполнение запроса к Telegram API.

        Args:
            method: Метод API (например, 'sendMessage')
            data: Данные запроса
            files: Файлы для отправки

        Returns:
            Ответ от API

        Raises:
            TelegramAPIError: При ошибке API
        """
        url = f"{self.settings.api_url}/{method}"

        try:
            if files:
                response = await self.client.post(url, data=data, files=files)
            else:
                response = await self.client.post(url, json=data)

            result = response.json()

            if not result.get("ok"):
                error_code = result.get("error_code")
                description = result.get("description", "Unknown error")
                raise TelegramAPIError(description, error_code)

            return result.get("result", {})

        except httpx.TimeoutException:
            raise TelegramAPIError("Request timeout", error_code=408)
        except httpx.RequestError as e:
            raise TelegramAPIError(f"Request error: {e}", error_code=500)

    async def get_me(self) -> dict[str, Any]:
        """
        Получение информации о боте.

        Returns:
            Информация о боте
        """
        result = await self._request("getMe")
        logger.info(f"Получена информация о боте: @{result.get('username')}")
        return result

    async def send_message(
        self,
        chat_id: int | str,
        text: str,
        parse_mode: str | None = None,
        disable_notification: bool = False,
        reply_to_message_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Отправка текстового сообщения.

        Args:
            chat_id: ID чата или username
            text: Текст сообщения
            parse_mode: Режим парсинга (HTML, Markdown, MarkdownV2)
            disable_notification: Отключить уведомление
            reply_to_message_id: ID сообщения для ответа

        Returns:
            Информация об отправленном сообщении
        """
        chat_id = validate_chat_id(chat_id)
        text = validate_message_text(text, self.settings.MAX_MESSAGE_LENGTH)
        parse_mode = validate_parse_mode(parse_mode) or self.settings.DEFAULT_PARSE_MODE

        data = {
            "chat_id": chat_id,
            "text": text,
        }

        if parse_mode:
            data["parse_mode"] = parse_mode
        if disable_notification:
            data["disable_notification"] = True
        if reply_to_message_id:
            data["reply_to_message_id"] = validate_message_id(reply_to_message_id)

        result = await self._request("sendMessage", data)
        logger.info(
            f"Сообщение отправлено в чат {chat_id}, " + f"message_id={result.get('message_id')}"
        )
        return result

    async def get_updates(
        self,
        offset: int | None = None,
        limit: int = 100,
        timeout: int = 0,
    ) -> dict[str, Any]:
        """
        Получение обновлений (входящих сообщений).

        Args:
            offset: Offset для получения обновлений
            limit: Максимальное количество обновлений
            timeout: Long polling timeout

        Returns:
            Список обновлений
        """
        limit = validate_limit(limit, 1, 100)

        data = {"limit": limit, "timeout": timeout}
        if offset is not None:
            data["offset"] = offset

        result = await self._request("getUpdates", data)
        logger.info(f"Получено {len(result)} обновлений")
        return result

    async def get_chat(self, chat_id: int | str) -> dict[str, Any]:
        """
        Получение информации о чате.

        Args:
            chat_id: ID чата или username

        Returns:
            Информация о чате
        """
        chat_id = validate_chat_id(chat_id)
        result = await self._request("getChat", {"chat_id": chat_id})
        logger.info(f"Получена информация о чате {chat_id}")
        return result

    async def send_photo(
        self,
        chat_id: int | str,
        photo: str,
        caption: str | None = None,
        parse_mode: str | None = None,
        disable_notification: bool = False,
    ) -> dict[str, Any]:
        """
        Отправка фото.

        Args:
            chat_id: ID чата или username
            photo: URL или file_id фото
            caption: Подпись к фото
            parse_mode: Режим парсинга
            disable_notification: Отключить уведомление

        Returns:
            Информация об отправленном сообщении
        """
        chat_id = validate_chat_id(chat_id)
        parse_mode = validate_parse_mode(parse_mode) or self.settings.DEFAULT_PARSE_MODE

        data = {
            "chat_id": chat_id,
            "photo": photo,
        }

        if caption:
            data["caption"] = validate_message_text(caption, 1024)
        if parse_mode:
            data["parse_mode"] = parse_mode
        if disable_notification:
            data["disable_notification"] = True

        result = await self._request("sendPhoto", data)
        logger.info(f"Фото отправлено в чат {chat_id}")
        return result

    async def send_document(
        self,
        chat_id: int | str,
        document: str,
        caption: str | None = None,
        parse_mode: str | None = None,
        disable_notification: bool = False,
    ) -> dict[str, Any]:
        """
        Отправка документа.

        Args:
            chat_id: ID чата или username
            document: URL или file_id документа
            caption: Подпись к документу
            parse_mode: Режим парсинга
            disable_notification: Отключить уведомление

        Returns:
            Информация об отправленном сообщении
        """
        chat_id = validate_chat_id(chat_id)
        parse_mode = validate_parse_mode(parse_mode) or self.settings.DEFAULT_PARSE_MODE

        data = {
            "chat_id": chat_id,
            "document": document,
        }

        if caption:
            data["caption"] = validate_message_text(caption, 1024)
        if parse_mode:
            data["parse_mode"] = parse_mode
        if disable_notification:
            data["disable_notification"] = True

        result = await self._request("sendDocument", data)
        logger.info(f"Документ отправлен в чат {chat_id}")
        return result

    async def edit_message(
        self,
        chat_id: int | str,
        message_id: int,
        text: str,
        parse_mode: str | None = None,
    ) -> dict[str, Any]:
        """
        Редактирование сообщения.

        Args:
            chat_id: ID чата или username
            message_id: ID сообщения
            text: Новый текст
            parse_mode: Режим парсинга

        Returns:
            Информация об отредактированном сообщении
        """
        chat_id = validate_chat_id(chat_id)
        message_id = validate_message_id(message_id)
        text = validate_message_text(text, self.settings.MAX_MESSAGE_LENGTH)
        parse_mode = validate_parse_mode(parse_mode) or self.settings.DEFAULT_PARSE_MODE

        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
        }

        if parse_mode:
            data["parse_mode"] = parse_mode

        result = await self._request("editMessageText", data)
        logger.info(f"Сообщение {message_id} отредактировано в чате {chat_id}")
        return result

    async def delete_message(
        self,
        chat_id: int | str,
        message_id: int,
    ) -> bool:
        """
        Удаление сообщения.

        Args:
            chat_id: ID чата или username
            message_id: ID сообщения

        Returns:
            True при успешном удалении
        """
        chat_id = validate_chat_id(chat_id)
        message_id = validate_message_id(message_id)

        await self._request(
            "deleteMessage",
            {
                "chat_id": chat_id,
                "message_id": message_id,
            },
        )

        logger.info(f"Сообщение {message_id} удалено из чата {chat_id}")
        return True

    async def close(self):
        """Закрытие HTTP клиента."""
        if self._client:
            await self._client.aclose()
            self._client = None
