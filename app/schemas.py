from pydantic import BaseModel, Field

from app.models import CourierStatus, OrderStatus


class OrderCreate(BaseModel):
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float
