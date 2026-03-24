# src/mcp_server/middleware/rate_limiter.py
import asyncio
from collections import defaultdict
import time

class SlidingWindowRateLimiter:
    def __init__(self, max_calls: int, window_seconds: int = 60):
        self.max_calls = max_calls
        self.window = window_seconds
        self._calls: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check(self, key: str) -> None:
        async with self._lock:
            now = time.monotonic()
            window_start = now - self.window
            self._calls[key] = [t for t in self._calls[key] if t > window_start]
            if len(self._calls[key]) >= self.max_calls:
                raise McpError(ErrorCode.INVALID_REQUEST, "Rate limit exceeded")
            self._calls[key].append(now)