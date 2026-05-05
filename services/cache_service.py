import hashlib
import logging
import re
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.observability.metrics import Metrics
from models.cache_entry import CacheEntry
from models.car import Car

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _normalize_question(
        self,
        raw_question: str,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        model_year: Optional[int] = None,
    ) -> str:
        text = (raw_question or "").strip().lower()
        text = text.replace("؟", " ")

        # إزالة علامات الترقيم والمسافات الزائدة
        text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        # إزالة كلمات عامة لا تغيّر المعنى كثيرًا
        stop_words = {
            "ايه", "اي", "ما", "هو", "هي", "عن", "على", "لو", "طب",
            "عايز", "اريد", "محتاج", "ممكن", "تفاصيل", "معلومات",
            "العربية", "العربيه", "سيارة", "سياره", "بكام", "السعر"
        }
        tokens = [t for t in text.split() if t not in stop_words]
        normalized_text = " ".join(tokens)

        context_parts = [
            brand.strip().lower() if brand else "",
            model.strip().lower() if model else "",
            str(model_year) if model_year else "",
            normalized_text,
        ]
        return "|".join([p for p in context_parts if p])

    def _make_cache_key(
        self,
        intent: str,
        normalized_question: str,
        car_id: Optional[int] = None,
    ) -> str:
        raw = f"{intent}:{car_id or 'none'}:{normalized_question}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    async def get_cached_response(
        self,
        intent: str,
        raw_question: str,
        car_id: Optional[int] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        model_year: Optional[int] = None,
    ) -> Optional[CacheEntry]:
        normalized_question = self._normalize_question(
            raw_question=raw_question,
            brand=brand,
            model=model,
            model_year=model_year,
        )
        cache_key = self._make_cache_key(intent, normalized_question, car_id)

        now = datetime.utcnow()

        result = await self.db.execute(
            select(CacheEntry).where(
                and_(
                    CacheEntry.cache_key == cache_key,
                    CacheEntry.is_active == True,
                    CacheEntry.expires_at.is_not(None),
                    CacheEntry.expires_at > now,
                )
            )
        )
        entry = result.scalar_one_or_none()

        if not entry:
            Metrics.inc_cache_miss()
            logger.info(
                "cache_miss",
                extra={
                    "extra_data": {
                        "intent": intent,
                        "car_id": car_id,
                        "normalized_question": normalized_question,
                    }
                },
            )
            return None

        # لو العربية المرتبطة بالكاش اتباعت أو بقت غير متاحة نعطل الكاش
        if entry.car_id:
            car_result = await self.db.execute(
                select(Car).where(Car.car_id == entry.car_id)
            )
            car = car_result.scalar_one_or_none()

            if not car or bool(car.is_sold) or not bool(car.is_available):
                entry.is_active = False
                await self.db.commit()

                Metrics.inc_cache_miss()
                logger.info(
                    "cache_invalidated_unavailable_car",
                    extra={
                        "extra_data": {
                            "cache_id": entry.cache_id,
                            "car_id": entry.car_id,
                        }
                    },
                )
                return None

        entry.repeat_count = (entry.repeat_count or 0) + 1
        entry.last_hit_at = now
        await self.db.commit()

        Metrics.inc_cache_hit()
        logger.info(
            "cache_hit",
            extra={
                "extra_data": {
                    "cache_id": entry.cache_id,
                    "intent": entry.intent,
                    "car_id": entry.car_id,
                    "repeat_count": entry.repeat_count,
                }
            },
        )
        return entry

    async def increment_or_create(
        self,
        intent: str,
        raw_question: str,
        response_text: str,
        car_id: Optional[int] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        model_year: Optional[int] = None,
    ) -> CacheEntry:
        normalized_question = self._normalize_question(
            raw_question=raw_question,
            brand=brand,
            model=model,
            model_year=model_year,
        )
        cache_key = self._make_cache_key(intent, normalized_question, car_id)

        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=settings.CACHE_TTL_SECONDS)

        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_key == cache_key)
        )
        entry = result.scalar_one_or_none()

        if entry:
            entry.raw_question = raw_question
            entry.normalized_question = normalized_question
            entry.cached_answer = response_text
            entry.expires_at = expires_at
            entry.is_active = True
            entry.repeat_count = (entry.repeat_count or 0) + 1
            entry.last_hit_at = now

            logger.info(
                "cache_updated",
                extra={
                    "extra_data": {
                        "cache_id": entry.cache_id,
                        "intent": intent,
                        "car_id": car_id,
                        "repeat_count": entry.repeat_count,
                    }
                },
            )
        else:
            entry = CacheEntry(
                car_id=car_id,
                intent=intent,
                raw_question=raw_question,
                normalized_question=normalized_question,
                cache_key=cache_key,
                repeat_count=1,
                cached_answer=response_text,
                is_active=True,
                expires_at=expires_at,
                last_hit_at=now,
            )
            self.db.add(entry)

            logger.info(
                "cache_created",
                extra={
                    "extra_data": {
                        "intent": intent,
                        "car_id": car_id,
                        "normalized_question": normalized_question,
                    }
                },
            )

        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def invalidate_by_car(self, car_id: int) -> int:
        result = await self.db.execute(
            update(CacheEntry)
            .where(
                and_(
                    CacheEntry.car_id == car_id,
                    CacheEntry.is_active == True,
                )
            )
            .values(is_active=False)
        )
        await self.db.commit()

        count = result.rowcount or 0
        logger.info(
            "cache_invalidated_by_car",
            extra={
                "extra_data": {
                    "car_id": car_id,
                    "deactivated_entries": count,
                }
            },
        )
        return count

    async def flush_all(self) -> int:
        result = await self.db.execute(
            update(CacheEntry)
            .where(CacheEntry.is_active == True)
            .values(is_active=False)
        )
        await self.db.commit()

        count = result.rowcount or 0
        logger.info(
            "cache_flushed_all",
            extra={"extra_data": {"deactivated_entries": count}},
        )
        return count

    async def list_entries(self, search: Optional[str] = None) -> list[CacheEntry]:
        stmt = select(CacheEntry).order_by(CacheEntry.updated_at.desc())

        if search:
            s = f"%{search.strip()}%"
            stmt = stmt.where(
                (CacheEntry.raw_question.ilike(s))
                | (CacheEntry.normalized_question.ilike(s))
                | (CacheEntry.intent.ilike(s))
                | (CacheEntry.cached_answer.ilike(s))
            )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_entry(self, cache_id: int) -> Optional[CacheEntry]:
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_id == cache_id)
        )
        return result.scalar_one_or_none()

    async def update_entry(self, cache_id: int, updates: dict) -> Optional[CacheEntry]:
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_id == cache_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return None

        allowed_fields = {"cached_answer", "repeat_count", "is_active"}
        for key, value in updates.items():
            if key in allowed_fields and hasattr(entry, key):
                setattr(entry, key, value)

        await self.db.commit()
        await self.db.refresh(entry)

        logger.info(
            "cache_entry_updated",
            extra={
                "extra_data": {
                    "cache_id": cache_id,
                    "updated_fields": list(updates.keys()),
                }
            },
        )
        return entry

    async def disable_entry(self, cache_id: int) -> Optional[CacheEntry]:
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_id == cache_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return None

        entry.is_active = False
        await self.db.commit()
        await self.db.refresh(entry)

        logger.info(
            "cache_entry_disabled",
            extra={"extra_data": {"cache_id": cache_id}},
        )
        return entry

    async def enable_entry(self, cache_id: int) -> Optional[CacheEntry]:
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_id == cache_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return None

        entry.is_active = True
        await self.db.commit()
        await self.db.refresh(entry)

        logger.info(
            "cache_entry_enabled",
            extra={"extra_data": {"cache_id": cache_id}},
        )
        return entry

    async def delete_entry(self, cache_id: int) -> bool:
        result = await self.db.execute(
            select(CacheEntry).where(CacheEntry.cache_id == cache_id)
        )
        entry = result.scalar_one_or_none()
        if not entry:
            return False

        await self.db.delete(entry)
        await self.db.commit()

        logger.info(
            "cache_entry_deleted",
            extra={"extra_data": {"cache_id": cache_id}},
        )
        return True
