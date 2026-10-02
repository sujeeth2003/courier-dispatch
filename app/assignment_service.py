"""Handles assigning an order to a courier with concurrency-safe row locking."""
import time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.matching.geo import haversine_km
from app.metrics import assignment_latency_seconds, assignments_total, pending_orders_gauge
from app.models import Assignment, Courier, CourierStatus, Order, OrderStatus
from app.redis_client import get_redis, nearby_couriers


async def assign_order_nearest(session: AsyncSession, order: Order) -> Assignment | None:
    """Find the nearest available courier via Redis geo index, then lock and assign in Postgres.

    Uses SELECT ... FOR UPDATE SKIP LOCKED so concurrent requests never double-assign
    the same courier: if a courier row is already locked by another transaction it is
    skipped, and the next candidate is tried. The row lock is held until the caller commits.
    """
    start = time.monotonic()
    candidates = await nearby_couriers(order.pickup_lat, order.pickup_lon)
    if not candidates:
        return None

    redis = get_redis()

    for courier_id in candidates:
        result = await session.execute(
            select(Courier)
            .where(Courier.id == courier_id, Courier.status == CourierStatus.available)
            .with_for_update(skip_locked=True)
        )
        courier = result.scalar_one_or_none()
        if courier is None:
            continue  # locked by another transaction, or no longer available

        pos = await redis.geopos("couriers:geo", courier_id)
        if not pos or pos[0] is None:
            continue
        courier_lon, courier_lat = pos[0]
        dist = haversine_km(order.pickup_lat, order.pickup_lon, courier_lat, courier_lon)
        courier.status = CourierStatus.busy
        order.status = OrderStatus.assigned
        order.courier_id = courier.id

        assignment = Assignment(
            order_id=order.id,
            courier_id=courier.id,
            pickup_distance_km=dist,
            strategy="nearest",
        )
        session.add(assignment)
        assignments_total.labels(strategy="nearest").inc()
        assignment_latency_seconds.observe(time.monotonic() - start)
        return assignment

    return None


async def refresh_pending_gauge(session: AsyncSession) -> None:
    count = await session.scalar(
        select(func.count()).select_from(Order).where(Order.status == OrderStatus.pending)
    )
    pending_orders_gauge.set(count or 0)
