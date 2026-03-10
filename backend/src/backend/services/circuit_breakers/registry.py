from aiobreaker import CircuitBreaker
from aiobreaker.state import CircuitBreakerState
from aiobreaker.storage.memory import CircuitMemoryStorage

from backend.core.config import CIRCUIT_FAIL_MAX, circuit_reset_timeout
from backend.services.circuit_breakers.storage import create_redis_storage


def _build_storage(name: str):
    redis_storage = create_redis_storage(name)
    if redis_storage is not None:
        return redis_storage
    return CircuitMemoryStorage(state=CircuitBreakerState.CLOSED)


db_breaker = CircuitBreaker(
    fail_max=CIRCUIT_FAIL_MAX,
    timeout_duration=circuit_reset_timeout(),
    state_storage=_build_storage("db"),
    name="db",
)

