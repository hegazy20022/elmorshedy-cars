from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time


class BookingBase(BaseModel):
    car_id: int = Field(..., ge=1)
    customer_id: Optional[int] = Field(default=None, ge=1)

    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None

    booking_date: date
    booking_time: time
    notes: Optional[str] = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    booking_status: Optional[str] = None
    notes: Optional[str] = None


class BookingResponse(BookingBase):
    booking_id: int
    day_name: Optional[str] = None
    booking_status: str = "confirmed"
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
