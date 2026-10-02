from pydantic import BaseModel, Field

from app.models import CourierStatus, OrderStatus


class OrderCreate(BaseModel):
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float


class OrderOut(BaseModel):
    id: str
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
    status: OrderStatus
    courier_id: str | None

    model_config = {"from_attributes": True}


class CourierLocationUpdate(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class CourierOut(BaseModel):
    id: str
    name: str
    status: CourierStatus

    model_config = {"from_attributes": True}
