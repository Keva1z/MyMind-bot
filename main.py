from aiogram import Bot, Dispatcher
from bot.config import config
from bot.handlers import setup_handlers
from database.main import async_main
from service.schedule.scheduler import DailyScheduler

import logging, asyncio

bot = Bot(token=config.bot_token)
dp = Dispatcher(bot=bot)

logging.basicConfig(level=logging.INFO)

async def on_startup():
    await async_main() # Initialize database
    scheduler = DailyScheduler(bot)

    setup_handlers(dp)
    logging.info("Bot started")

async def main() -> None:
    dp.startup.register(on_startup)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())