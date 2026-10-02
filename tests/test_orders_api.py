"""Integration tests requiring a live Postgres + Redis (see docker-compose / CI services).

Skipped automatically if the DB is unreachable, so `pytest` still works without docker.
"""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db import create_all, engine
from app.main import app


async def _db_available() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.fixture
async def client():
    if not await _db_available():
        pytest.skip("Postgres not available")
    await create_all()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


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
