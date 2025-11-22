"""
Command handlers for Telegram bot
Handles all bot commands (/start, /help, /reset, etc.)
Author: Sami (CodeNob Dev)
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


class CommandHandlers:
    """
    Handles all Telegram bot commands

    Commands:
    - /start: Welcome message with quick actions
    - /help: List of available commands
    - /reset: Clear chat history
    - /settings: Show current AI settings
    - /notify: Test notification (demo feature)
    """

    def __init__(self, session_manager, rate_limiter, config):
        """
        Initialize command handlers

        Args:
            session_manager: SessionManager instance for chat history
            rate_limiter: RateLimiter instance for spam protection
            config: BotConfig instance with settings
        """
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
        self.config = config

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /start command - welcome message

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user = update.effective_user
        user_id = user.id

        # Create inline keyboard with quick actions
        keyboard = [
            [
                InlineKeyboardButton("💬 Chat with AI", callback_data="chat_start"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
            [
                InlineKeyboardButton("🔄 Reset Chat", callback_data="reset"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings"),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Welcome message
        welcome_text = (
            f"👋 Hello {user.first_name}!\n\n"
            f"I'm an AI-powered chatbot using OpenAI's {self.config.openai_model} model.\n\n"
            f"🤖 Just send me any message and I'll respond!\n\n"
            f"📋 Use /help to see all available commands."
        )

        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

        # Reset session for new start
        self.session_manager.reset_session(user_id)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /help command - list available commands

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        help_text = (
            "📋 *Available Commands:*\n\n"
            "/start - Start the bot and see welcome message\n"
            "/help - Show this help message\n"
            "/reset - Clear your chat history\n"
            "/settings - View current AI settings\n"
            "/notify - Test notification feature\n\n"
            "💬 *How to use:*\n"
            "Just send any message and I'll respond using AI!\n\n"
            "⚡ *Features:*\n"
            "• Context-aware responses (remembers last 5 messages)\n"
            "• Rate limiting for spam protection\n"
            "• Secure API key handling\n"
            "• Input validation for safety\n\n"
            "🛡️ *Privacy:*\n"
            "Your conversations are stored only in memory and cleared after 1 hour of inactivity."
        )

        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def reset_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /reset command - clear chat history

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user_id = update.effective_user.id

        # Reset session
        self.session_manager.reset_session(user_id)

        # Also reset rate limiter for this user
        self.rate_limiter.reset_user(user_id)

        reset_text = (
            "🔄 *Chat Reset Complete*\n\n"
            "Your conversation history has been cleared.\n"
            "Rate limits have been reset.\n\n"
            "You can start a fresh conversation now!"
        )

        await update.message.reply_text(reset_text, parse_mode="Markdown")

    async def settings_command(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handle /settings command - show current configuration

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user_id = update.effective_user.id

        # Get session info
        session_info = self.session_manager.get_session_info(user_id)

        settings_text = (
            "⚙️ *Current Settings:*\n\n"
            f"🤖 *AI Model:* {self.config.openai_model}\n"
            f"📊 *Max Tokens:* {self.config.max_tokens}\n"
            f"🌡️ *Temperature:* {self.config.temperature}\n"
            f"💬 *Chat History:* {session_info['message_count']}/{self.config.max_tokens} messages\n"
            f"⏱️ *Rate Limit:* {self.config.max_requests_per_minute} messages/minute\n\n"
            f"ℹ️ *Session Info:*\n"
            f"Messages in history: {session_info['message_count']}\n"
            f"Time since last message: {session_info['time_since_activity']}s\n"
        )

        await update.message.reply_text(settings_text, parse_mode="Markdown")

    async def notify_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle /notify command - test notification feature

        This is a demo feature showing how the bot could receive
        notifications from external systems (webhooks, APIs, sensors, etc.)

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        # Simulate notification from external system
        notification_text = (
            "🔔 *Test Notification*\n\n"
            "This is a simulated notification from an external system.\n\n"
            "📡 *Example Use Cases:*\n"
            "• Price alerts (crypto, stocks)\n"
            "• Weather warnings\n"
            "• Server monitoring alerts\n"
            "• Sensor data (IoT devices)\n"
            "• GitHub/GitLab events\n"
            "• Custom webhooks\n\n"
            "💡 *How it works:*\n"
            "External systems can send POST requests to a webhook endpoint, "
            "and the bot forwards them as Telegram messages.\n\n"
            "⚡ This feature is included in Premium tier on Fiverr!"
        )

        await update.message.reply_text(notification_text, parse_mode="Markdown")


# Test command handlers when running this file directly
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING COMMAND HANDLERS")
    print("=" * 60)

    # Import dependencies
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from config import load_config
    from utils.session import SessionManager
    from utils.rate_limiter import RateLimiter

    try:
        # Load config
        config = load_config()

        # Create dependencies
        session_manager = SessionManager(max_history=5)
        rate_limiter = RateLimiter(max_requests=10, time_window=60)

        # Create handler instance
        handlers = CommandHandlers(session_manager, rate_limiter, config)

        print("\n✅ Command handlers initialized successfully")

        print("\n📋 Available command handlers:")
        print("  - start_command: Welcome message with inline buttons")
        print("  - help_command: Show available commands")
        print("  - reset_command: Clear chat history")
        print("  - settings_command: Display current settings")
        print("  - notify_command: Test notification feature")

        print("\n" + "=" * 60)
        print("✅ ALL COMMAND HANDLER TESTS COMPLETE")
        print("=" * 60)
        print("\nℹ️  Note: Full testing requires running bot")
        print("These handlers will be connected in bot.py")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
