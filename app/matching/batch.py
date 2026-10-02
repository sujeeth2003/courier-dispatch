"""v2 matcher: batch a window of orders and couriers, solve as an assignment problem.

Uses the Hungarian algorithm (scipy.optimize.linear_sum_assignment) to minimize total
pickup distance across the whole batch. Falls back to a greedy nearest-first assignment
if scipy is unavailable.
"""
from app.matching.geo import haversine_km
from app.matching.nearest import CourierLoc, OrderLoc, match_orders_nearest

try:
    import numpy as np
    from scipy.optimize import linear_sum_assignment

    _HAS_SCIPY = True
except ImportError:  # pragma: no cover
    _HAS_SCIPY = False


def match_orders_batch(
    orders: list[OrderLoc], couriers: list[CourierLoc]
) -> list[tuple[str, str, float]]:
    """Return a list of (order_id, courier_id, distance_km) minimizing total pickup distance."""
    if not orders or not couriers:
        return []

    if not _HAS_SCIPY:
        return match_orders_nearest(orders, couriers)

    n_orders, n_couriers = len(orders), len(couriers)
    cost = np.zeros((n_orders, n_couriers))
    for i, order in enumerate(orders):
        for j, courier in enumerate(couriers):
            cost[i, j] = haversine_km(order.pickup_lat, order.pickup_lon, courier.lat, courier.lon)

    row_idx, col_idx = linear_sum_assignment(cost)
    results = []
    for r, c in zip(row_idx, col_idx):
        results.append((orders[r].id, couriers[c].id, float(cost[r, c])))
    return results
