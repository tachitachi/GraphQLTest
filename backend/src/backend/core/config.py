import os
from datetime import timedelta


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/booksdb",
)

REDIS_URL = os.getenv("REDIS_URL")

CACHE_TTL_SECONDS_RAW = os.getenv("CACHE_TTL_SECONDS", "30")
try:
    CACHE_TTL_SECONDS = max(int(CACHE_TTL_SECONDS_RAW), 0)
except ValueError:
    CACHE_TTL_SECONDS = 30


CIRCUIT_FAIL_MAX_RAW = os.getenv("CIRCUIT_FAIL_MAX", "5")
try:
    CIRCUIT_FAIL_MAX = max(int(CIRCUIT_FAIL_MAX_RAW), 1)
except ValueError:
    CIRCUIT_FAIL_MAX = 5


CIRCUIT_RESET_TIMEOUT_SECONDS_RAW = os.getenv("CIRCUIT_RESET_TIMEOUT_SECONDS", "60")
try:
    CIRCUIT_RESET_TIMEOUT_SECONDS = max(int(CIRCUIT_RESET_TIMEOUT_SECONDS_RAW), 1)
except ValueError:
    CIRCUIT_RESET_TIMEOUT_SECONDS = 60


def circuit_reset_timeout() -> timedelta:
    return timedelta(seconds=CIRCUIT_RESET_TIMEOUT_SECONDS)

