"""
Telegram OpenAI Bot - Production Ready
Secure AI-powered bot with rate limiting and session management
Author: Sami (crake178)
Telegram OpenAI Bot - Auto-deployed via GitHub Actions
"""

import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from dotenv import load_dotenv

from config import BotConfig
from handlers.commands import CommandHandlers
from handlers.chat import ChatHandler
from utils.rate_limiter import RateLimiter
from utils.session_manager import SessionManager
from utils.openai_client import OpenAIClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle errors in the bot
    Logs errors without exposing sensitive information to users
    """
    logger.error(f"Exception while handling an update: {context.error}")

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, something went wrong. Please try again later."
        )


def main():
    """
    Main function to start the bot
    Sets up handlers and starts polling
    """
    try:
        # Validate configuration
        config = BotConfig()
        logger.info("Configuration validated successfully")

        # Create application
        application = Application.builder().token(config.telegram_token).build()

        # Initialize dependencies
        rate_limiter = RateLimiter(max_requests=config.max_requests_per_minute)
        session_manager = SessionManager(max_history=5)

        # Create OpenAI client
        openai_client = OpenAIClient(
            api_key=config.openai_api_key,
            model=config.openai_model,
            max_tokens=config.openai_max_tokens,
            temperature=config.openai_temperature,
        )

        # Initialize handlers
        command_handlers = CommandHandlers(
            session_manager=session_manager, rate_limiter=rate_limiter, config=config
        )

        chat_handler = ChatHandler(
            session_manager=session_manager,
            rate_limiter=rate_limiter,
            openai_client=openai_client,
        )

        # Register command handlers
        application.add_handler(CommandHandler("start", command_handlers.start_command))
        application.add_handler(CommandHandler("help", command_handlers.help_command))
        application.add_handler(
            CommandHandler("settings", command_handlers.settings_command)
        )
        application.add_handler(CommandHandler("reset", command_handlers.reset_command))

        # Register message handler (for all non-command messages)
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, chat_handler.handle_message)
        )

        # Register callback query handler (for inline buttons)
        application.add_handler(CallbackQueryHandler(chat_handler.handle_callback))

        # Register error handler
        application.add_error_handler(error_handler)

        # Start the bot
        logger.info("Bot started successfully!")
        logger.info("Press Ctrl+C to stop")

        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ FATAL ERROR: {str(e)}")
        logger.error("=" * 60)
        raise


if __name__ == "__main__":
    main()
