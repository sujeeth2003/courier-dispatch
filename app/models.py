import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class CourierStatus(str, enum.Enum):
    available = "available"
    busy = "busy"
    offline = "offline"


class OrderStatus(str, enum.Enum):
    pending = "pending"
    assigned = "assigned"
    picked_up = "picked_up"
    delivered = "delivered"
    cancelled = "cancelled"


class Courier(Base):
    __tablename__ = "couriers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String, default="Courier")
    status: Mapped[CourierStatus] = mapped_column(
        Enum(CourierStatus, name="courier_status"), default=CourierStatus.available
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
