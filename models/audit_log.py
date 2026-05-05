from sqlalchemy import Column, Integer, Text, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from .base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    actor_type = Column(Text, nullable=False)
    actor_id = Column(Text)
    action_name = Column(Text, nullable=False)
    entity_type = Column(Text)
    entity_id = Column(Text)
    details = Column(JSON().with_variant(JSONB, 'postgresql'), default=dict)
    created_at = Column(TIMESTAMP, server_default=func.now())
