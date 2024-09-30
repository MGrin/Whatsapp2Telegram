from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)


class TelegramBot:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.application = Application.builder().token(self.token).build()
        self.replies: list[dict[str, str]] = []

    async def start(self):
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )
        await self.application.initialize()
        await self.application.start()
        if self.application.updater:
            await self.application.updater.start_polling()
        else:
            print("Warning: Application updater is None. Polling not started.")

    async def stop(self):
        await self.application.stop()
        await self.application.shutdown()

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message:
            await update.message.reply_text("WhatsApp to Telegram forwarder is active.")
        elif update.callback_query:
            await update.callback_query.answer(
                "WhatsApp to Telegram forwarder is active."
            )

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if (
            update.message
            and update.message.chat
            and update.message.chat.id == int(self.chat_id)
        ):
            if not update.message.reply_to_message or not update.message.text:
                self.replies.append(
                    {
                        "chat": "General",
                        "text": "Unhandled message: No reply to message or text",
                    }
                )
                return

            text = update.message.text
            reply_message = update.message.reply_to_message
            if not reply_message.text:
                self.replies.append(
                    {
                        "chat": "General",
                        "text": "Unhandled message: No text in the reply to message",
                    }
                )
                return

            from_chat = reply_message.text.split("\n")[0].split(":")[1].strip()
            if not from_chat:
                self.replies.append(
                    {
                        "chat": "General",
                        "text": "Unhandled message: No chat name found in the reply to message",
                    }
                )
                return

            self.replies.append(
                {
                    "chat": from_chat,
                    "text": text,
                }
            )

    async def forward_message(self, message: dict[str, str]) -> None:
        await self.application.bot.send_message(
            chat_id=self.chat_id,
            text=f"From: {message['chat']}\nMessage:\n{message['text']}",
        )

    async def send_qr_code(self, qr_image_bytes: bytes):
        await self.application.bot.send_photo(
            chat_id=self.chat_id,
            photo=qr_image_bytes,
            caption="Scan this QR code to authenticate WhatsApp",
        )

    def get_replies(self):
        replies = self.replies
        self.replies = []
        return replies
