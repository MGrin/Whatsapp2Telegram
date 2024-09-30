import os
import asyncio
import signal
from dotenv import load_dotenv
from whatsapp2telegram.whatsapp import WhatsAppClient
from whatsapp2telegram.telegram_bot import TelegramBot

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def shutdown(
    signal: signal.Signals,
    loop: asyncio.AbstractEventLoop,
    whatsapp_client: WhatsAppClient,
    telegram_bot: TelegramBot,
) -> None:
    print(f"Received exit signal {signal.name}...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    whatsapp_client.stop()
    await telegram_bot.stop()
    loop.stop()


async def main():
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set in the environment variables."
        )

    telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    whatsapp_client = WhatsAppClient(telegram_bot)

    loop = asyncio.get_running_loop()
    signals = (signal.SIGHUP, signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s,
            lambda s=s: asyncio.create_task(
                shutdown(s, loop, whatsapp_client, telegram_bot)
            ),
        )

    try:
        await telegram_bot.start()
        await whatsapp_client.start()

        while True:
            new_messages = await whatsapp_client.get_new_messages()
            for message in new_messages:
                await telegram_bot.forward_message(message)

            replies = telegram_bot.get_replies()
            for reply in replies:
                await whatsapp_client.send_message(reply["chat"], reply["text"])

            await asyncio.sleep(2)

    except asyncio.CancelledError:
        pass
    finally:
        print("Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
