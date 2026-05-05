from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Text, unique=True, nullable=False, index=True)

    full_name = Column(Text)
    phone = Column(Text)
    address = Column(Text)
    username = Column(Text)

    preferred_car_id = Column(Integer, ForeignKey("cars.car_id", ondelete="SET NULL"))

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
