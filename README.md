# WhatsApp to Telegram

A simple server to forward messages from WhatsApp to Telegram and vice versa using Selenium and Telegram Bot API.

For a detailed explanation of this project, check out the [WhatsApp2Telegram: Bridging Two Messaging Worlds](https://medium.com/@mgrin/whatsapp2telegram-8ebfb3114904) article on Medium.

## Features

- Forward messages from WhatsApp to Telegram
- Send replies from Telegram to WhatsApp

## Installation

```bash
poetry install
```

## Usage

```bash
poetry run python main.py
```

## Whatsapp Authentication

The script uses Selenium to authenticate with WhatsApp Web. The authentication is done by scanning the QR code sent to your telegram on the first run.

## Telegram Authentication

You should create a telegram bot and get the token from [@BotFather](https://t.me/botfather), then get your chat id from [@userinfobot](https://t.me/userinfobot) and set them in the `.env` file.

- `TELEGRAM_BOT_TOKEN`: The token of the Telegram bot.
- `TELEGRAM_CHAT_ID`: The ID of the Telegram chat.
