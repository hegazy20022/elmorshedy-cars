from sqlalchemy import Column, Integer, Text, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class CarFinancingOption(Base):
    __tablename__ = "car_financing_options"

    financing_id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.car_id", ondelete="CASCADE"), nullable=False)

    down_payment = Column(Numeric(12, 2))
    installment_months = Column(Integer)
    installment_value = Column(Numeric(12, 2))
    total_price = Column(Numeric(12, 2))
    notes = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
