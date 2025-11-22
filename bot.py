"""
Main Telegram bot application with OpenAI integration
Combines all modules into a working chatbot
Author: Sami (CodeNob Dev)
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Import configuration and utilities
from config import load_config
from utils.session import SessionManager
from utils.rate_limiter import RateLimiter
from utils.openai_client import OpenAIClient

# Import handlers
from handlers.commands import CommandHandlers
from handlers.chat import ChatHandler


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Main Telegram bot class

    Orchestrates all components:
    - Configuration management
    - Session management
    - Rate limiting
    - OpenAI integration
    - Command handling
    - Message handling

    Security features:
    - Input validation on all messages
    - Rate limiting per user
    - Secure API key handling
    - Error handling and logging
    """

    def __init__(self):
        """Initialize bot with all components"""

        logger.info("=" * 60)
        logger.info("🤖 INITIALIZING TELEGRAM BOT")
        logger.info("=" * 60)

        # Load configuration
        logger.info("📋 Loading configuration...")
        self.config = load_config()
        logger.info("✅ Configuration loaded")

        # Initialize session manager
        logger.info("💾 Initializing session manager...")
        self.session_manager = SessionManager(
            max_history=5, session_timeout=3600  # 1 hour
        )
        logger.info("✅ Session manager ready")

        # Initialize rate limiter
        logger.info("🛡️ Initializing rate limiter...")
        self.rate_limiter = RateLimiter(
            max_requests=self.config.max_requests_per_minute, time_window=60
        )
        logger.info("✅ Rate limiter ready")

        # Initialize OpenAI client
        logger.info("🤖 Initializing OpenAI client...")
        self.openai_client = OpenAIClient(
            api_key=self.config.openai_api_key,
            model=self.config.openai_model,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
        )
        logger.info("✅ OpenAI client ready")

        # Initialize handlers
        logger.info("🎯 Initializing command handlers...")
        self.command_handlers = CommandHandlers(
            self.session_manager, self.rate_limiter, self.config
        )
        logger.info("✅ Command handlers ready")

        logger.info("💬 Initializing chat handler...")
        self.chat_handler = ChatHandler(
            self.session_manager, self.rate_limiter, self.openai_client
        )
        logger.info("✅ Chat handler ready")

        # Create application
        logger.info("🚀 Creating Telegram application...")
        self.application = (
            Application.builder().token(self.config.telegram_token).build()
        )
        logger.info("✅ Application created")

        # Register handlers
        self._register_handlers()

        logger.info("=" * 60)
        logger.info("✅ BOT INITIALIZATION COMPLETE")
        logger.info("=" * 60)

    def _register_handlers(self):
        """Register all command and message handlers"""

        logger.info("📝 Registering handlers...")

        # Command handlers
        self.application.add_handler(
            CommandHandler("start", self.command_handlers.start_command)
        )
        self.application.add_handler(
            CommandHandler("help", self.command_handlers.help_command)
        )
        self.application.add_handler(
            CommandHandler("reset", self.command_handlers.reset_command)
        )
        self.application.add_handler(
            CommandHandler("settings", self.command_handlers.settings_command)
        )
        self.application.add_handler(
            CommandHandler("notify", self.command_handlers.notify_command)
        )

        # Callback query handler (for inline buttons)
        self.application.add_handler(
            CallbackQueryHandler(self.chat_handler.handle_callback)
        )

        # Message handler (for chat messages)
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, self.chat_handler.handle_message
            )
        )

        # Error handler
        self.application.add_error_handler(self._error_handler)

        logger.info("✅ All handlers registered")

    async def _error_handler(self, update: Update, context):
        """
        Handle errors in bot updates

        Args:
            update: Telegram update that caused error
            context: Context with error information
        """
        logger.error(f"Update {update} caused error: {context.error}")

        # Try to notify user (if update has a message)
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An unexpected error occurred. Please try again later.\n"
                    "If the problem persists, use /reset to clear your session."
                )
            except Exception as e:
                logger.error(f"Failed to send error message to user: {e}")

    def run(self):
        """Start the bot using polling"""

        logger.info("=" * 60)
        logger.info("🚀 STARTING BOT")
        logger.info("=" * 60)
        logger.info(f"Model: {self.config.openai_model}")
        logger.info(f"Max tokens: {self.config.max_tokens}")
        logger.info(f"Temperature: {self.config.temperature}")
        logger.info(f"Rate limit: {self.config.max_requests_per_minute} req/min")
        logger.info("=" * 60)
        logger.info("✅ Bot is running! Press Ctrl+C to stop.")
        logger.info("=" * 60)

        # Start polling
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point for the bot"""

    try:
        # Create and run bot
        bot = TelegramBot()
        bot.run()

    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("🛑 Bot stopped by user")
        logger.info("=" * 60)

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ FATAL ERROR: {e}")
        logger.error("=" * 60)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
