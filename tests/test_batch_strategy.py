"""Integration tests for MATCHER_STRATEGY=batch. Require live Postgres + Redis."""
import asyncio
from contextlib import suppress

import pytest
from sqlalchemy import select

from app.batch_service import assign_pending_batch, run_batch_loop
from app.config import settings
from app.db import SessionLocal
from app.models import Assignment

ORDER = {"pickup_lat": 37.77, "pickup_lon": -122.41, "dropoff_lat": 37.78, "dropoff_lon": -122.42}


@pytest.fixture
def batch_mode(monkeypatch):
    monkeypatch.setattr(settings, "matcher_strategy", "batch")


async def _add_couriers(client, n):
    ids = []
    for i in range(n):
        courier = (await client.post("/couriers", params={"name": f"c{i}"})).json()
        await client.post(
            f"/couriers/{courier['id']}/location",
            json={"lat": 37.77 + i * 0.001, "lon": -122.41},
        )
        ids.append(courier["id"])
    return ids


async def _run_batch_once() -> int:
    async with SessionLocal() as session:
        assigned = await assign_pending_batch(session)
        await session.commit()
    return assigned


async def test_order_stays_pending_until_batch_runs(client, batch_mode):
    await _add_couriers(client, 1)
    order = (await client.post("/orders", json=ORDER)).json()
    assert order["status"] == "pending"
    assert order["courier_id"] is None


async def test_batch_assigns_pending_orders_to_distinct_couriers(client, batch_mode):
    courier_ids = await _add_couriers(client, 3)
    order_ids = [(await client.post("/orders", json=ORDER)).json()["id"] for _ in range(3)]

    assert await _run_batch_once() == 3

    orders = [(await client.get(f"/orders/{oid}")).json() for oid in order_ids]
    assigned = [o["courier_id"] for o in orders]
    assert all(o["status"] == "assigned" for o in orders)
    assert sorted(assigned) == sorted(courier_ids)


async def test_batch_leaves_extra_orders_pending(client, batch_mode):
    await _add_couriers(client, 2)
    for _ in range(5):
        await client.post("/orders", json=ORDER)

    assert await _run_batch_once() == 2

    async with SessionLocal() as session:
        strategies = (await session.execute(select(Assignment.strategy))).scalars().all()
    assert strategies == ["batch", "batch"]
