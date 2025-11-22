"""
Session management for chat history
Maintains conversation context for OpenAI API calls
Author: Sami (CodeNob Dev)
"""

from collections import deque
from typing import Dict, List, Deque
from dataclasses import dataclass
import time


@dataclass
class Message:
    """
    Represents a single message in chat history

    Attributes:
        role: Either 'user' or 'assistant'
        content: The message text
        timestamp: When message was created
    """

    role: str  # 'user' or 'assistant'
    content: str
    timestamp: float


class SessionManager:
    """
    Manages chat sessions and conversation history per user

    Features:
    - Stores last N messages per user
    - Automatic cleanup of old sessions
    - Thread-safe for single-process bots
    - Memory efficient with deque

    Security:
    - Limits history size to prevent memory bloat
    - Automatic expiry of inactive sessions
    - Per-user isolation
    """

    def __init__(self, max_history: int = 5, session_timeout: int = 3600):
        """
        Initialize session manager

        Args:
            max_history: Maximum messages to keep per user (default: 5)
            session_timeout: Seconds before inactive session expires (default: 3600 = 1 hour)
        """
        self.max_history = max_history
        self.session_timeout = session_timeout

        # Store conversation history per user
        # Key: user_id, Value: deque of Message objects
        self.sessions: Dict[int, Deque[Message]] = {}

        # Track last activity per user for cleanup
        self.last_activity: Dict[int, float] = {}

    def add_user_message(self, user_id: int, content: str):
        """
        Add a user message to chat history

        Args:
            user_id: Telegram user ID
            content: Message text from user
        """
        self._ensure_session_exists(user_id)

        message = Message(role="user", content=content, timestamp=time.time())

        self._add_message(user_id, message)

    def add_assistant_message(self, user_id: int, content: str):
        """
        Add an assistant (bot) message to chat history

        Args:
            user_id: Telegram user ID
            content: Response text from OpenAI
        """
        self._ensure_session_exists(user_id)

        message = Message(role="assistant", content=content, timestamp=time.time())

        self._add_message(user_id, message)

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """
        Get chat history formatted for OpenAI API

        Args:
            user_id: Telegram user ID

        Returns:
            List of message dicts in OpenAI format:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        self._ensure_session_exists(user_id)

        # Convert Message objects to OpenAI format
        history = [
            {"role": msg.role, "content": msg.content} for msg in self.sessions[user_id]
        ]

        return history

    def reset_session(self, user_id: int):
        """
        Clear all chat history for a user

        Args:
            user_id: Telegram user ID
        """
        if user_id in self.sessions:
            self.sessions[user_id].clear()

        self.last_activity[user_id] = time.time()

    def get_session_info(self, user_id: int) -> Dict:
        """
        Get information about user's session

        Args:
            user_id: Telegram user ID

        Returns:
            Dictionary with session statistics
        """
        self._ensure_session_exists(user_id)

        session = self.sessions[user_id]
        last_active = self.last_activity.get(user_id, 0)

        return {
            "message_count": len(session),
            "max_history": self.max_history,
            "last_activity": last_active,
            "time_since_activity": (
                int(time.time() - last_active) if last_active > 0 else 0
            ),
        }

    def cleanup_expired_sessions(self):
        """
        Remove sessions that have been inactive for longer than timeout

        This prevents memory bloat from users who don't return
        """
        current_time = time.time()
        expired_users = []

        for user_id, last_active in self.last_activity.items():
            if current_time - last_active > self.session_timeout:
                expired_users.append(user_id)

        # Remove expired sessions
        for user_id in expired_users:
            if user_id in self.sessions:
                del self.sessions[user_id]
            del self.last_activity[user_id]

        return len(expired_users)

    def get_stats(self) -> Dict:
        """
        Get overall session manager statistics

        Returns:
            Dictionary with global statistics
        """
        return {
            "active_sessions": len(self.sessions),
            "max_history_per_user": self.max_history,
            "session_timeout_seconds": self.session_timeout,
            "total_messages": sum(len(session) for session in self.sessions.values()),
        }

    def _ensure_session_exists(self, user_id: int):
        """
        Create session if it doesn't exist

        Args:
            user_id: Telegram user ID
        """
        if user_id not in self.sessions:
            self.sessions[user_id] = deque(maxlen=self.max_history)

        # Update last activity
        self.last_activity[user_id] = time.time()

    def _add_message(self, user_id: int, message: Message):
        """
        Add message to user's session

        Automatically maintains max_history limit using deque

        Args:
            user_id: Telegram user ID
            message: Message object to add
        """
        self.sessions[user_id].append(message)
        self.last_activity[user_id] = time.time()


# Test the session manager when running this file directly
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING SESSION MANAGER")
    print("=" * 60)

    # Create session manager with max 3 messages for testing
    manager = SessionManager(max_history=3, session_timeout=60)

    test_user = 123456

    print(f"\n📋 Test Configuration:")
    print(f"  Max history: 3 messages")
    print(f"  Session timeout: 60 seconds")
    print(f"  Test user ID: {test_user}\n")

    # Test 1: Add messages
    print("Test 1: Adding messages to session")
    manager.add_user_message(test_user, "Hello!")
    manager.add_assistant_message(test_user, "Hi there! How can I help?")
    manager.add_user_message(test_user, "What's the weather?")
    manager.add_assistant_message(test_user, "I don't have weather data.")

    history = manager.get_history(test_user)
    print(f"  Messages in history: {len(history)}")
    for i, msg in enumerate(history, 1):
        print(f"  {i}. {msg['role']:10} → {msg['content'][:40]}...")

    # Test 2: Exceed max history (should keep only last 3)
    print("\nTest 2: Adding message beyond max history")
    manager.add_user_message(test_user, "Tell me a joke")
    history = manager.get_history(test_user)
    print(f"  Messages after adding 5th: {len(history)} (should be 3)")
    print(f"  Oldest message: '{history[0]['content'][:40]}...'")

    # Test 3: Session info
    print("\nTest 3: Session information")
    info = manager.get_session_info(test_user)
    print(f"  Message count: {info['message_count']}")
    print(f"  Max history: {info['max_history']}")
    print(f"  Time since activity: {info['time_since_activity']}s")

    # Test 4: Reset session
    print("\nTest 4: Reset session")
    manager.reset_session(test_user)
    history = manager.get_history(test_user)
    print(f"  Messages after reset: {len(history)}")

    # Test 5: Multiple users
    print("\nTest 5: Multiple users")
    user2 = 789012
    manager.add_user_message(test_user, "User 1 message")
    manager.add_user_message(user2, "User 2 message")

    stats = manager.get_stats()
    print(f"  Active sessions: {stats['active_sessions']}")
    print(f"  Total messages: {stats['total_messages']}")

    # Test 6: Cleanup (simulate timeout)
    print("\nTest 6: Cleanup expired sessions")
    print("  (Would remove sessions inactive for >60 seconds)")
    expired = manager.cleanup_expired_sessions()
    print(f"  Expired sessions removed: {expired}")

    print("\n" + "=" * 60)
    print("✅ ALL SESSION MANAGER TESTS COMPLETE")
    print("=" * 60)
