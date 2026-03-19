from __future__ import annotations

from collections import defaultdict, deque
from time import time

from fastapi import HTTPException, status

from src.app.core.config import get_settings


class RateLimiter:
    def __init__(self) -> None:
        self._entries: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> None:
        settings = get_settings()
        now = time()
        window = settings.rate_limit_window_seconds
        limit = settings.rate_limit_requests
        bucket = self._entries[key]
        while bucket and now - bucket[0] > window:
            bucket.popleft()
        if len(bucket) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="rate limit exceeded",
                headers={"Retry-After": str(window)},
            )
        bucket.append(now)

    def clear(self) -> None:
        self._entries.clear()


rate_limiter = RateLimiter()
