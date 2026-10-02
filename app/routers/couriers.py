from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.metrics import location_updates_total
from app.models import Courier, CourierStatus
from app.redis_client import set_courier_location
from app.schemas import CourierLocationUpdate, CourierOut

router = APIRouter(prefix="/couriers", tags=["couriers"])


@router.post("", response_model=CourierOut, status_code=201)
async def create_courier(name: str = "Courier", session: AsyncSession = Depends(get_session)):
    courier = Courier(name=name, status=CourierStatus.available)
    session.add(courier)
    await session.commit()
    await session.refresh(courier)
    return courier


@router.post("/{courier_id}/location", status_code=204)
async def update_location(
    courier_id: str, payload: CourierLocationUpdate, session: AsyncSession = Depends(get_session)
):
    courier = await session.get(Courier, courier_id)
    if courier is None:
        raise HTTPException(status_code=404, detail="courier not found")
    await set_courier_location(courier_id, payload.lat, payload.lon)
    location_updates_total.inc()


@router.get("/{courier_id}", response_model=CourierOut)
async def get_courier(courier_id: str, session: AsyncSession = Depends(get_session)):
    courier = await session.get(Courier, courier_id)
    if courier is None:
        raise HTTPException(status_code=404, detail="courier not found")
    return courier
