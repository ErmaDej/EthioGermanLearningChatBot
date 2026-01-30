"""
EthioGerman Language School - Telegram AI Tutor Bot
Main entry point.
"""
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

from bot.config import Config
from bot.handlers.start import start_handler, help_handler, cancel_handler
from bot.handlers.menu import menu_handler, menu_callback_handler, settings_callback_handler
from bot.handlers.learn import learn_conversation_handler
from bot.handlers.exam import exam_conversation_handler
from bot.handlers.progress import progress_handler, progress_callback_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

# Reduce noise from httpx
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    """Handle errors in the bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to notify user
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "An error occurred. Please try again.\n"
                "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut."
            )
        except Exception:
            pass


def main() -> None:
    """Start the bot."""
    logger.info("Starting EthioGerman Language School Bot...")
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Add conversation handlers (must be added before other handlers)
    application.add_handler(learn_conversation_handler)
    application.add_handler(exam_conversation_handler)
    
    # Add command handlers
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(cancel_handler)
    application.add_handler(menu_handler)
    application.add_handler(progress_handler)
    
    # Add callback query handlers
    application.add_handler(menu_callback_handler)
    application.add_handler(settings_callback_handler)
    application.add_handler(progress_callback_handler)
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Add logging for all updates (for debugging)
    async def log_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info(f"Update received: ID={update.update_id}")
        if update.message:
            logger.info(f"Message: {update.message.text} from {update.effective_user.id}")
        elif update.callback_query:
            logger.info(f"Callback: {update.callback_query.data} from {update.effective_user.id}")
            
    application.add_handler(MessageHandler(filters.ALL, log_update), group=-1)

    # Add ping handler
    async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Pong!")
    application.add_handler(CommandHandler('ping', ping))
    
    # Start the bot
    logger.info("Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
