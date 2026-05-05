from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.business_info import BusinessInfo


class BotControlService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def is_bot_enabled(self) -> bool:
        result = await self.db.execute(
            select(BusinessInfo).where(BusinessInfo.info_key == "bot_enabled")
        )
        row = result.scalar_one_or_none()
        if not row:
            return True
        return bool(row.info_value.get("value", True))

    async def set_bot_enabled(self, enabled: bool) -> bool:
        result = await self.db.execute(
            select(BusinessInfo).where(BusinessInfo.info_key == "bot_enabled")
        )
        row = result.scalar_one_or_none()
        if not row:
            return False

        row.info_value = {"value": enabled}
        await self.db.commit()
        return enabled
