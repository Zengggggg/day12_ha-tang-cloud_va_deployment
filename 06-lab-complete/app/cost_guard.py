from dataclasses import dataclass
from datetime import date

from fastapi import HTTPException, status

from app.config import settings


@dataclass
class _DailyCounter:
    day: date
    requests: int = 0


_counter = _DailyCounter(day=date.today(), requests=0)


def enforce_daily_budget() -> None:
    global _counter
    today = date.today()
    if _counter.day != today:
        _counter = _DailyCounter(day=today, requests=0)

    if _counter.requests >= settings.daily_request_budget:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Daily request budget exceeded.",
        )

    _counter.requests += 1
