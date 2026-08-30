"""Lightweight in-memory rate limiting for sensitive endpoints.

This is a simple fixed-window counter keyed by client IP, suitable for a
single-process deployment (consistent with the SQLite/embedded-ChromaDB
scope of this project). It intentionally avoids adding a Redis dependency.
For a multi-instance deployment, swap this for a shared store (e.g. Redis)
behind the same `check_rate_limit` interface.
"""

import time
import threading
from collections import defaultdict

from fastapi import HTTPException, Request

_lock = threading.Lock()
# {bucket_key: [window_start_epoch, count]}
_buckets: dict[str, list] = defaultdict(lambda: [0.0, 0])


def _client_key(request: Request, scope: str) -> str:
    client_ip = request.client.host if request.client else "unknown"
    return f"{scope}:{client_ip}"


def check_rate_limit(request: Request, scope: str, limit_per_minute: int) -> None:
    """Raise HTTP 429 if the client has exceeded `limit_per_minute` for `scope`.

    A `limit_per_minute` of 0 or less disables rate limiting entirely.
    """
    if limit_per_minute <= 0:
        return

    key = _client_key(request, scope)
    now = time.time()
    window = 60.0

    with _lock:
        window_start, count = _buckets[key]
        if now - window_start >= window:
            # New window
            _buckets[key] = [now, 1]
            return
        if count >= limit_per_minute:
            retry_after = int(window - (now - window_start)) + 1
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit exceeded ({limit_per_minute} requests/minute). "
                    f"Please try again in {retry_after}s."
                ),
                headers={"Retry-After": str(retry_after)},
            )
        _buckets[key][1] = count + 1


def reset_rate_limits() -> None:
    """Clear all rate-limit state (used in tests)."""
    with _lock:
        _buckets.clear()
