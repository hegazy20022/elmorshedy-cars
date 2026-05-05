from __future__ import annotations
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class CarBase(BaseModel):
    car_name: str = Field(..., min_length=1)
    brand: Optional[str] = None
    model: Optional[str] = None
    model_year: Optional[int] = Field(default=None, ge=1950, le=2100)
    color: Optional[str] = None
    description: Optional[str] = None
    license_status: Optional[str] = None

    cash_price: Optional[float] = Field(default=None, ge=0)
    installment_price: Optional[float] = Field(default=None, ge=0)

    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    class_level: Optional[str] = None
    engine_cc: Optional[int] = Field(default=None, ge=0)

    usage_tags: List[str] = Field(default_factory=list)

    city_friendly: bool = False
    family_friendly: bool = False
    fuel_economy_level: Optional[str] = None

    mileage: Optional[int] = Field(default=None, ge=0)
    paint_status: Optional[str] = None

    is_sold: bool = False
    is_available: bool = True


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    car_name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    model_year: Optional[int] = Field(default=None, ge=1950, le=2100)
    color: Optional[str] = None
    description: Optional[str] = None
    license_status: Optional[str] = None

    cash_price: Optional[float] = Field(default=None, ge=0)
    installment_price: Optional[float] = Field(default=None, ge=0)

    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    class_level: Optional[str] = None
    engine_cc: Optional[int] = Field(default=None, ge=0)

    usage_tags: Optional[List[str]] = None

    city_friendly: Optional[bool] = None
    family_friendly: Optional[bool] = None
    fuel_economy_level: Optional[str] = None

    mileage: Optional[int] = Field(default=None, ge=0)
    paint_status: Optional[str] = None

    is_sold: Optional[bool] = None
    is_available: Optional[bool] = None


class CarResponse(CarBase):
    car_id: int
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
