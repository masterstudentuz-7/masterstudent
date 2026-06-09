import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import init_db
from handlers import setup_routers
from middlewares.antiflood import AntiFloodMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main():
    """Main bot function."""
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Create bot instance
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Create dispatcher
    dp = Dispatcher(storage=MemoryStorage())
    
    # Add middleware
    dp.message.middleware(AntiFloodMiddleware(rate_limit=0.5))
    
    # Setup routers
    main_router = setup_routers()
    dp.include_router(main_router)
    
    # Start polling
    logger.info("Bot starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
