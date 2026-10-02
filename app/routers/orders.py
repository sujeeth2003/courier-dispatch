from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.assignment_service import assign_order_nearest, refresh_pending_gauge
from app.config import settings
from app.db import get_session
from app.metrics import orders_created_total
from app.models import Order
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

    if settings.matcher_strategy == "nearest":
        await assign_order_nearest(session, order)
        await session.commit()
        await session.refresh(order)

    await refresh_pending_gauge(session)

    return order


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: str, session: AsyncSession = Depends(get_session)):
    order = await session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order
