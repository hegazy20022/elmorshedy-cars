from sqlalchemy import Column, Integer, Text, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func

from .base import Base


class CarImage(Base):
    __tablename__ = "car_images"

    image_id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.car_id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    display_order = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
