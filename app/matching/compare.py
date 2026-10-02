"""Compare v1 (nearest) vs v2 (batch/Hungarian) matchers on synthetic data.

Run: python -m app.matching.compare
Prints average pickup distance per strategy and writes results to compare_results.json.
"""
import json
import random
import statistics

from app.matching.batch import match_orders_batch
from app.matching.nearest import CourierLoc, OrderLoc, match_orders_nearest
