from collections import defaultdict, deque
from datetime import datetime, timedelta
from threading import Lock

from fastapi import HTTPException, Request, status


_RATE_LIMIT_BUCKETS: dict[str, deque] = defaultdict(deque)
_RATE_LIMIT_LOCK = Lock()


def enforce_rate_limit(request: Request, action: str, max_requests: int, window_seconds: int) -> None:
    client_ip = request.client.host if request.client else "unknown"
    bucket_key = f"{action}:{client_ip}"
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window_seconds)

    with _RATE_LIMIT_LOCK:
        attempts = _RATE_LIMIT_BUCKETS[bucket_key]
        while attempts and attempts[0] < window_start:
            attempts.popleft()

        if len(attempts) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many attempts. Please wait and try again.",
            )

        attempts.append(now)
