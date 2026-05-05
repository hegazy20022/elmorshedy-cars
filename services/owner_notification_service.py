from __future__ import annotations
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class OwnerNotificationService:
    def __init__(self, bot=None):
        self.bot = bot

    async def notify_service_failure(
        self,
        source: str,
        error_message: str,
        telegram_user_id: Optional[str] = None,
    ) -> None:
        if not self.bot:
            logger.warning("OwnerNotificationService bot is not initialized")
            return

        text = (
            "🚨 تنبيه عطل في الخدمة\n"
            f"المصدر: {source}\n"
            f"العميل: {telegram_user_id or 'غير معروف'}\n"
            f"الخطأ: {error_message}"
        )

        try:
            await self.bot.send_message(
                chat_id=settings.TELEGRAM_OWNER_CHAT_ID,
                text=text,
            )
        except Exception:
            logger.exception("Failed to notify owner about service failure")
