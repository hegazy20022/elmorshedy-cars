from __future__ import annotations

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from models.business_info import BusinessInfo


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class DashboardAuthService:
    SETTING_KEY = "dashboard_auth"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_row(self) -> Optional[BusinessInfo]:
        result = await self.db.execute(
            select(BusinessInfo).where(BusinessInfo.info_key == self.SETTING_KEY)
        )
        return result.scalar_one_or_none()

    async def ensure_initialized(self, default_password: str = "admin123") -> BusinessInfo:
        row = await self._get_row()
        if row:
            if not isinstance(row.info_value, dict):
                row.info_value = {
                    "enabled": True,
                    "password_hash": pwd_context.hash(default_password),
                }
                await self.db.commit()
                await self.db.refresh(row)
            return row

        row = BusinessInfo(
            info_key=self.SETTING_KEY,
            info_value={
                "enabled": True,
                "password_hash": pwd_context.hash(default_password),
            },
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return row

    async def is_enabled(self) -> bool:
        row = await self.ensure_initialized()
        info = row.info_value if isinstance(row.info_value, dict) else {}
        return bool(info.get("enabled", True))

    async def verify_password(self, password: str) -> bool:
        row = await self.ensure_initialized()
        info = row.info_value if isinstance(row.info_value, dict) else {}
        password_hash = info.get("password_hash")
        if not password_hash:
            return False
        return pwd_context.verify(password, password_hash)

    async def change_password(self, current_password: str, new_password: str) -> tuple[bool, str]:
        row = await self.ensure_initialized()
        info = row.info_value if isinstance(row.info_value, dict) else {}
        password_hash = info.get("password_hash")

        if not password_hash or not pwd_context.verify(current_password, password_hash):
            return False, "الباسورد الحالي غير صحيح"

        info["password_hash"] = pwd_context.hash(new_password)
        row.info_value = info
        await self.db.commit()
        return True, "تم تغيير الباسورد بنجاح"

    async def set_enabled(self, enabled: bool) -> bool:
        row = await self.ensure_initialized()
        info = row.info_value if isinstance(row.info_value, dict) else {}
        info["enabled"] = enabled
        row.info_value = info
        await self.db.commit()
        return enabled
