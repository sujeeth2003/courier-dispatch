from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assignment_service import assign_order_nearest
from app.db import get_session
from app.metrics import orders_created_total, pending_orders_gauge
from app.models import Order, OrderStatus
from app.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
async def create_order(payload: OrderCreate, session: AsyncSession = Depends(get_session)):
    order = Order(
        pickup_lat=payload.pickup_lat,
        pickup_lon=payload.pickup_lon,
        dropoff_lat=payload.dropoff_lat,
        dropoff_lon=payload.dropoff_lon,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    orders_created_total.inc()

    await assign_order_nearest(session, order)
    await session.commit()
    await session.refresh(order)

    result = await session.execute(select(Order).where(Order.status == OrderStatus.pending))
    pending_orders_gauge.set(len(result.scalars().all()))

    return order
