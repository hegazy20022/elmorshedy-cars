from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from services.dashboard_auth_service import DashboardAuthService

router = APIRouter(prefix="/dashboard-auth", tags=["dashboard-auth"])


@router.get("/status")
async def dashboard_auth_status(db: AsyncSession = Depends(get_db)):
    service = DashboardAuthService(db)
    enabled = await service.is_enabled()
    return {"enabled": enabled}


@router.post("/login")
async def dashboard_login(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    password = payload.get("password", "")
    service = DashboardAuthService(db)

    ok = await service.verify_password(password)
    if not ok:
        raise HTTPException(status_code=401, detail="الباسورد غير صحيح")

    return {"ok": True}


@router.post("/change-password")
async def dashboard_change_password(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    current_password = payload.get("current_password", "")
    new_password = payload.get("new_password", "")

    if not new_password or len(new_password) < 4:
        raise HTTPException(status_code=400, detail="الباسورد الجديد لازم يكون 4 حروف على الأقل")

    service = DashboardAuthService(db)
    ok, message = await service.change_password(current_password, new_password)

    if not ok:
        raise HTTPException(status_code=400, detail=message)

    return {"ok": True, "message": message}


@router.post("/enable")
async def dashboard_auth_enable(db: AsyncSession = Depends(get_db)):
    service = DashboardAuthService(db)
    enabled = await service.set_enabled(True)
    return {"ok": True, "enabled": enabled}


@router.post("/disable")
async def dashboard_auth_disable(db: AsyncSession = Depends(get_db)):
    service = DashboardAuthService(db)
    enabled = await service.set_enabled(False)
    return {"ok": True, "enabled": enabled}
