from sqlalchemy import Column, Integer, Text, Date, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .base import Base


class AnalyticsReport(Base):
    __tablename__ = "analytics_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    report_month = Column(Date, nullable=False)
    report_text = Column(Text, nullable=False)
    metrics_json = Column(JSON().with_variant(JSONB, 'postgresql'), default=dict)
    generated_at = Column(TIMESTAMP, server_default=func.now())
