from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from services.ai_service import AIService
from services.analytics_service import AnalyticsService
from services.booking_service import BookingService
from services.bot_control_service import BotControlService
from services.cache_service import CacheService
from services.car_service import CarService
from services.chat_service import ChatService
from services.customer_service import CustomerService
from services.entity_service import EntityService
from services.intent_service import IntentService
from services.memory_service import MemoryService
from services.voice_service import VoiceService


def get_ai_service() -> AIService:
    return AIService()


def get_entity_service() -> EntityService:
    return EntityService()


def get_intent_service() -> IntentService:
    return IntentService()


def get_car_service(db: AsyncSession = Depends(get_db)) -> CarService:
    return CarService(db)


def get_customer_service(db: AsyncSession = Depends(get_db)) -> CustomerService:
    return CustomerService(db)


def get_booking_service(db: AsyncSession = Depends(get_db)) -> BookingService:
    return BookingService(db)


def get_memory_service(db: AsyncSession = Depends(get_db)) -> MemoryService:
    return MemoryService(db)


def get_cache_service(db: AsyncSession = Depends(get_db)) -> CacheService:
    return CacheService(db)


def get_chat_service(db: AsyncSession = Depends(get_db)) -> ChatService:
    return ChatService(db)


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(db)


def get_bot_control_service(db: AsyncSession = Depends(get_db)) -> BotControlService:
    return BotControlService(db)


def get_voice_service() -> VoiceService:
    return VoiceService()
