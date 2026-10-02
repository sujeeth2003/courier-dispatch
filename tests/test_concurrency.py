"""Fires N simultaneous order-creation requests against fewer couriers than orders,
and asserts no courier is ever assigned to more than one active order at a time.

Requires live Postgres + Redis; skipped otherwise.
"""
import asyncio

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db import create_all, engine
from app.main import app

N_ORDERS = 20
N_COURIERS = 5


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
