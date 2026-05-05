from __future__ import annotations
from typing import Optional, Any, Dict
from datetime import date, time, datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.conversation_state import ConversationState


class MemoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_state(self, telegram_user_id: str) -> Optional[ConversationState]:
        result = await self.db.execute(
            select(ConversationState).where(ConversationState.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_state(self, telegram_user_id: str) -> ConversationState:
        state = await self.get_state(telegram_user_id)
        if state:
            return state

        state = ConversationState(
            telegram_user_id=telegram_user_id,
            mode="AI",
            context={},
        )
        self.db.add(state)
        await self.db.commit()
        await self.db.refresh(state)
        return state

    async def update_state(
        self,
        telegram_user_id: str,
        mode: Optional[str] = None,
        current_intent: Optional[str] = -1,  # type: ignore # Sentinel for no change
        current_step: Optional[str] = -1,    # type: ignore # Sentinel for no change
        selected_car_id: Optional[int] = None,
        context_updates: Optional[Dict[str, Any]] = None,
    ) -> ConversationState:
        state = await self.get_or_create_state(telegram_user_id)

        if mode is not None:
            state.mode = mode
        if current_intent != -1:
            state.current_intent = current_intent
        if current_step != -1:
            state.current_step = current_step
        if selected_car_id is not None:
            state.selected_car_id = selected_car_id

        ctx = dict(state.context or {})
        if context_updates:
            for key, value in context_updates.items():
                ctx[key] = value
        state.context = ctx

        await self.db.commit()
        await self.db.refresh(state)
        return state

    async def mark_greeted(self, telegram_user_id: str):
        await self.update_state(
            telegram_user_id,
            context_updates={"greeted": True},
        )

    async def get_context_value(self, telegram_user_id: str, key: str, default: Any = None) -> Any:
        state = await self.get_state(telegram_user_id)
        if not state or not state.context:
            return default
        return state.context.get(key, default)

    async def set_last_car(self, telegram_user_id: str, car_id: int):
        await self.update_state(
            telegram_user_id,
            selected_car_id=car_id,
            context_updates={"last_car_id": car_id},
        )

    async def get_last_car_id(self, telegram_user_id: str) -> Optional[int]:
        state = await self.get_state(telegram_user_id)
        if not state:
            return None

        if state.selected_car_id:
            return state.selected_car_id

        ctx = state.context or {}
        return ctx.get("last_car_id")

    async def set_last_budget(self, telegram_user_id: str, budget: float):
        await self.update_state(
            telegram_user_id,
            context_updates={"last_budget": budget},
        )

    async def get_last_budget(self, telegram_user_id: str) -> Optional[float]:
        return await self.get_context_value(telegram_user_id, "last_budget")

    async def set_pending_car_clarification(
        self,
        telegram_user_id: str,
        brand: Optional[str],
        model: Optional[str],
        model_year: Optional[int],
    ):
        await self.update_state(
            telegram_user_id,
            current_step="awaiting_car_clarification",
            context_updates={
                "awaiting_car_clarification": True,
                "last_brand": brand,
                "last_model": model,
                "last_model_year": model_year,
            },
        )

    async def clear_pending_car_clarification(self, telegram_user_id: str):
        await self.update_state(
            telegram_user_id,
            current_step=None,
            context_updates={
                "awaiting_car_clarification": False,
            },
        )

    async def set_customer_info(
        self,
        telegram_user_id: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ):
        updates = {}
        if full_name:
            updates["customer_name"] = full_name
        if phone:
            updates["customer_phone"] = phone
        if address:
            updates["customer_address"] = address

        if updates:
            await self.update_state(
                telegram_user_id,
                context_updates=updates,
            )

    async def get_customer_info(self, telegram_user_id: str) -> dict:
        state = await self.get_state(telegram_user_id)
        ctx = state.context or {} if state else {}
        return {
            "full_name": ctx.get("customer_name"),
            "phone": ctx.get("customer_phone"),
            "address": ctx.get("customer_address"),
        }

    async def set_pending_booking(self, telegram_user_id: str, booking_data: dict):
        safe_data = dict(booking_data)

        if isinstance(safe_data.get("booking_date"), date):
            safe_data["booking_date"] = safe_data["booking_date"].isoformat()

        if isinstance(safe_data.get("booking_time"), time):
            safe_data["booking_time"] = safe_data["booking_time"].strftime("%H:%M:%S")

        await self.update_state(
            telegram_user_id,
            current_step="awaiting_booking_customer_info",
            context_updates={
                "pending_booking_data": safe_data,
            },
        )

    async def get_pending_booking(self, telegram_user_id: str) -> Optional[dict]:
        data = await self.get_context_value(telegram_user_id, "pending_booking_data")

        if not data:
            return data

        parsed_data = dict(data)

        if parsed_data.get("booking_date"):
            parsed_data["booking_date"] = datetime.fromisoformat(parsed_data["booking_date"]).date()

        if parsed_data.get("booking_time"):
            parsed_data["booking_time"] = datetime.strptime(parsed_data["booking_time"], "%H:%M:%S").time()

        return parsed_data

    async def clear_pending_booking(self, telegram_user_id: str):
        await self.update_state(
            telegram_user_id,
            current_step=None,
            context_updates={
                "pending_booking_data": None,
            },
        )

    async def set_last_booking_info(
        self,
        telegram_user_id: str,
        booking_id: Optional[int] = None,
        booking_date: Optional[str] = None,
        booking_time: Optional[str] = None,
        car_name: Optional[str] = None,
    ):
        updates = {}
        if booking_id is not None:
            updates["last_booking_id"] = booking_id
        if booking_date is not None:
            updates["last_booking_date"] = booking_date
        if booking_time is not None:
            updates["last_booking_time"] = booking_time
        if car_name is not None:
            updates["last_booking_car_name"] = car_name

        if updates:
            await self.update_state(
                telegram_user_id,
                context_updates=updates,
            )

    async def get_last_booking_info(self, telegram_user_id: str) -> dict:
        state = await self.get_state(telegram_user_id)
        ctx = state.context or {} if state else {}
        return {
            "booking_id": ctx.get("last_booking_id"),
            "booking_date": ctx.get("last_booking_date"),
            "booking_time": ctx.get("last_booking_time"),
            "car_name": ctx.get("last_booking_car_name"),
        }

    async def set_owner_mode(self, telegram_user_id: str):
        return await self.update_state(telegram_user_id, mode="OWNER")

    async def set_ai_mode(self, telegram_user_id: str):
        return await self.update_state(telegram_user_id, mode="AI")

    async def set_paused_mode(self, telegram_user_id: str):
        return await self.update_state(telegram_user_id, mode="PAUSED")
