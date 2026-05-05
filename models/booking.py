from sqlalchemy import Column, Integer, Text, Date, Time, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)

    car_id = Column(Integer, ForeignKey("cars.car_id", ondelete="RESTRICT"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id", ondelete="SET NULL"))

    customer_name = Column(Text)
    customer_phone = Column(Text)
    customer_address = Column(Text)

    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    day_name = Column(Text)

    booking_status = Column(Text, default="confirmed")
    notes = Column(Text)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
