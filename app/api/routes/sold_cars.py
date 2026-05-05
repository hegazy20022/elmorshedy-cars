from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from models.sold_car import SoldCar

router = APIRouter(prefix="/sold-cars", tags=["sold-cars"])


@router.get("")
async def list_sold_cars(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SoldCar).order_by(SoldCar.sale_id.desc())
    )
    rows = list(result.scalars().all())

    return [
        {
            "sale_id": row.sale_id,
            "car_id": row.car_id,
            "customer_id": row.customer_id,
            "buyer_name": row.buyer_name,
            "buyer_phone": row.buyer_phone,
            "buyer_address": row.buyer_address,
            "cash_price": float(row.cash_price) if row.cash_price is not None else None,
            "down_payment": float(row.down_payment) if row.down_payment is not None else None,
            "remaining_amount": float(row.remaining_amount) if row.remaining_amount is not None else None,
            "installment_months": row.installment_months,
            "installment_end_date": str(row.installment_end_date) if row.installment_end_date else None,
            "installment_value": float(row.installment_value) if row.installment_value is not None else None,
            "sold_at": row.sold_at.isoformat() if row.sold_at else None,
        }
        for row in rows
    ]


@router.post("")
async def create_sold_car(
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    row = SoldCar(
        car_id=payload.get("car_id"),
        customer_id=payload.get("customer_id"),
        buyer_name=payload.get("buyer_name"),
        buyer_phone=payload.get("buyer_phone"),
        buyer_address=payload.get("buyer_address"),
        cash_price=payload.get("cash_price"),
        down_payment=payload.get("down_payment"),
        remaining_amount=payload.get("remaining_amount"),
        installment_months=payload.get("installment_months"),
        installment_end_date=payload.get("installment_end_date"),
        installment_value=payload.get("installment_value"),
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)

    return {"ok": True, "sale_id": row.sale_id}


@router.put("/{sale_id}")
async def update_sold_car(
    sale_id: int,
    payload: dict = Body(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SoldCar).where(SoldCar.sale_id == sale_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="عملية البيع غير موجودة")

    allowed_fields = [
        "car_id",
        "customer_id",
        "buyer_name",
        "buyer_phone",
        "buyer_address",
        "cash_price",
        "down_payment",
        "remaining_amount",
        "installment_months",
        "installment_end_date",
        "installment_value",
    ]

    for field in allowed_fields:
        if field in payload:
            setattr(row, field, payload[field])

    await db.commit()
    await db.refresh(row)
    return {"ok": True}


@router.delete("/{sale_id}")
async def delete_sold_car(
    sale_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(SoldCar).where(SoldCar.sale_id == sale_id)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="عملية البيع غير موجودة")

    await db.delete(row)
    await db.commit()
    return {"ok": True}
