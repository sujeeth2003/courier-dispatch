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


def run_comparison(n_orders: int = 50, n_couriers: int = 60, seed: int = 42) -> dict:
    orders, couriers = generate_synthetic(n_orders, n_couriers, seed)

    nearest_results = match_orders_nearest(orders, couriers)
    batch_results = match_orders_batch(orders, couriers)

    nearest_distances = [d for _, _, d in nearest_results]
    batch_distances = [d for _, _, d in batch_results]

    summary = {
        "n_orders": n_orders,
        "n_couriers": n_couriers,
        "nearest": {
            "assigned": len(nearest_results),
            "avg_pickup_distance_km": statistics.mean(nearest_distances) if nearest_distances else None,
            "total_pickup_distance_km": sum(nearest_distances),
        },
        "batch": {
            "assigned": len(batch_results),
            "avg_pickup_distance_km": statistics.mean(batch_distances) if batch_distances else None,
            "total_pickup_distance_km": sum(batch_distances),
        },
    }
    return summary


if __name__ == "__main__":
    result = run_comparison()
    print(json.dumps(result, indent=2))
    with open("compare_results.json", "w") as f:
        json.dump(result, f, indent=2)
