from redis.asyncio import Redis, from_url

from app.config import settings

COURIER_GEO_KEY = "couriers:geo"
COURIER_LAST_SEEN_PREFIX = "courier:last_seen:"

_redis: Redis | None = None


def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = from_url(settings.redis_url, decode_responses=True)
    return _redis
