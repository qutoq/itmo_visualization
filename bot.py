import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import Config, load_config
from src.handlers import echo, main_end


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s "
        "[%(asctime)s] - %(name)s - %(message)s",
    )

    logger.info("Starting bot")

    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    dp: Dispatcher = Dispatcher()

    #dp.include_router(echo.router)
    dp.include_router(main_end.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped.")
