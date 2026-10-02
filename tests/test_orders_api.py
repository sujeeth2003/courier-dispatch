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
