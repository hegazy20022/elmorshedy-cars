from sqlalchemy import Column, Integer, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .base import Base


class CacheEntry(Base):
    __tablename__ = "cache_entries"

    cache_id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.car_id", ondelete="CASCADE"))

    intent = Column(Text, nullable=False)
    raw_question = Column(Text)
    normalized_question = Column(Text)
    cache_key = Column(Text, unique=True, nullable=False)

    repeat_count = Column(Integer, default=1)
    cached_answer = Column(Text)

    is_active = Column(Boolean, default=True)
    expires_at = Column(TIMESTAMP)
    last_hit_at = Column(TIMESTAMP, server_default=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
