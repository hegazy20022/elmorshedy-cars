from __future__ import annotations
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from models.car import Car
from models.car_image import CarImage
from models.car_financing_option import CarFinancingOption


class CarService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_car_by_id(self, car_id: int) -> Optional[Car]:
        result = await self.db.execute(select(Car).where(Car.car_id == car_id))
        return result.scalar_one_or_none()

    async def search_cars(self, brand: Optional[str], model: Optional[str], model_year: Optional[int]) -> List[Car]:
        from sqlalchemy import or_
        filters = [Car.is_available.is_(True), Car.is_sold.is_(False)]

        if brand:
            # توحيد الماركات المشهورة عشان لو الأونر دخلها غلط أو العميل كتبها بطريقة تانية
            brand_variations = [brand]
            if "تويوتا" in brand: brand_variations.extend(["تيوتا", "تويتا"])
            if "هيونداي" in brand: brand_variations.extend(["هيونداى", "هونداي"])
            if "بي ام" in brand: brand_variations.extend(["بى ام", "bmw"])
            if "بي واي دي" in brand: brand_variations.extend(["بى واى دى", "byd"])
            if "مرسيدس" in brand: brand_variations.extend(["مارسيدس", "mercedes"])

            brand_filters = [Car.brand.ilike(f"%{v}%") for v in brand_variations]
            filters.append(or_(*brand_filters))

        if model:
            # توحيد الموديلات المشهورة عشان لو الأونر دخلها غلط أو العميل كتبها بطريقة تانية
            model_variations = [model]
            if "كورولا" in model: model_variations.extend(["كرولا", "كرولة"])
            if "النترا" in model: model_variations.extend(["انترا", "الانترا"])
            if "سيراتو" in model: model_variations.extend(["سراتو", "سريتو"])
            if "أكسنت" in model or "اكسنت" in model: model_variations.extend(["اكسينت", "اكسنت", "أكسنت"])
            if "أوبترا" in model or "اوبترا" in model: model_variations.extend(["اوبتره", "اوبترا", "أوبترا"])

            model_filters = [Car.model.ilike(f"%{v}%") for v in model_variations]
            filters.append(or_(*model_filters))

        if model_year:
            filters.append(Car.model_year == model_year)

        result = await self.db.execute(
            select(Car).where(and_(*filters)).order_by(Car.created_at.desc()).limit(10)
        )
        return list(result.scalars().all())

    async def search_loose_by_text(self, text: str) -> List[Car]:
        result = await self.db.execute(
            select(Car).where(
                and_(
                    Car.is_available.is_(True),
                    Car.is_sold.is_(False),
                    func.coalesce(Car.car_name, "").ilike(f"%{text}%"),
                )
            ).limit(10)
        )
        return list(result.scalars().all())

    async def get_financing_options(self, car_id: int) -> List[CarFinancingOption]:
        result = await self.db.execute(
            select(CarFinancingOption)
            .where(CarFinancingOption.car_id == car_id)
            .order_by(CarFinancingOption.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_car_images(self, car_id: int) -> List[str]:
        result = await self.db.execute(
            select(CarImage)
            .where(CarImage.car_id == car_id)
            .order_by(CarImage.display_order.asc())
        )
        images = result.scalars().all()
        return [img.image_url for img in images]

    def _score_car(
        self,
        car: Car,
        budget: Decimal,
        preferred_transmission: Optional[str] = None,
        preferred_body_type: Optional[str] = None,
        preferred_fuel_type: Optional[str] = None,
        wants_reliable: bool = False,
        wants_family_car: bool = False,
        wants_economic: bool = False,
        wants_city_car: bool = False,
    ) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []

        if car.cash_price is not None:
            price_gap = abs(Decimal(car.cash_price) - budget)
            if price_gap <= budget * Decimal("0.05"):
                score += 40
                reasons.append("قريبة جدًا من الميزانية")
            elif price_gap <= budget * Decimal("0.10"):
                score += 30
                reasons.append("قريبة من الميزانية")
            elif price_gap <= budget * Decimal("0.20"):
                score += 20
                reasons.append("في رينج قريب من الميزانية")

        if preferred_transmission and car.transmission == preferred_transmission:
            score += 15
            reasons.append("مطابقة لناقل الحركة المطلوب")

        if preferred_body_type and car.body_type == preferred_body_type:
            score += 15
            reasons.append("مطابقة لفئة العربية المطلوبة")

        if preferred_fuel_type and car.fuel_type == preferred_fuel_type:
            score += 10
            reasons.append("مطابقة لنوع الوقود المطلوب")

        usage_tags = car.usage_tags or []

        if wants_reliable:
            if "اعتمادية" in usage_tags:
                score += 20
                reasons.append("مناسبة كاعتمادية وصيانة")

        if wants_family_car:
            if car.family_friendly or "عائلية" in usage_tags:
                score += 20
                reasons.append("مناسبة للاستخدام العائلي")

        if wants_economic:
            if car.fuel_economy_level == "high" or "اقتصادية" in usage_tags:
                score += 20
                reasons.append("موفرة في الاستهلاك")

        if wants_city_car:
            if car.city_friendly or "مدينة" in usage_tags:
                score += 15
                reasons.append("مناسبة للمشاوير والمدينة")

        return score, reasons

    async def recommend_by_budget_and_preferences(
        self,
        budget: Decimal,
        preferred_transmission: Optional[str] = None,
        preferred_body_type: Optional[str] = None,
        preferred_fuel_type: Optional[str] = None,
        wants_reliable: bool = False,
        wants_family_car: bool = False,
        wants_economic: bool = False,
        wants_city_car: bool = False,
        limit: int = 5,
    ) -> List[dict]:
        low = budget * Decimal("0.70")
        high = budget * Decimal("1.30")

        result = await self.db.execute(
            select(Car).where(
                and_(
                    Car.is_available.is_(True),
                    Car.is_sold.is_(False),
                    Car.cash_price.is_not(None),
                    Car.cash_price >= low,
                    Car.cash_price <= high,
                )
            ).limit(50)
        )
        cars = list(result.scalars().all())

        scored = []
        for car in cars:
            score, reasons = self._score_car(
                car=car,
                budget=budget,
                preferred_transmission=preferred_transmission,
                preferred_body_type=preferred_body_type,
                preferred_fuel_type=preferred_fuel_type,
                wants_reliable=wants_reliable,
                wants_family_car=wants_family_car,
                wants_economic=wants_economic,
                wants_city_car=wants_city_car,
            )
            scored.append({
                "car": car,
                "score": score,
                "reasons": reasons,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:limit]

    async def recommend_by_budget(self, budget: float, limit: int = 5):
        return await self.recommend_by_budget_and_preferences(
            budget=Decimal(str(budget)),
            limit=limit,
        )

    async def get_alternatives(self, reference_car: Car, limit: int = 3) -> List[Car]:
        if reference_car.cash_price is None:
            return []

        low = reference_car.cash_price * Decimal("0.80")
        high = reference_car.cash_price * Decimal("1.20")

        result = await self.db.execute(
            select(Car).where(
                and_(
                    Car.is_available.is_(True),
                    Car.is_sold.is_(False),
                    Car.car_id != reference_car.car_id,
                    Car.cash_price.is_not(None),
                    Car.cash_price >= low,
                    Car.cash_price <= high,
                )
            ).order_by(func.abs(Car.cash_price - reference_car.cash_price)).limit(limit)
        )
        return list(result.scalars().all())

    async def mark_as_sold(self, car_id: int) -> Optional[Car]:
        car = await self.get_car_by_id(car_id)
        if car:
            car.is_sold = True
            car.is_available = False
            await self.db.commit()
            await self.db.refresh(car)
        return car

    async def format_car_details(self, car: Car, financing_options: Optional[List[CarFinancingOption]] = None) -> str:
        lines = [f"🚗 {car.car_name}"]

        if car.brand:
            lines.append(f"🏷 الماركة: {car.brand}")
        if car.model:
            lines.append(f"📌 الموديل: {car.model}")
        if car.model_year:
            lines.append(f"📅 سنة الإصدار: {car.model_year}")
        if car.color:
            lines.append(f"🎨 اللون: {car.color}")
        if car.mileage is not None:
            lines.append(f"🛣 العداد: {car.mileage:,} كم")
        if car.transmission:
            lines.append(f"⚙️ الفتيس: {car.transmission}")
        if car.fuel_type:
            lines.append(f"⛽ الوقود: {car.fuel_type}")
        if car.body_type:
            lines.append(f"🚘 الفئة: {car.body_type}")
        if car.paint_status:
            lines.append(f"🧱 حالة الرش: {car.paint_status}")
        if car.license_status:
            lines.append(f"📋 حالة الرخصة: {car.license_status}")
        if car.cash_price is not None:
            lines.append(f"💰 السعر كاش: {int(car.cash_price):,} جنيه")
        if car.installment_price is not None:
            lines.append(f"💳 السعر قسط: {int(car.installment_price):,} جنيه")
        if car.description:
            lines.append(f"📝 الوصف: {car.description}")

        if financing_options:
            lines.append("")
            lines.append("تفاصيل التقسيط المتاحة")
            for idx, option in enumerate(financing_options, start=1):
                part = f"{idx} - مقدم {int(option.down_payment or 0):,} جنيه"
                if option.installment_months:
                    part += f" - مدة {option.installment_months} شهر"
                if option.installment_value is not None:
                    part += f" - القسط {int(option.installment_value):,} جنيه"
                if option.total_price is not None:
                    part += f" - الإجمالي {int(option.total_price):,} جنيه"
                if option.notes:
                    part += f" - {option.notes}"
                lines.append(part)

        lines.append("")
        lines.append("ولو تحب أحجز لحضرتك معاد للمعاينة")
        return "\n".join(lines)
    async def find_closest_year_matches(
        self,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        model_year: Optional[int] = None,
        limit: int = 5,
    ) -> List[Car]:
        filters = [Car.is_available.is_(True), Car.is_sold.is_(False)]

        if brand:
            filters.append(Car.brand.ilike(f"%{brand}%"))

        if model:
            filters.append(Car.model.ilike(f"%{model}%"))

        stmt = select(Car).where(and_(*filters))

        if model_year:
            stmt = stmt.order_by(func.abs(Car.model_year - model_year), Car.created_at.desc())
        else:
            stmt = stmt.order_by(Car.created_at.desc())

        result = await self.db.execute(stmt.limit(limit))
        return list(result.scalars().all())

    async def search_same_brand_alternatives(
        self,
        brand: Optional[str],
        exclude_car_id: Optional[int] = None,
        limit: int = 5,
    ) -> List[Car]:
        if not brand:
            return []

        filters = [
            Car.is_available.is_(True),
            Car.is_sold.is_(False),
            Car.brand.ilike(f"%{brand}%"),
        ]

        if exclude_car_id:
            filters.append(Car.car_id != exclude_car_id)

        result = await self.db.execute(
            select(Car)
            .where(and_(*filters))
            .order_by(Car.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
