import logging
import sys
import os
import nest_asyncio

nest_asyncio.apply()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram.ext import (
    Application, MessageHandler, CallbackQueryHandler,
    CommandHandler, filters
)
from config import TELEGRAM_TOKEN
from database import init_db
from handlers.start import get_onboarding_handler
from handlers.analysis import handle_photo
from handlers.menu import handle_menu, handle_text, admin_stats
from handlers.privacy import privacy, delete_my_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("errors.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    import asyncio

    async def post_init(app):
        await init_db()
        logger.info("✅ База данных инициализирована")

    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(get_onboarding_handler())
    app.add_handler(CommandHandler("privacy", privacy))
    app.add_handler(CommandHandler("delete_my_data", delete_my_data))
    app.add_handler(CommandHandler("admin", admin_stats))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_menu))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    logger.info("🚀 FizAI запущен!")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app.run_polling(drop_pending_updates=True))

if __name__ == "__main__":
    main()