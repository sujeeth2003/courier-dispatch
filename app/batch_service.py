"""v2 runtime: assign all pending orders together, once per batch window."""
import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assignment_service import refresh_pending_gauge
from app.config import settings
from app.db import SessionLocal
from app.matching.batch import match_orders_batch
from app.matching.nearest import CourierLoc, OrderLoc
from app.metrics import assignment_latency_seconds, assignments_total
from app.models import Assignment, Courier, CourierStatus, Order, OrderStatus
from app.redis_client import courier_positions

logger = logging.getLogger(__name__)


async def assign_pending_batch(session: AsyncSession) -> int:
    """Match every pending order against every free courier in one Hungarian solve.

    Pending orders and available couriers are locked with FOR UPDATE SKIP LOCKED, so
    nothing another transaction holds can be assigned twice. Locks are released when
    the caller commits. Returns the number of orders assigned.
    """
    orders = (
        await session.execute(
            select(Order)
            .where(Order.status == OrderStatus.pending)
            .order_by(Order.created_at)
            .with_for_update(skip_locked=True)
        )
    ).scalars().all()
    if not orders:
        return 0

    couriers = (
        await session.execute(
            select(Courier)
            .where(Courier.status == CourierStatus.available)
            .with_for_update(skip_locked=True)
        )
    ).scalars().all()
    positions = await courier_positions([c.id for c in couriers])

    matches = match_orders_batch(
        [OrderLoc(o.id, o.pickup_lat, o.pickup_lon) for o in orders],
        [CourierLoc(cid, lat, lon) for cid, (lat, lon) in positions.items()],
    )

    orders_by_id = {o.id: o for o in orders}
    couriers_by_id = {c.id: c for c in couriers}
    now = datetime.now(timezone.utc)
    for order_id, courier_id, distance_km in matches:
        order = orders_by_id[order_id]
        courier = couriers_by_id[courier_id]
        courier.status = CourierStatus.busy
        order.status = OrderStatus.assigned
        order.courier_id = courier.id
        session.add(
            Assignment(
                order_id=order.id,
                courier_id=courier.id,
                pickup_distance_km=distance_km,
                strategy="batch",
            )
        )
        assignments_total.labels(strategy="batch").inc()
        assignment_latency_seconds.observe((now - order.created_at).total_seconds())
    return len(matches)


async def run_batch_loop() -> None:
    """Run assign_pending_batch every batch_window_seconds until cancelled."""
    while True:
        await asyncio.sleep(settings.batch_window_seconds)
        try:
            async with SessionLocal() as session:
                await assign_pending_batch(session)
                await session.commit()
                await refresh_pending_gauge(session)
        except Exception:
            logger.exception("batch assignment failed")
