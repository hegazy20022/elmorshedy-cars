from sqlalchemy import Column, Integer, Text, Date, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    summary_id = Column(Integer, primary_key=True, index=True)
    week_start = Column(Date)
    summary = Column(Text)
    top_questions = Column(Text)
    customer_notes = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
