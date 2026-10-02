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
