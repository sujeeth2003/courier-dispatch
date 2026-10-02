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


async def set_courier_location(courier_id: str, lat: float, lon: float) -> None:
    redis = get_redis()
    await redis.geoadd(COURIER_GEO_KEY, (lon, lat, courier_id))
    await redis.set(f"{COURIER_LAST_SEEN_PREFIX}{courier_id}", "now", ex=settings.courier_stale_seconds)


async def nearby_couriers(lat: float, lon: float, radius_km: float = 50.0, count: int = 20):
    redis = get_redis()
    results = await redis.geosearch(
        COURIER_GEO_KEY,
        longitude=lon,
        latitude=lat,
        radius=radius_km,
        unit="km",
        count=count,
        sort="ASC",
    )
    return results


async def remove_courier_location(courier_id: str) -> None:
    redis = get_redis()
    await redis.zrem(COURIER_GEO_KEY, courier_id)


async def courier_positions(courier_ids: list[str]) -> dict[str, tuple[float, float]]:
    """Return {courier_id: (lat, lon)} for every id present in the geo index."""
    if not courier_ids:
        return {}
    found = await get_redis().geopos(COURIER_GEO_KEY, *courier_ids)
    return {cid: (pos[1], pos[0]) for cid, pos in zip(courier_ids, found) if pos is not None}
