from typing import Optional, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.message import Message


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_message(
        self,
        customer_id: Optional[int],
        telegram_user_id: str,
        message_text: str,
        sender_type: str,
        message_type: str = "text",
        detected_intent: Optional[str] = None,
        message_metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        msg = Message(
            customer_id=customer_id,
            telegram_user_id=telegram_user_id,
            message_text=message_text,
            sender_type=sender_type,
            message_type=message_type,
            detected_intent=detected_intent,
            message_metadata=message_metadata or {},
        )

        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg

    async def get_messages_by_user(self, telegram_user_id: str) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.telegram_user_id == telegram_user_id)
            .order_by(Message.sent_at.asc())
        )
        return list(result.scalars().all())
