from sqlalchemy import Column, Integer, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .base import Base


class BusinessInfo(Base):
    __tablename__ = "business_info"

    info_id = Column(Integer, primary_key=True, index=True)
    info_key = Column(Text, unique=True, nullable=False)
    info_value = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
