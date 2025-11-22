"""
Configuration module for Telegram OpenAI Bot
Handles environment variables, validation, and security settings
Author: Sami (CodeNob Dev)
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class BotConfig:
    """
    Bot configuration class with validation

    Attributes:
        telegram_token: Telegram bot API token
        openai_api_key: OpenAI API key
        openai_model: OpenAI model name (default: gpt-5-nano)
        max_tokens: Maximum tokens per response
        temperature: Response creativity (0.0-1.0)
        max_requests_per_minute: Rate limiting threshold
    """

    telegram_token: str
    openai_api_key: str
    openai_model: str = "gpt-5-nano"
    max_tokens: int = 150
    temperature: float = 0.7
    max_requests_per_minute: int = 10

    def __post_init__(self):
        """Validate configuration after initialization"""
        self._validate_tokens()
        self._validate_openai_params()
        self._validate_rate_limit()

    def _validate_tokens(self):
        """
        Validate that required API tokens are present and properly formatted

        Raises:
            ValueError: If tokens are missing or invalid
        """
        # Check Telegram token
        if not self.telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is missing in .env file")

        if not self.telegram_token.count(":") == 1:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN format is invalid (should be: 123456:ABC-DEF...)"
            )

        # Check OpenAI key
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is missing in .env file")

        if not self.openai_api_key.startswith("sk-"):
            raise ValueError(
                "OPENAI_API_KEY format is invalid (should start with 'sk-')"
            )

    def _validate_openai_params(self):
        """
        Validate OpenAI parameters are within acceptable ranges

        Raises:
            ValueError: If parameters are out of range
        """
        # Validate model name
        valid_models = [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]

        if self.openai_model not in valid_models:
            raise ValueError(f"Invalid OpenAI model. Must be one of: {valid_models}")

        # Validate max_tokens
        if not 1 <= self.max_tokens <= 2000:
            raise ValueError("max_tokens must be between 1 and 2000")

        # Validate temperature
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")

    def _validate_rate_limit(self):
        """
        Validate rate limiting configuration

        Raises:
            ValueError: If rate limit is invalid
        """
        if not 1 <= self.max_requests_per_minute <= 100:
            raise ValueError("max_requests_per_minute must be between 1 and 100")


def load_config() -> BotConfig:
    """
    Load and validate bot configuration from environment variables

    Returns:
        BotConfig: Validated configuration object

    Raises:
        ValueError: If any configuration is invalid
    """
    try:
        config = BotConfig(
            telegram_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-5-nano"),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "150")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_requests_per_minute=int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10")),
        )

        print("✅ Configuration loaded and validated successfully")
        return config

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        raise
    except Exception as e:
        print(f"❌ Unexpected error loading configuration: {e}")
        raise


# Test configuration when running this file directly
if __name__ == "__main__":
    print("=" * 50)
    print("🔍 STARTING CONFIGURATION TEST")
    print("=" * 50)

    try:
        print("\n📂 Step 1: Loading environment variables...")
        load_dotenv()
        print("✅ Environment variables loaded")

        print("\n📂 Step 2: Creating configuration object...")
        config = load_config()

        print("\n" + "=" * 50)
        print("📋 CONFIGURATION SUMMARY")
        print("=" * 50)
        print(f"Telegram Token: {config.telegram_token[:20]}...")
        print(f"OpenAI Model: {config.openai_model}")
        print(f"Max Tokens: {config.max_tokens}")
        print(f"Temperature: {config.temperature}")
        print(f"Rate Limit: {config.max_requests_per_minute} req/min")
        print("=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("=" * 50)

    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ CONFIGURATION ERROR")
        print("=" * 50)
        print(f"Error: {e}")
        print("\n📋 Full traceback:")
        import traceback

        traceback.print_exc()
        print("=" * 50)
