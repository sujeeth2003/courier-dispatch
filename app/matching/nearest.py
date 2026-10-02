"""v1 matcher: assign each order to the single nearest available courier, immediately."""
from dataclasses import dataclass

from app.matching.geo import haversine_km


@dataclass
class CourierLoc:
    id: str
    lat: float
    lon: float


@dataclass
class OrderLoc:
    id: str
    pickup_lat: float
    pickup_lon: float


def find_nearest_courier(order: OrderLoc, couriers: list[CourierLoc]) -> tuple[CourierLoc, float] | None:
    """Return (courier, distance_km) for the closest courier, or None if none available."""
    if not couriers:
        return None
    best = min(
        couriers,
        key=lambda c: haversine_km(order.pickup_lat, order.pickup_lon, c.lat, c.lon),
    )
    dist = haversine_km(order.pickup_lat, order.pickup_lon, best.lat, best.lon)
    return best, dist
