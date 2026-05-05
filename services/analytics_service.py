from __future__ import annotations
import json
from datetime import date
from sqlalchemy import func, select, desc, and_, text
from sqlalchemy.ext.asyncio import AsyncSession

from models.booking import Booking
from models.message import Message
from models.customer import Customer
from models.car import Car
from models.analytics_report import AnalyticsReport


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_basic_stats(self) -> dict:
        try:
            bookings_count = await self.db.scalar(select(func.count()).select_from(Booking))
            messages_count = await self.db.scalar(select(func.count()).select_from(Message))
            customers_count = await self.db.scalar(select(func.count()).select_from(Customer))
            available_cars_count = await self.db.scalar(
                select(func.count()).select_from(Car).where(Car.is_available.is_(True), Car.is_sold.is_(False))
            )
            return {
                "bookings_count": bookings_count or 0,
                "messages_count": messages_count or 0,
                "customers_count": customers_count or 0,
                "available_cars_count": available_cars_count or 0,
            }
        except Exception:
            return {"bookings_count": 0, "messages_count": 0, "customers_count": 0, "available_cars_count": 0}

    async def get_top_asked_cars(self, limit: int = 5) -> list[dict]:
        try:
            # طريقة أكثر أماناً للتعامل مع الـ JSONB في PostgreSQL
            stmt = (
                select(
                    Car.car_name,
                    func.count(Message.message_id).label("count")
                )
                .join(Car, text("cars.car_id = CAST(messages.metadata->>'car_id' AS INTEGER)"))
                .where(Message.detected_intent == "ask_specific_car")
                .group_by(Car.car_name)
                .order_by(desc("count"))
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            return [{"car_name": r[0], "count": r[1]} for r in result.all()]
        except Exception:
            return []

    async def get_top_booked_cars(self, limit: int = 5) -> list[dict]:
        try:
            stmt = (
                select(
                    Car.car_name,
                    func.count(Booking.booking_id).label("count")
                )
                .join(Car, Booking.car_id == Car.car_id)
                .group_by(Car.car_name)
                .order_by(desc("count"))
                .limit(limit)
            )
            result = await self.db.execute(stmt)
            return [{"car_name": r[0], "count": r[1]} for r in result.all()]
        except Exception:
            return []

    async def get_budget_trends(self) -> list[dict]:
        try:
            stmt = select(text("messages.metadata->>'extracted_budget'")) \
                   .where(text("messages.metadata->>'extracted_budget' IS NOT NULL"))
            
            result = await self.db.execute(stmt)
            budgets = []
            for r in result.all():
                try:
                    if r[0]: budgets.append(float(r[0]))
                except: continue
            
            categories = {"أقل من 500 ألف": 0, "500 ألف - 1 مليون": 0, "أكثر من 1 مليون": 0}
            for b in budgets:
                if b < 500000: categories["أقل من 500 ألف"] += 1
                elif b <= 1000000: categories["500 ألف - 1 مليون"] += 1
                else: categories["أكثر من 1 مليون"] += 1
            return [{"label": k, "value": v} for k, v in categories.items()]
        except Exception:
            return []

    async def generate_monthly_report(self, ai_service) -> AnalyticsReport:
        today = date.today()
        month_start = today.replace(day=1)
        stats = await self.get_basic_stats()
        top_asked = await self.get_top_asked_cars()
        top_booked = await self.get_top_booked_cars()
        budget_trends = await self.get_budget_trends()
        
        data_summary = {
            "month": month_start.strftime("%Y-%m"),
            "total_messages": stats["messages_count"],
            "total_bookings": stats["bookings_count"],
            "top_asked": top_asked,
            "top_booked": top_booked,
            "budget_trends": budget_trends
        }
        
        prompt = f"اكتب تقرير تحليلي بالعامية المصرية لمعرض سيارات بناء على البيانات دي: {json.dumps(data_summary, ensure_ascii=False)}"
        
        from app.core.config import settings
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = await model.generate_content_async(prompt)
        
        report = AnalyticsReport(report_month=month_start, report_text=response.text, metrics_json=data_summary)
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_latest_report(self) -> AnalyticsReport | None:
        try:
            result = await self.db.execute(select(AnalyticsReport).order_by(AnalyticsReport.report_month.desc()).limit(1))
            return result.scalar_one_or_none()
        except Exception:
            return None
