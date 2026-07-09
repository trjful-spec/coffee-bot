import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from services.reminder_service import poll_reminder_worker
from config import config
from database.db import init_db
from handlers import register_handlers
from utils.logging import setup_logging


async def on_startup(bot: Bot):
    # Запускаем воркер в бэкграунде (он будет крутиться в бесконечном цикле asyncio)
    asyncio.create_task(poll_reminder_worker(bot))


async def main():
    setup_logging()

    await init_db()

    logger = logging.getLogger(__name__)

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    dp = Dispatcher()

    # СВЯЗЫВАЕМ ФУНКЦИЮ STARTUP С ДИСПЕТЧЕРОМ
    dp.startup.register(on_startup)

    register_handlers(dp)

    logger.info("Coffee Bot started")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())