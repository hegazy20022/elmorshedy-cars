import os
import uuid

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from models.car import Car
from models.car_image import CarImage

router = APIRouter(prefix="/car-images", tags=["car-images"])

UPLOAD_DIR = "uploads/car_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/{car_id}")
async def list_car_images(car_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CarImage)
        .where(CarImage.car_id == car_id)
        .order_by(CarImage.display_order.asc(), CarImage.created_at.asc())
    )
    images = list(result.scalars().all())
    return [
        {
            "image_id": img.image_id,
            "car_id": img.car_id,
            "image_url": img.image_url,
            "display_order": img.display_order,
        }
        for img in images
    ]


@router.post("/{car_id}")
async def upload_car_images(
    car_id: int,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    car_result = await db.execute(select(Car).where(Car.car_id == car_id))
    car = car_result.scalar_one_or_none()
    if not car:
        raise HTTPException(status_code=404, detail="العربية غير موجودة")

    existing_result = await db.execute(
        select(CarImage).where(CarImage.car_id == car_id)
    )
    existing = list(existing_result.scalars().all())

    if len(existing) + len(files) > 10:
        raise HTTPException(status_code=400, detail="الحد الأقصى 10 صور لكل عربية")

    created = []
    order_start = len(existing) + 1

    for idx, file in enumerate(files, start=order_start):
        ext = os.path.splitext(file.filename or "")[1].lower() or ".jpg"
        filename = f"car_{car_id}_{uuid.uuid4().hex}{ext}"
        path = os.path.join(UPLOAD_DIR, filename)

        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)

        image = CarImage(
            car_id=car_id,
            image_url=f"/uploads/car_images/{filename}",
            display_order=idx,
        )
        db.add(image)
        created.append(image)

    await db.commit()

    return {"ok": True, "uploaded_count": len(created)}


@router.delete("/{image_id}")
async def delete_car_image(image_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CarImage).where(CarImage.image_id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="الصورة غير موجودة")

    file_path = image.image_url.lstrip("/")
    if os.path.exists(file_path):
        os.remove(file_path)

    await db.delete(image)
    await db.commit()
    return {"ok": True}
