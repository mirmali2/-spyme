"""Lightweight in-memory rate limiter. Swap for Redis in multi-worker deploys."""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request


class RateLimiter:
    def __init__(self, max_calls: int, window_sec: int):
        self.max_calls = max_calls
        self.window = window_sec
        self.hits: dict[str, deque] = defaultdict(deque)

    def __call__(self, request: Request):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        bucket = self.hits[ip]
        # Drop expired
        while bucket and bucket[0] < now - self.window:
            bucket.popleft()
        if len(bucket) >= self.max_calls:
            raise HTTPException(
                status_code=429,
                detail=f"Too many attempts. Try again in {self.window} seconds.",
            )
        bucket.append(now)


login_limiter = RateLimiter(max_calls=5, window_sec=900)         # 5 / 15 min
register_limiter = RateLimiter(max_calls=3, window_sec=3600)     # 3 / hour
google_limiter = RateLimiter(max_calls=10, window_sec=900)       # 10 / 15 min
