from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from models.base import Base


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(Text, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=True)
    sender_type = Column(Text, nullable=False)
    message_type = Column(Text, nullable=False, default="text")
    message_text = Column(Text, nullable=True)
    detected_intent = Column(Text, nullable=True)

    message_metadata = Column("metadata", JSON().with_variant(JSONB, 'postgresql'), nullable=True, default=dict)

    sent_at = Column(DateTime(timezone=True), server_default=func.now())
