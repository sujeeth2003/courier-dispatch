"""Integration tests requiring a live Postgres + Redis (see docker-compose / CI services).

Skipped automatically if the DB is unreachable, so `pytest` still works without docker.
"""
import uuid


async def test_create_courier_and_order(client):
    courier_resp = await client.post("/couriers", params={"name": "Alice"})
    assert courier_resp.status_code == 201
    courier = courier_resp.json()

    loc_resp = await client.post(
        f"/couriers/{courier['id']}/location", json={"lat": 37.7749, "lon": -122.4194}
    )
    assert loc_resp.status_code == 204

    order_resp = await client.post(
        "/orders",
        json={
            "pickup_lat": 37.775,
            "pickup_lon": -122.419,
            "dropoff_lat": 37.78,
            "dropoff_lon": -122.42,
        },
    )
    assert order_resp.status_code == 201
    order = order_resp.json()
    assert order["status"] in ("assigned", "pending")


async def test_get_unknown_order_404(client):
    resp = await client.get(f"/orders/{uuid.uuid4()}")
    assert resp.status_code == 404


async def test_nearest_strategy_assigns_immediately(client):
    courier = (await client.post("/couriers", params={"name": "Bob"})).json()
    await client.post(
        f"/couriers/{courier['id']}/location", json={"lat": 37.77, "lon": -122.41}
    )
    order = (
        await client.post(
            "/orders",
            json={
                "pickup_lat": 37.77,
                "pickup_lon": -122.41,
                "dropoff_lat": 37.78,
                "dropoff_lon": -122.42,
            },
        )
    ).json()
    assert order["status"] == "assigned"
    assert order["courier_id"] == courier["id"]
