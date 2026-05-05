from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.schemas.car import CarCreate, CarUpdate
from models.car import Car
from services.car_service import CarService
from services.cache_service import CacheService

router = APIRouter(prefix="/cars", tags=["cars"])

# =============================================
# تطبيع أسماء الماركات والموديلات تلقائياً
# عشان الأونر يكتب زي ما يريد والنظام يصلح قبل الحفظ
# =============================================
BRAND_NORMALIZE = {
    "تيوتا": "تويوتا", "تويتا": "تويوتا", "تيوتا": "تويوتا",
    "هيونداى": "هيونداي", "هونداي": "هيونداي",
    "بى ام": "بي ام دبليو", "بي ام": "بي ام دبليو", "bmw": "بي ام دبليو",
    "بى واى دى": "بي واي دي", "byd": "بي واي دي",
    "مارسيدس": "مرسيدس", "mercedes": "مرسيدس",
    "شفروليه": "شيفروليه",
    "اوبل": "أوبل",
}

MODEL_NORMALIZE = {
    "كرولا": "كورولا", "كرولة": "كورولا",
    "انترا": "النترا", "الانترا": "النترا",
    "سراتو": "سيراتو", "سريتو": "سيراتو",
    "اكسينت": "أكسنت", "اكسنت": "أكسنت",
    "اوبترا": "أوبترا", "اوبتره": "أوبترا",
    "افانزا": "أفانزا",
}

def normalize_car_data(brand: str | None, model: str | None, car_name: str | None):
    """تطبيع أسماء الماركات والموديلات عند الإدخال"""
    # تطبيع الماركة
    if brand:
        brand_lower = brand.strip().lower()
        for wrong, correct in BRAND_NORMALIZE.items():
            if wrong.lower() in brand_lower:
                brand = correct
                break

    # تطبيع الموديل
    if model:
        model_lower = model.strip().lower()
        for wrong, correct in MODEL_NORMALIZE.items():
            if wrong.lower() in model_lower:
                model = correct
                break

    # تطبيع الاسم الكامل (بناءً على الماركة والموديل بعد التصحيح)
    if car_name and brand and model:
        car_name = f"{brand} {model}"
    elif car_name:
        # تصحيح الاسم بشكل مستقل
        for wrong, correct in {**BRAND_NORMALIZE, **MODEL_NORMALIZE}.items():
            car_name = car_name.replace(wrong, correct)

    return brand, model, car_name



@router.get("/")
async def list_cars(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Car).order_by(Car.created_at.desc()))
    cars = result.scalars().all()

    return [
        {
            "car_id": car.car_id,
            "car_name": car.car_name,
            "brand": car.brand,
            "model": car.model,
            "model_year": car.model_year,
            "color": car.color,
            "description": car.description,
            "license_status": car.license_status,
            "cash_price": float(car.cash_price) if car.cash_price is not None else None,
            "installment_price": float(car.installment_price) if car.installment_price is not None else None,
            "transmission": car.transmission,
            "fuel_type": car.fuel_type,
            "body_type": car.body_type,
            "engine_cc": car.engine_cc,
            "usage_tags": car.usage_tags,
            "class_level": car.class_level,
            "city_friendly": car.city_friendly,
            "family_friendly": car.family_friendly,
            "fuel_economy_level": car.fuel_economy_level,
            "mileage": car.mileage,
            "paint_status": car.paint_status,
            "is_sold": car.is_sold,
            "is_available": car.is_available,
            "created_at": car.created_at.isoformat() if car.created_at else None,
        }
        for car in cars
    ]


@router.post("/")
async def create_car_dashboard(
    payload: CarCreate,
    db: AsyncSession = Depends(get_db),
):
    data = payload.model_dump()
    # تطبيع البيانات تلقائياً قبل الحفظ
    data["brand"], data["model"], data["car_name"] = normalize_car_data(
        data.get("brand"), data.get("model"), data.get("car_name")
    )
    car = Car(**data)
    db.add(car)
    await db.commit()
    await db.refresh(car)
    return {"ok": True, "car_id": car.car_id}


@router.put("/{car_id}")
async def update_car_dashboard(
    car_id: int,
    payload: CarUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Car).where(Car.car_id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    data = payload.model_dump(exclude_unset=True)
    
    # تطبيع البيانات تلقائياً عند التعديل
    brand = data.get("brand", car.brand)
    model = data.get("model", car.model)
    car_name = data.get("car_name", car.car_name)
    data["brand"], data["model"], data["car_name"] = normalize_car_data(brand, model, car_name)

    for key, value in data.items():
        if hasattr(car, key):
            setattr(car, key, value)

    await db.commit()
    await db.refresh(car)

    cache_service = CacheService(db)
    await cache_service.invalidate_by_car(car_id)

    return {"ok": True}


@router.delete("/{car_id}")
async def delete_car_dashboard(
    car_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Car).where(Car.car_id == car_id))
    car = result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    await db.delete(car)
    await db.commit()
    return {"ok": True}


@router.post("/{car_id}/mark-sold")
async def mark_car_sold(car_id: int, db: AsyncSession = Depends(get_db)):
    car_service = CarService(db)
    cache_service = CacheService(db)

    car = await car_service.mark_as_sold(car_id)
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")

    invalidated = await cache_service.invalidate_by_car(car_id)
    return {"ok": True, "car_id": car_id, "invalidated_cache_entries": invalidated}
