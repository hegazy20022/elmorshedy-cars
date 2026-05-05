from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from models.customer import Customer
from models.message import Message
from models.conversation_state import ConversationState
from services.memory_service import MemoryService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Customer).order_by(Customer.created_at.desc()))
    customers = result.scalars().all()

    rows = []
    for customer in customers:
        msg_result = await db.execute(
            select(Message)
            .where(Message.telegram_user_id == customer.telegram_user_id)
            .order_by(Message.sent_at.desc())
            .limit(1)
        )
        state_result = await db.execute(
            select(ConversationState).where(ConversationState.telegram_user_id == customer.telegram_user_id)
        )

        last_msg = msg_result.scalar_one_or_none()
        conv_state = state_result.scalar_one_or_none()

        rows.append({
            "معرف المستخدم": customer.telegram_user_id,
            "اسم العميل": customer.full_name,
            "اسم المستخدم": customer.username,
            "الهاتف": customer.phone,
            "آخر رسالة": last_msg.message_text if last_msg else "",
            "وضع المحادثة": conv_state.mode if conv_state else "AI",
        })

    return rows


@router.post("/{telegram_user_id}/takeover")
async def takeover_conversation(telegram_user_id: str, db: AsyncSession = Depends(get_db)):
    memory = MemoryService(db)
    await memory.set_owner_mode(telegram_user_id)
    return {"ok": True, "mode": "OWNER"}


@router.post("/{telegram_user_id}/resume")
async def resume_conversation(telegram_user_id: str, db: AsyncSession = Depends(get_db)):
    memory = MemoryService(db)
    await memory.set_ai_mode(telegram_user_id)
    return {"ok": True, "mode": "AI"}


@router.post("/{telegram_user_id}/pause")
async def pause_conversation(telegram_user_id: str, db: AsyncSession = Depends(get_db)):
    memory = MemoryService(db)
    await memory.set_paused_mode(telegram_user_id)
    return {"ok": True, "mode": "PAUSED"}
