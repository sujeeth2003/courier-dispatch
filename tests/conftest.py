import os

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://courier:courier@localhost:5432/courier_dispatch_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

import app.redis_client as redis_client  # noqa: E402
from app.db import create_all, engine  # noqa: E402
from app.main import app  # noqa: E402


async def _db_available() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@pytest.fixture
async def client():
    # Each test runs in its own event loop, so connections from a previous test must not be reused.
    await engine.dispose()
    redis_client._redis = None

    if not await _db_available():
        pytest.skip("Postgres not available")
    await create_all()
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE assignments, orders, couriers CASCADE"))
    await redis_client.get_redis().delete(redis_client.COURIER_GEO_KEY)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    await redis_client.get_redis().aclose()
    redis_client._redis = None
    await engine.dispose()
