from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.cache import CacheUpdate
from services.cache_service import CacheService

router = APIRouter(prefix="/cache", tags=["cache"])


@router.get("/")
async def list_cache_entries(
    search: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = CacheService(db)
    rows = await service.list_entries(search=search)

    return [
        {
            "cache_id": row.cache_id,
            "car_id": row.car_id,
            "intent": row.intent,
            "raw_question": row.raw_question,
            "normalized_question": row.normalized_question,
            "cache_key": row.cache_key,
            "repeat_count": row.repeat_count,
            "cached_answer": row.cached_answer,
            "is_active": row.is_active,
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
            "last_hit_at": row.last_hit_at.isoformat() if row.last_hit_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
        for row in rows
    ]


@router.get("/{cache_id}")
async def get_cache_entry(
    cache_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = CacheService(db)
    row = await service.get_entry(cache_id)
    if not row:
        raise HTTPException(status_code=404, detail="Cache entry not found")

    return {
        "cache_id": row.cache_id,
        "car_id": row.car_id,
        "intent": row.intent,
        "raw_question": row.raw_question,
        "normalized_question": row.normalized_question,
        "cache_key": row.cache_key,
        "repeat_count": row.repeat_count,
        "cached_answer": row.cached_answer,
        "is_active": row.is_active,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        "last_hit_at": row.last_hit_at.isoformat() if row.last_hit_at else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@router.put("/{cache_id}")
async def update_cache_entry(
    cache_id: int,
    payload: CacheUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = CacheService(db)
    row = await service.update_entry(cache_id, payload.model_dump(exclude_unset=True))
    if not row:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    return {"ok": True}


@router.post("/{cache_id}/disable")
async def disable_cache_entry(
    cache_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = CacheService(db)
    row = await service.disable_entry(cache_id)
    if not row:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    return {"ok": True, "is_active": False}


@router.post("/{cache_id}/enable")
async def enable_cache_entry(
    cache_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = CacheService(db)
    row = await service.enable_entry(cache_id)
    if not row:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    return {"ok": True, "is_active": True}


@router.delete("/{cache_id}")
async def delete_cache_entry(
    cache_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = CacheService(db)
    deleted = await service.delete_entry(cache_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cache entry not found")
    return {"ok": True}
