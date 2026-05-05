from fastapi import APIRouter
from sqlalchemy import text

from app.core.database import AsyncSessionLocal

router = APIRouter(tags=["observability"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "elmorshedy-cars-api",
    }


@router.get("/health/db")
async def health_db():
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected",
        }
    except Exception as exc:
        return {
            "status": "down",
            "database": "disconnected",
            "error": str(exc),
        }
