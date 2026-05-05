from sqlalchemy import Column, Integer, Text, Numeric, Boolean, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .base import Base


class Car(Base):
    __tablename__ = "cars"

    car_id = Column(Integer, primary_key=True, index=True)
    car_name = Column(Text, nullable=False)
    brand = Column(Text)
    model = Column(Text)
    model_year = Column(Integer)
    color = Column(Text)
    description = Column(Text)
    license_status = Column(Text)
    cash_price = Column(Numeric(12, 2))
    installment_price = Column(Numeric(12, 2))

    transmission = Column(Text)
    fuel_type = Column(Text)
    body_type = Column(Text)
    engine_cc = Column(Integer)
    usage_tags = Column(JSON().with_variant(JSONB, 'postgresql'), default=list)
    class_level = Column(Text)  # فئة أولى - فئة ثانية - فئة ثالثة
    city_friendly = Column(Boolean, default=False)
    family_friendly = Column(Boolean, default=False)
    fuel_economy_level = Column(Text)
    mileage = Column(Integer)
    paint_status = Column(Text)

    is_sold = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
