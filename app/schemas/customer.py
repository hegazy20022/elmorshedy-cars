from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomerResponse(BaseModel):
    customer_id: int
    telegram_user_id: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    username: Optional[str] = None
    preferred_car_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
