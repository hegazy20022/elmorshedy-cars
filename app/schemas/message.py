from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class MessageResponse(BaseModel):
    message_id: int
    telegram_user_id: str
    customer_id: Optional[int] = None
    sender_type: str
    message_type: str = "text"
    message_text: Optional[str] = None
    detected_intent: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    sent_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
