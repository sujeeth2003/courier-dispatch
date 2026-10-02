from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.metrics import location_updates_total
from app.models import Courier, CourierStatus
from app.redis_client import set_courier_location
from app.schemas import CourierLocationUpdate, CourierOut

router = APIRouter(prefix="/couriers", tags=["couriers"])
