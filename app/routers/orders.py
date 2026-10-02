from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.assignment_service import assign_order_nearest
from app.db import get_session
from app.metrics import orders_created_total, pending_orders_gauge
from app.models import Order, OrderStatus
from app.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])
