from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    from services.analytics_service import AnalyticsService
    service = AnalyticsService(db)
    return await service.get_basic_stats()

@router.get("/top-asked")
async def get_top_asked(db: AsyncSession = Depends(get_db)):
    from services.analytics_service import AnalyticsService
    service = AnalyticsService(db)
    return await service.get_top_asked_cars()

@router.get("/top-booked")
async def get_top_booked(db: AsyncSession = Depends(get_db)):
    from services.analytics_service import AnalyticsService
    service = AnalyticsService(db)
    return await service.get_top_booked_cars()

@router.get("/budget-trends")
async def get_budget_trends(db: AsyncSession = Depends(get_db)):
    from services.analytics_service import AnalyticsService
    service = AnalyticsService(db)
    return await service.get_budget_trends()

@router.get("/latest-report")
async def get_latest_report(db: AsyncSession = Depends(get_db)):
    from services.analytics_service import AnalyticsService
    service = AnalyticsService(db)
    report = await service.get_latest_report()
    if not report:
        return None
    return {
        "report_month": report.report_month,
        "report_text": report.report_text,
        "generated_at": report.generated_at
    }

@router.post("/generate-report")
async def generate_report(db: AsyncSession = Depends(get_db)):
    from services.analytics_service import AnalyticsService
    from services.ai_service import AIService
    service = AnalyticsService(db)
    ai_service = AIService()
    try:
        report = await service.generate_monthly_report(ai_service)
        return {"status": "success", "report_id": report.report_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
