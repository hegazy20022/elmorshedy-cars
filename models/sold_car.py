from sqlalchemy import Column, Integer, Text, Numeric, TIMESTAMP, Date, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class SoldCar(Base):
    __tablename__ = "sold_cars"

    sale_id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.car_id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="SET NULL"))

    buyer_name = Column(Text)
    buyer_phone = Column(Text)
    buyer_address = Column(Text)

    cash_price = Column(Numeric(12, 2))
    down_payment = Column(Numeric(12, 2))
    remaining_amount = Column(Numeric(12, 2))

    installment_months = Column(Integer)
    installment_end_date = Column(Date)
    installment_value = Column(Numeric(12, 2))

    sold_at = Column(TIMESTAMP, server_default=func.now())
