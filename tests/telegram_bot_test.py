import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update
from telegram.ext import ContextTypes
from whatsapp2telegram.telegram_bot import TelegramBot


@pytest.fixture
def telegram_bot():
    return TelegramBot("test_token", "123456")


@pytest.mark.asyncio
async def test_start(telegram_bot: TelegramBot):
    telegram_bot.application.add_handler = MagicMock()
    telegram_bot.application.initialize = AsyncMock()
    telegram_bot.application.start = AsyncMock()
    telegram_bot.application.updater = MagicMock()
    telegram_bot.application.updater.start_polling = AsyncMock()

    await telegram_bot.start()

    assert telegram_bot.application.add_handler.call_count == 2
    telegram_bot.application.initialize.assert_called_once()
    telegram_bot.application.start.assert_called_once()
    telegram_bot.application.updater.start_polling.assert_called_once()


@pytest.mark.asyncio
async def test_stop(telegram_bot: TelegramBot):
    telegram_bot.application.stop = AsyncMock()
    telegram_bot.application.shutdown = AsyncMock()

    await telegram_bot.stop()

    telegram_bot.application.stop.assert_called_once()
    telegram_bot.application.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_start_command(telegram_bot: TelegramBot):
    update = MagicMock(spec=Update)
    update.message.reply_text = AsyncMock()
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await telegram_bot._start_command(update, context)  # type: ignore

    update.message.reply_text.assert_called_once_with(
        "WhatsApp to Telegram forwarder is active."
    )


@pytest.mark.asyncio
async def test_handle_message(telegram_bot: TelegramBot):
    update = MagicMock(spec=Update)
    update.message.chat.id = int(telegram_bot.chat_id)
    update.message.text = "Test reply"
    update.message.reply_to_message.text = "From: TestChat\nOriginal message"
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)

    await telegram_bot._handle_message(update, context)  # type: ignore

    assert len(telegram_bot.replies) == 1
    assert telegram_bot.replies[0] == {"chat": "TestChat", "text": "Test reply"}


@pytest.mark.asyncio
async def test_forward_message(telegram_bot: TelegramBot):
    mock_bot = AsyncMock()
    telegram_bot.application.bot = mock_bot
    message = {"chat": "TestChat", "text": "Test message"}

    await telegram_bot.forward_message(message)

    mock_bot.send_message.assert_called_once_with(
        chat_id=telegram_bot.chat_id, text="From: TestChat\nMessage:\nTest message"
    )


@pytest.mark.asyncio
async def test_send_qr_code(telegram_bot: TelegramBot):
    mock_bot = AsyncMock()
    telegram_bot.application.bot = mock_bot
    qr_image_bytes = b"fake_qr_code_bytes"

    await telegram_bot.send_qr_code(qr_image_bytes)

    mock_bot.send_photo.assert_called_once_with(
        chat_id=telegram_bot.chat_id,
        photo=qr_image_bytes,
        caption="Scan this QR code to authenticate WhatsApp",
    )


def test_get_replies(telegram_bot: TelegramBot):
    telegram_bot.replies = [
        {"chat": "TestChat1", "text": "Test1"},
        {"chat": "TestChat2", "text": "Test2"},
    ]

    replies = telegram_bot.get_replies()

    assert replies == [
        {"chat": "TestChat1", "text": "Test1"},
        {"chat": "TestChat2", "text": "Test2"},
    ]
    assert telegram_bot.replies == []
