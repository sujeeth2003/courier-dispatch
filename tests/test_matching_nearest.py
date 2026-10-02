from app.matching.geo import haversine_km
from app.matching.nearest import CourierLoc, OrderLoc, find_nearest_courier, match_orders_nearest


def test_haversine_zero_distance():
    assert haversine_km(37.7749, -122.4194, 37.7749, -122.4194) == 0.0


def test_haversine_known_distance():
    # San Francisco to Los Angeles is roughly 559 km
    dist = haversine_km(37.7749, -122.4194, 34.0522, -118.2437)
    assert 550 < dist < 570
