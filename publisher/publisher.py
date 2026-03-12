import json
import os
import random
import time
import uuid
import logging

import redis

logger = logging.getLogger(__name__)

logging.basicConfig(level="INFO")

def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    pool_size = max(_env_int("EVENT_ID_POOL_SIZE", 8), 1)
    interval_ms = max(_env_int("PUBLISH_INTERVAL_MS", 500), 10)

    r = redis.Redis.from_url(redis_url, decode_responses=True)

    seq = 0
    while True:
        seq += 1
        event_id = str(random.randint(1, pool_size))
        channel = f"event:{event_id}"
        payload = {
            "id": str(uuid.uuid4()),
            "seq": seq,
            "eventId": event_id,
            "publishedAtMs": int(time.time() * 1000),
            "value": random.random(),
        }
        resp = r.publish(channel, json.dumps(payload))
        # logger.info(resp)
        time.sleep(interval_ms / 1000.0)


if __name__ == "__main__":
    main()

