"""Compare v1 (nearest) vs v2 (batch/Hungarian) matchers on synthetic data.

Run: python -m app.matching.compare
Prints average pickup distance per strategy and writes results to compare_results.json.
"""
import json
import random
import statistics

from app.matching.batch import match_orders_batch
from app.matching.nearest import CourierLoc, OrderLoc, match_orders_nearest


def generate_synthetic(n_orders: int, n_couriers: int, seed: int = 42):
    rng = random.Random(seed)
    lat_range = (37.70, 37.80)  # roughly a city-sized bounding box
    lon_range = (-122.50, -122.40)

    orders = [
        OrderLoc(
            id=f"order-{i}",
            pickup_lat=rng.uniform(*lat_range),
            pickup_lon=rng.uniform(*lon_range),
        )
        for i in range(n_orders)
    ]
    couriers = [
        CourierLoc(
            id=f"courier-{i}",
            lat=rng.uniform(*lat_range),
            lon=rng.uniform(*lon_range),
        )
        for i in range(n_couriers)
    ]
    return orders, couriers
