import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from app.config import settings

_ip_request_buckets: dict[str, deque[float]] = defaultdict(deque)


def enforce_rate_limit(request: Request) -> None:
    now = time.time()
    ip = request.client.host if request.client else "unknown"
    bucket = _ip_request_buckets[ip]
    window_start = now - 60

    while bucket and bucket[0] < window_start:
        bucket.popleft()

    if len(bucket) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please retry later.",
        )

    bucket.append(now)
