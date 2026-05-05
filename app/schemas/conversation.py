from __future__ import annotations
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict


class ConversationModeUpdate(BaseModel):
    mode: str


class ConversationResponse(BaseModel):
    telegram_user_id: str
    customer_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    last_message: Optional[str] = None
    mode: Optional[str] = "AI"
    context: Optional[dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
