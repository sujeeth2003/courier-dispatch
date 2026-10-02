"""Fires N simultaneous order-creation requests against fewer couriers than orders,
and asserts no courier is ever assigned to more than one active order at a time.

Requires live Postgres + Redis; skipped otherwise.
"""
import asyncio


N_ORDERS = 20
N_COURIERS = 5


async def test_no_double_assignment_under_concurrency(client):
    courier_ids = []
    for i in range(N_COURIERS):
        resp = await client.post("/couriers", params={"name": f"c{i}"})
        courier = resp.json()
        courier_ids.append(courier["id"])
        await client.post(
            f"/couriers/{courier['id']}/location",
            json={"lat": 37.77 + i * 0.001, "lon": -122.41 + i * 0.001},
        )

    async def create_order():
        return await client.post(
            "/orders",
            json={
                "pickup_lat": 37.77,
                "pickup_lon": -122.41,
                "dropoff_lat": 37.78,
                "dropoff_lon": -122.42,
            },
        )

    responses = await asyncio.gather(*[create_order() for _ in range(N_ORDERS)])
    orders = [r.json() for r in responses]

    assigned_courier_ids = [o["courier_id"] for o in orders if o["courier_id"] is not None]

    # No courier should appear more than once among assigned orders at the same time.
    assert len(assigned_courier_ids) == len(set(assigned_courier_ids))
    assert len(assigned_courier_ids) <= N_COURIERS
