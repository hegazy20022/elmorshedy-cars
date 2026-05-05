from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from models.business_info import BusinessInfo

router = APIRouter(prefix="/control", tags=["control"])


@router.post("/bot/enable")
async def enable_bot(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessInfo).where(BusinessInfo.info_key == "bot_enabled"))
    info = result.scalar_one_or_none()
    
    if info:
        info.info_value = {"value": True}
    else:
        info = BusinessInfo(info_key="bot_enabled", info_value={"value": True})
        db.add(info)
        
    await db.commit()
    return {"bot_enabled": True}


@router.post("/bot/disable")
async def disable_bot(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BusinessInfo).where(BusinessInfo.info_key == "bot_enabled"))
    info = result.scalar_one_or_none()
    
    if info:
        info.info_value = {"value": False}
    else:
        info = BusinessInfo(info_key="bot_enabled", info_value={"value": False})
        db.add(info)
        
    await db.commit()
    return {"bot_enabled": False}
