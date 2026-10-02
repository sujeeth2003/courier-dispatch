from app.matching.batch import match_orders_batch
from app.matching.nearest import CourierLoc, OrderLoc, match_orders_nearest


def _synthetic(n_orders=8, n_couriers=8):
    orders = [OrderLoc(id=f"o{i}", pickup_lat=i * 0.01, pickup_lon=i * 0.01) for i in range(n_orders)]
    couriers = [
        CourierLoc(id=f"c{i}", lat=(n_orders - i) * 0.01, lon=(n_orders - i) * 0.01)
        for i in range(n_couriers)
    ]
    return orders, couriers


def test_match_orders_batch_assigns_all_when_enough_couriers():
    orders, couriers = _synthetic(5, 5)
    results = match_orders_batch(orders, couriers)
    assert len(results) == 5
    assigned_couriers = [c for _, c, _ in results]
    assert len(assigned_couriers) == len(set(assigned_couriers))


def test_match_orders_batch_no_double_assignment_more_orders_than_couriers():
    orders, couriers = _synthetic(10, 4)
    results = match_orders_batch(orders, couriers)
    assert len(results) == 4
    assigned_couriers = [c for _, c, _ in results]
    assert len(assigned_couriers) == len(set(assigned_couriers))
    assigned_orders = [o for o, _, _ in results]
    assert len(assigned_orders) == len(set(assigned_orders))


def test_match_orders_batch_empty_inputs():
    assert match_orders_batch([], []) == []
