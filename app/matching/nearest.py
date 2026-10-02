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


def match_orders_nearest(
    orders: list[OrderLoc], couriers: list[CourierLoc]
) -> list[tuple[str, str, float]]:
    """Process orders one at a time in order, greedily taking the nearest still-free courier.

    Returns a list of (order_id, courier_id, distance_km).
    """
    available = list(couriers)
    results = []
    for order in orders:
        found = find_nearest_courier(order, available)
        if found is None:
            continue
        courier, dist = found
        results.append((order.id, courier.id, dist))
        available = [c for c in available if c.id != courier.id]
    return results
