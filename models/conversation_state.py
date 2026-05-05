from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, JSON, Date
from sqlalchemy.sql import func
from .base import Base


class ConversationState(Base):
    __tablename__ = "conversation_state"

    telegram_user_id = Column(Text, primary_key=True)
    mode = Column(Text, default="AI")
    current_intent = Column(Text)
    current_step = Column(Text)
    selected_car_id = Column(Integer, ForeignKey("cars.car_id", ondelete="SET NULL"))
    context = Column(JSON, default=dict)

    daily_message_count = Column(Integer, default=0)
    last_message_date = Column(Date)

    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
