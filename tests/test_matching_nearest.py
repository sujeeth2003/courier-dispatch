from app.matching.geo import haversine_km
from app.matching.nearest import CourierLoc, OrderLoc, find_nearest_courier, match_orders_nearest


def test_haversine_zero_distance():
    assert haversine_km(37.7749, -122.4194, 37.7749, -122.4194) == 0.0


def test_haversine_known_distance():
    # San Francisco to Los Angeles is roughly 559 km
    dist = haversine_km(37.7749, -122.4194, 34.0522, -118.2437)
    assert 550 < dist < 570


def test_find_nearest_courier_picks_closest():
    order = OrderLoc(id="o1", pickup_lat=0.0, pickup_lon=0.0)
    couriers = [
        CourierLoc(id="far", lat=10.0, lon=10.0),
        CourierLoc(id="near", lat=0.01, lon=0.01),
        CourierLoc(id="mid", lat=1.0, lon=1.0),
    ]
    courier, dist = find_nearest_courier(order, couriers)
    assert courier.id == "near"
    assert dist >= 0


def test_find_nearest_courier_no_couriers():
    order = OrderLoc(id="o1", pickup_lat=0.0, pickup_lon=0.0)
    assert find_nearest_courier(order, []) is None
