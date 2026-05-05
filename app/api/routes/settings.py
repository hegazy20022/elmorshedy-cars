from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from models.business_info import BusinessInfo

router = APIRouter(prefix="/settings", tags=["settings"])


async def _get_or_create_setting(db: AsyncSession, key: str, default_value: dict):
    result = await db.execute(
        select(BusinessInfo).where(BusinessInfo.info_key == key)
    )
    row = result.scalar_one_or_none()

    if row:
        return row

    row = BusinessInfo(
        info_key=key,
        info_value=default_value,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


@router.get("/booking")
async def get_booking_settings(db: AsyncSession = Depends(get_db)):
    row = await _get_or_create_setting(
        db,
        "booking_settings",
        {
            "working_days": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
            "start_time": "10:00",
            "end_time": "18:00",
            "slot_duration_minutes": 60,
            "emergency_closed_dates": [],
        },
    )
    return row.info_value


@router.put("/booking")
async def update_booking_settings(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    row = await _get_or_create_setting(
        db,
        "booking_settings",
        {
            "working_days": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
            "start_time": "10:00",
            "end_time": "18:00",
            "slot_duration_minutes": 60,
            "emergency_closed_dates": [],
        },
    )

    row.info_value = {
        "working_days": payload.get("working_days", []),
        "start_time": payload.get("start_time", "10:00"),
        "end_time": payload.get("end_time", "18:00"),
        "slot_duration_minutes": int(payload.get("slot_duration_minutes", 60)),
        "emergency_closed_dates": payload.get("emergency_closed_dates", []),
    }

    await db.commit()
    await db.refresh(row)
    return {"ok": True, "data": row.info_value}


@router.get("/contact")
async def get_business_contact(db: AsyncSession = Depends(get_db)):
    row = await _get_or_create_setting(
        db,
        "business_contact",
        {
            "phone": "",
            "address": "",
            "location_url": "",
        },
    )
    return row.info_value


@router.put("/contact")
async def update_business_contact(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    row = await _get_or_create_setting(
        db,
        "business_contact",
        {
            "phone": "",
            "address": "",
            "location_url": "",
        },
    )

    row.info_value = {
        "phone": payload.get("phone", ""),
        "address": payload.get("address", ""),
        "location_url": payload.get("location_url", ""),
    }

    await db.commit()
    await db.refresh(row)
    return {"ok": True, "data": row.info_value}


@router.get("/cache")
async def get_cache_settings(db: AsyncSession = Depends(get_db)):
    row = await _get_or_create_setting(
        db,
        "cache_settings",
        {
            "repeat_threshold": 3,
            "ttl_hours": 24,
        },
    )
    return row.info_value


@router.put("/cache")
async def update_cache_settings(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    row = await _get_or_create_setting(
        db,
        "cache_settings",
        {
            "repeat_threshold": 3,
            "ttl_hours": 24,
        },
    )

    row.info_value = {
        "repeat_threshold": int(payload.get("repeat_threshold", 3)),
        "ttl_hours": int(payload.get("ttl_hours", 24)),
    }

    await db.commit()
    await db.refresh(row)
    return {"ok": True, "data": row.info_value}
