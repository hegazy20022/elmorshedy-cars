from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from models.purchase_request import PurchaseRequest

router = APIRouter(prefix="/purchase-requests", tags=["purchase-requests"])


@router.get("")
async def list_purchase_requests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PurchaseRequest).order_by(PurchaseRequest.request_id.desc())
    )
    rows = list(result.scalars().all())

    return [
        {
            "request_id": row.request_id,
            "seller_name": row.seller_name,
            "seller_phone": row.seller_phone,
            "seller_address": row.seller_address,
            "car_name": row.car_name,
            "brand": row.brand,
            "model": row.model,
            "model_year": row.model_year,
            "color": row.color,
            "license_status": row.license_status,
            "description": row.description,
            "asking_price": float(row.asking_price) if row.asking_price is not None else None,
            "status": row.status,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
        for row in rows
    ]


@router.post("")
async def create_purchase_request(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    row = PurchaseRequest(
        seller_name=payload.get("seller_name"),
        seller_phone=payload.get("seller_phone"),
        seller_address=payload.get("seller_address"),
        car_name=payload.get("car_name"),
        brand=payload.get("brand"),
        model=payload.get("model"),
        model_year=payload.get("model_year"),
        color=payload.get("color"),
        license_status=payload.get("license_status"),
        description=payload.get("description"),
        asking_price=payload.get("asking_price"),
        status=payload.get("status"),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    return {"ok": True, "request_id": row.request_id}


@router.put("/{request_id}")
async def update_purchase_request(
    request_id: int,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PurchaseRequest).where(PurchaseRequest.request_id == request_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="السجل غير موجود")

    allowed_fields = [
        "seller_name",
        "seller_phone",
        "seller_address",
        "car_name",
        "brand",
        "model",
        "model_year",
        "color",
        "license_status",
        "description",
        "asking_price",
        "status",
    ]

    for field in allowed_fields:
        if field in payload:
            setattr(row, field, payload[field])

    await db.commit()
    await db.refresh(row)
    return {"ok": True}


@router.delete("/{request_id}")
async def delete_purchase_request(
    request_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PurchaseRequest).where(PurchaseRequest.request_id == request_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="السجل غير موجود")

    await db.delete(row)
    await db.commit()
    return {"ok": True}
