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
