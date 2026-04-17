import os
from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "VinFast Route Planner API")
    app_env: str = os.getenv("APP_ENV", "production")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))
    app_api_key: str = os.getenv("APP_API_KEY", "")
    cors_origins: List[str] = field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*").split(",")
    )
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    daily_request_budget: int = int(os.getenv("DAILY_REQUEST_BUDGET", "2000"))


settings = Settings()
