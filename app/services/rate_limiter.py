"""
Rate limiter service to mimic the Go implementation.
"""

import time
from threading import Lock


class RateLimiter:
    """A simple thread-safe rate limiter."""

    def __init__(self, max_count: int) -> None:
        """Initialize the rate limiter with a maximum count."""
        self.count: int = 0
        self.date: float = time.time()
        self.mutex: Lock = Lock()
        self.max_count: int = max_count

    def increment(self) -> None:
        """Increment the rate limit counter."""
        self.reset_if_expired()
        with self.mutex:
            self.count += 1

    def reset(self) -> None:
        """Reset the rate limit counter and timestamp."""
        with self.mutex:
            self.count = 0
            self.date = time.time()

    def get_count(self) -> int:
        """Get the current rate limit counter."""
        self.reset_if_expired()
        with self.mutex:
            return self.count

    def is_exceeded(self) -> bool:
        """Check if the rate limit has been exceeded."""
        return self.count >= self.max_count

    def reset_if_expired(self) -> None:
        """Reset the rate limit counter if the expiration time has passed."""
        if time.time() - self.date > 3600:  # 1 hour
            self.reset()


rate_limiter_instance = RateLimiter(1000)
