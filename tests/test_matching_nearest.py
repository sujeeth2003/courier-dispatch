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


def test_match_orders_nearest_no_double_assignment():
    orders = [OrderLoc(id=f"o{i}", pickup_lat=0.0, pickup_lon=0.0) for i in range(3)]
    couriers = [CourierLoc(id="c1", lat=0.001, lon=0.001), CourierLoc(id="c2", lat=0.002, lon=0.002)]

    results = match_orders_nearest(orders, couriers)

    assert len(results) == 2  # only 2 couriers available for 3 orders
    assigned_couriers = [courier_id for _, courier_id, _ in results]
    assert len(assigned_couriers) == len(set(assigned_couriers))


def test_match_orders_nearest_empty_inputs():
    assert match_orders_nearest([], []) == []
    assert match_orders_nearest([OrderLoc(id="o1", pickup_lat=0, pickup_lon=0)], []) == []
