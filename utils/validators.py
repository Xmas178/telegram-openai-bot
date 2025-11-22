"""
Input validation utilities for Telegram bot
Ensures all user input is safe and within acceptable limits
Author: Sami (CodeNob Dev)
"""

import re
from typing import Tuple


class InputValidator:
    """
    Validates and sanitizes user input to prevent security issues

    Security measures:
    - Maximum message length enforcement
    - HTML/script tag stripping
    - Command injection prevention
    - SQL injection pattern detection
    """

    # Maximum allowed message length
    MAX_MESSAGE_LENGTH = 500

    # Patterns that could indicate malicious input
    DANGEROUS_PATTERNS = [
        r"<script",  # XSS attempt
        r"javascript:",  # JavaScript injection
        r"on\w+\s*=",  # Event handler injection (onclick=, onerror=, etc.)
        r"DROP\s+TABLE",  # SQL injection
        r"DELETE\s+FROM",  # SQL injection
        r"INSERT\s+INTO",  # SQL injection
        r"UPDATE\s+\w+\s+SET",  # SQL injection
        r";.*rm\s+-rf",  # Command injection
        r"&&.*rm\s+-rf",  # Command injection
        r"\|\|.*rm\s+-rf",  # Command injection
    ]

    @staticmethod
    def validate_message(text: str) -> Tuple[bool, str, str]:
        """
        Validate and sanitize user message

        Args:
            text: Raw user input message

        Returns:
            Tuple of (is_valid, cleaned_text, error_message)
            - is_valid: True if message passes validation
            - cleaned_text: Sanitized message (empty if invalid)
            - error_message: Explanation if invalid (empty if valid)
        """
        # Check if message is empty
        if not text or not text.strip():
            return False, "", "Message cannot be empty"

        # Strip leading/trailing whitespace
        cleaned = text.strip()

        # Check message length
        if len(cleaned) > InputValidator.MAX_MESSAGE_LENGTH:
            return (
                False,
                "",
                f"Message too long (max {InputValidator.MAX_MESSAGE_LENGTH} characters)",
            )

        # Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                return False, "", "Message contains potentially dangerous content"

        # Remove HTML tags for safety
        cleaned = InputValidator._strip_html(cleaned)

        # All checks passed
        return True, cleaned, ""

    @staticmethod
    def _strip_html(text: str) -> str:
        """
        Remove HTML tags from text

        Args:
            text: Text that may contain HTML

        Returns:
            Text with HTML tags removed
        """
        # Remove all HTML tags
        cleaned = re.sub(r"<[^>]+>", "", text)
        return cleaned

    @staticmethod
    def validate_command(command: str) -> bool:
        """
        Validate that a command is a legitimate bot command

        Args:
            command: Command string (e.g., "/start", "/help")

        Returns:
            True if command is valid format
        """
        # Valid command format: /commandname (lowercase letters only)
        pattern = r"^/[a-z_]+$"
        return bool(re.match(pattern, command))

    @staticmethod
    def sanitize_for_logging(text: str, max_length: int = 100) -> str:
        """
        Sanitize text for safe logging (remove sensitive data, truncate)

        Args:
            text: Text to log
            max_length: Maximum length of logged text

        Returns:
            Sanitized text safe for logging
        """
        # Remove potential API keys, tokens, passwords
        sanitized = re.sub(r"sk-[a-zA-Z0-9-_]+", "[REDACTED_API_KEY]", text)
        sanitized = re.sub(r"\b\d{10,}\b", "[REDACTED_NUMBER]", sanitized)
        sanitized = re.sub(
            r"password[:\s=]+\S+", "password:[REDACTED]", sanitized, flags=re.IGNORECASE
        )

        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."

        return sanitized


# Test the validator when running this file directly
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING INPUT VALIDATOR")
    print("=" * 60)

    # Test cases
    test_cases = [
        ("Hello, how are you?", True, "Valid message"),
        ("", False, "Empty message"),
        ("A" * 600, False, "Message too long"),
        ("<script>alert('xss')</script>", False, "XSS attempt"),
        ("DROP TABLE users;", False, "SQL injection"),
        ("Normal message with numbers 123", True, "Valid with numbers"),
        ("javascript:alert(1)", False, "JavaScript injection"),
        ("Hello <b>world</b>", True, "HTML stripped but valid"),
    ]

    print("\n📋 Running test cases:\n")

    for i, (test_input, expected_valid, description) in enumerate(test_cases, 1):
        is_valid, cleaned, error = InputValidator.validate_message(test_input)

        # Check if result matches expectation
        status = "✅ PASS" if is_valid == expected_valid else "❌ FAIL"

        print(f"Test {i}: {description}")
        print(f"  Input: '{test_input[:50]}{'...' if len(test_input) > 50 else ''}'")
        print(f"  Expected: {'Valid' if expected_valid else 'Invalid'}")
        print(f"  Result: {'Valid' if is_valid else 'Invalid'} - {status}")
        if not is_valid:
            print(f"  Error: {error}")
        if is_valid and cleaned != test_input:
            print(f"  Cleaned: '{cleaned}'")
        print()

    print("=" * 60)
    print("🧪 TESTING COMMAND VALIDATOR")
    print("=" * 60)

    commands = [
        ("/start", True),
        ("/help", True),
        ("/reset", True),
        ("/Start", False),  # Uppercase not allowed
        ("start", False),  # Missing slash
        ("/test123", False),  # Numbers not allowed
        ("/test_command", True),  # Underscores allowed
    ]

    print("\n📋 Running command tests:\n")

    for cmd, expected in commands:
        result = InputValidator.validate_command(cmd)
        status = "✅ PASS" if result == expected else "❌ FAIL"
        print(f"Command: {cmd:20} Expected: {expected:5} Result: {result:5} {status}")

    print("\n" + "=" * 60)
    print("✅ ALL VALIDATOR TESTS COMPLETE")
    print("=" * 60)
