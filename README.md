# Telegram MCP Server

[![CI](https://github.com/creafly/telegram-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/creafly/telegram-mcp/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/creafly/telegram-mcp)](https://github.com/creafly/telegram-mcp/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/creafly/telegram-mcp)](https://github.com/creafly/telegram-mcp/pulls)

MCP server for working with Telegram Bot API.

## Features

- Send text messages with formatting (HTML, Markdown)
- Receive updates (incoming messages)
- Send photos and documents
- Edit and delete messages
- Get information about chats and bot

## Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
uv sync
```

## Configuration

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO
```

Get your bot token from [@BotFather](https://t.me/BotFather) in Telegram.

## Running

```bash
# Start the server
uv run python -m src.entrypoints.server
```

## Docker

```bash
# Build image
make build

# Run container
docker run -p 8000:8000 -e TELEGRAM_BOT_TOKEN=your_token telegram-mcp:latest
```

## Tools

| Tool             | Description           |
| ---------------- | --------------------- |
| `send_message`   | Send a text message   |
| `get_updates`    | Get incoming messages |
| `get_chat`       | Get chat information  |
| `get_me`         | Get bot information   |
| `send_photo`     | Send a photo          |
| `send_document`  | Send a document       |
| `edit_message`   | Edit a message        |
| `delete_message` | Delete a message      |

## Development

```bash
# Install dev dependencies
uv sync --group dev

# Run linting
make lint

# Run tests
make test
```

## Environment Variables

| Variable                | Description           | Default                  |
| ----------------------- | --------------------- | ------------------------ |
| `TELEGRAM_BOT_TOKEN`    | Bot token (required)  | -                        |
| `TELEGRAM_API_BASE_URL` | API base URL          | https://api.telegram.org |
| `PORT`                  | Server port           | 8000                     |
| `HOST`                  | Server host           | 0.0.0.0                  |
| `LOG_LEVEL`             | Logging level         | INFO                     |
| `MAX_MESSAGE_LENGTH`    | Max message length    | 4096                     |
| `DEFAULT_PARSE_MODE`    | Default parse mode    | HTML                     |
| `REQUEST_TIMEOUT`       | Request timeout (sec) | 30                       |

## License

MIT
