from sqlalchemy import Column, Integer, Text, Numeric, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base


class PurchaseRequest(Base):
    __tablename__ = "purchase_requests"

    request_id = Column(Integer, primary_key=True, index=True)

    seller_name = Column(Text)
    seller_phone = Column(Text)
    seller_address = Column(Text)

    car_name = Column(Text)
    brand = Column(Text)
    model = Column(Text)
    model_year = Column(Integer)
    color = Column(Text)
    license_status = Column(Text)
    description = Column(Text)
    asking_price = Column(Numeric(12, 2))

    status = Column(Text, default="pending")

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
