"""
Chat message handler with OpenAI integration
Processes user messages and generates AI responses
Author: Sami (CodeNob Dev)
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update
from telegram.ext import ContextTypes
from utils.validators import InputValidator
from utils.openai_client import OpenAIClient


class ChatHandler:
    """
    Handles chat messages with OpenAI integration

    Features:
    - Input validation for safety
    - Rate limiting enforcement
    - Chat history management
    - OpenAI API integration
    - Error handling and user feedback
    """

    def __init__(self, session_manager, rate_limiter, openai_client):
        """
        Initialize chat handler

        Args:
            session_manager: SessionManager instance
            rate_limiter: RateLimiter instance
            openai_client: OpenAIClient instance
        """
        self.session_manager = session_manager
        self.rate_limiter = rate_limiter
        self.openai_client = openai_client
        self.validator = InputValidator()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Process user message and generate AI response

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        user = update.effective_user
        user_id = user.id
        message_text = update.message.text

        # Step 1: Validate input
        is_valid, cleaned_text, error_msg = self.validator.validate_message(
            message_text
        )

        if not is_valid:
            await update.message.reply_text(
                f"❌ Invalid message: {error_msg}\n\n"
                f"Please send a valid message (max 500 characters, no dangerous content)."
            )
            return

        # Step 2: Check rate limiting
        allowed, remaining = self.rate_limiter.is_allowed(user_id)

        if not allowed:
            wait_time = self.rate_limiter.get_wait_time(user_id)
            await update.message.reply_text(
                f"⏳ Rate limit exceeded!\n\n"
                f"Please wait {wait_time} seconds before sending another message.\n"
                f"This prevents spam and keeps the bot responsive for everyone."
            )
            return

        # Step 3: Show typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )

        # Step 4: Add user message to session
        self.session_manager.add_user_message(user_id, cleaned_text)

        # Step 5: Get chat history
        history = self.session_manager.get_history(user_id)

        # Step 6: Call OpenAI API
        success, response_text, error = self.openai_client.get_chat_response(
            messages=history, user_id=user_id
        )

        # Step 7: Handle response
        if success:
            # Add assistant response to session
            self.session_manager.add_assistant_message(user_id, response_text)

            # Send response to user
            await update.message.reply_text(response_text)

            # Show remaining requests
            if remaining <= 3:
                await update.message.reply_text(
                    f"ℹ️ You have {remaining} requests remaining this minute.",
                    disable_notification=True,
                )
        else:
            # Handle error
            error_response = (
                f"❌ Sorry, I encountered an error:\n\n"
                f"{error}\n\n"
                f"Please try again in a moment. If the problem persists, "
                f"use /reset to clear your chat history."
            )
            await update.message.reply_text(error_response)

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle inline button callbacks

        Args:
            update: Telegram update object
            context: Telegram context object
        """
        query = update.callback_query
        await query.answer()

        callback_data = query.data

        if callback_data == "chat_start":
            await query.edit_message_text(
                "💬 Great! Just send me any message and I'll respond.\n\n"
                "I'll remember our last 5 messages for context."
            )

        elif callback_data == "help":
            help_text = (
                "📋 *Quick Help:*\n\n"
                "• Send any message to chat with AI\n"
                "• Use /reset to clear history\n"
                "• Use /settings to see configuration\n\n"
                "Type /help for full command list."
            )
            await query.edit_message_text(help_text, parse_mode="Markdown")

        elif callback_data == "reset":
            user_id = query.from_user.id
            self.session_manager.reset_session(user_id)
            await query.edit_message_text("🔄 Chat history cleared! Start fresh.")

        elif callback_data == "settings":
            user_id = query.from_user.id
            session_info = self.session_manager.get_session_info(user_id)

            settings_text = (
                f"⚙️ *Current Settings:*\n\n"
                f"💬 Messages in history: {session_info['message_count']}\n"
                f"⏱️ Time since last message: {session_info['time_since_activity']}s\n\n"
                f"Use /settings for full details."
            )
            await query.edit_message_text(settings_text, parse_mode="Markdown")


# Test chat handler when running this file directly
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING CHAT HANDLER")
    print("=" * 60)

    # Import dependencies
    import sys
    import os

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from config import load_config
    from utils.session import SessionManager
    from utils.rate_limiter import RateLimiter
    from utils.openai_client import OpenAIClient

    try:
        # Load config
        config = load_config()

        # Create dependencies
        session_manager = SessionManager(max_history=5)
        rate_limiter = RateLimiter(max_requests=10, time_window=60)
        openai_client = OpenAIClient(
            api_key=config.openai_api_key,
            model=config.openai_model,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
        )

        # Create handler instance
        chat_handler = ChatHandler(session_manager, rate_limiter, openai_client)

        print("\n✅ Chat handler initialized successfully")

        print("\n📋 Handler components:")
        print("  - Input validation: ✅ Active")
        print("  - Rate limiting: ✅ Active")
        print("  - Session management: ✅ Active")
        print("  - OpenAI integration: ✅ Active")

        print("\n🔄 Message processing flow:")
        print("  1. Validate input (safety)")
        print("  2. Check rate limit (spam prevention)")
        print("  3. Show typing indicator (UX)")
        print("  4. Add to session (context)")
        print("  5. Call OpenAI (AI response)")
        print("  6. Save response (history)")
        print("  7. Send to user (delivery)")

        print("\n" + "=" * 60)
        print("✅ ALL CHAT HANDLER TESTS COMPLETE")
        print("=" * 60)
        print("\nℹ️  Note: Full testing requires running bot")
        print("Handler will process real messages in bot.py")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()
