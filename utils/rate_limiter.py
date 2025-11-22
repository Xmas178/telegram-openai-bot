"""
Rate limiting utility for Telegram bot
Prevents spam and API abuse by limiting requests per user
Author: Sami (CodeNob Dev)
"""

import time
from collections import defaultdict, deque
from typing import Dict, Deque, Tuple


class RateLimiter:
    """
    Simple in-memory rate limiter to prevent spam

    Tracks requests per user and enforces a maximum rate.
    Uses a sliding window approach with timestamps.

    Security features:
    - Per-user rate limiting
    - Configurable time window
    - Automatic cleanup of old entries
    - Thread-safe for single-process bots
    """

    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed per time window
            time_window: Time window in seconds (default: 60 = 1 minute)
        """
        self.max_requests = max_requests
        self.time_window = time_window

        # Store timestamps of requests per user
        # Key: user_id, Value: deque of timestamps
        self.user_requests: Dict[int, Deque[float]] = defaultdict(deque)

        # Track when we last cleaned up old entries
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # Cleanup every 5 minutes

    def is_allowed(self, user_id: int) -> Tuple[bool, int]:
        """
        Check if user is allowed to make a request

        Args:
            user_id: Telegram user ID

        Returns:
            Tuple of (is_allowed, requests_remaining)
            - is_allowed: True if user can make request
            - requests_remaining: Number of requests left in current window
        """
        current_time = time.time()

        # Perform periodic cleanup
        self._cleanup_if_needed(current_time)

        # Get user's request history
        user_queue = self.user_requests[user_id]

        # Remove requests outside the time window
        cutoff_time = current_time - self.time_window
        while user_queue and user_queue[0] < cutoff_time:
            user_queue.popleft()

        # Check if user has exceeded rate limit
        current_count = len(user_queue)

        if current_count < self.max_requests:
            # User is allowed, record this request
            user_queue.append(current_time)
            requests_remaining = self.max_requests - current_count - 1
            return True, requests_remaining
        else:
            # User has exceeded rate limit
            requests_remaining = 0
            return False, requests_remaining

    def get_wait_time(self, user_id: int) -> int:
        """
        Get how long user must wait before next request is allowed

        Args:
            user_id: Telegram user ID

        Returns:
            Seconds until next request is allowed (0 if allowed now)
        """
        user_queue = self.user_requests[user_id]

        if not user_queue or len(user_queue) < self.max_requests:
            return 0

        # Calculate when the oldest request will expire
        oldest_request = user_queue[0]
        current_time = time.time()
        wait_time = int(self.time_window - (current_time - oldest_request))

        return max(0, wait_time)

    def reset_user(self, user_id: int):
        """
        Reset rate limit for a specific user

        Args:
            user_id: Telegram user ID to reset
        """
        if user_id in self.user_requests:
            del self.user_requests[user_id]

    def _cleanup_if_needed(self, current_time: float):
        """
        Clean up old user entries to prevent memory bloat

        Args:
            current_time: Current timestamp
        """
        # Only cleanup every cleanup_interval seconds
        if current_time - self.last_cleanup < self.cleanup_interval:
            return

        # Remove users with no recent requests
        cutoff_time = current_time - self.time_window
        users_to_remove = []

        for user_id, queue in self.user_requests.items():
            # Remove old timestamps from queue
            while queue and queue[0] < cutoff_time:
                queue.popleft()

            # If queue is empty, mark user for removal
            if not queue:
                users_to_remove.append(user_id)

        # Remove inactive users
        for user_id in users_to_remove:
            del self.user_requests[user_id]

        self.last_cleanup = current_time

    def get_stats(self) -> Dict:
        """
        Get current rate limiter statistics

        Returns:
            Dictionary with statistics about current state
        """
        return {
            "active_users": len(self.user_requests),
            "max_requests": self.max_requests,
            "time_window_seconds": self.time_window,
            "last_cleanup": self.last_cleanup,
        }


# Test the rate limiter when running this file directly
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING RATE LIMITER")
    print("=" * 60)

    # Create rate limiter: max 5 requests per 10 seconds (for testing)
    limiter = RateLimiter(max_requests=5, time_window=10)

    test_user_id = 123456

    print(f"\n📋 Test Configuration:")
    print(f"  Max requests: 5")
    print(f"  Time window: 10 seconds")
    print(f"  Test user ID: {test_user_id}\n")

    # Test 1: Make 5 requests (should all be allowed)
    print("Test 1: Making 5 requests (should all be allowed)")
    for i in range(5):
        allowed, remaining = limiter.is_allowed(test_user_id)
        status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
        print(f"  Request {i+1}: {status} - {remaining} requests remaining")

    # Test 2: Make 6th request (should be blocked)
    print("\nTest 2: Making 6th request (should be blocked)")
    allowed, remaining = limiter.is_allowed(test_user_id)
    status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
    wait_time = limiter.get_wait_time(test_user_id)
    print(f"  Request 6: {status}")
    print(f"  Wait time: {wait_time} seconds")

    # Test 3: Different user (should be allowed)
    print("\nTest 3: Different user making request (should be allowed)")
    different_user = 789012
    allowed, remaining = limiter.is_allowed(different_user)
    status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
    print(f"  Request: {status} - {remaining} requests remaining")

    # Test 4: Reset first user
    print("\nTest 4: Reset first user and retry")
    limiter.reset_user(test_user_id)
    allowed, remaining = limiter.is_allowed(test_user_id)
    status = "✅ ALLOWED" if allowed else "❌ BLOCKED"
    print(f"  Request after reset: {status} - {remaining} requests remaining")

    # Test 5: Statistics
    print("\nTest 5: Rate limiter statistics")
    stats = limiter.get_stats()
    print(f"  Active users: {stats['active_users']}")
    print(f"  Max requests: {stats['max_requests']}")
    print(f"  Time window: {stats['time_window_seconds']}s")

    # Test 6: Time-based expiry (simulate waiting)
    print("\nTest 6: Time-based expiry simulation")
    print("  (In production, requests would expire after 10 seconds)")
    print("  Waiting 2 seconds...")
    time.sleep(2)
    wait_time = limiter.get_wait_time(test_user_id)
    print(f"  Wait time after 2s: {wait_time} seconds")

    print("\n" + "=" * 60)
    print("✅ ALL RATE LIMITER TESTS COMPLETE")
    print("=" * 60)
