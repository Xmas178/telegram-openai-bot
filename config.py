"""
Configuration module for Telegram Bot
Validates and provides access to environment variables
Author: Sami (CodeNob Dev)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BotConfig:
    """
    Configuration class that loads and validates environment variables
    """

    def __init__(self):
        """Initialize configuration from environment variables"""
        # Telegram configuration
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

        # OpenAI configuration
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.openai_max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "150"))
        self.openai_temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))

        # Rate limiting configuration
        self.max_requests_per_minute = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
