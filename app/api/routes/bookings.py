from datetime import date, time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.booking import BookingCreate, BookingUpdate
from services.booking_service import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def list_bookings(db: AsyncSession = Depends(get_db)):
    service = BookingService(db)
    bookings = await service.list_bookings()

    return [
        {
            "رقم_الحجز": b.booking_id,
            "رقم_العربية": b.car_id,
            "رقم_العميل": b.customer_id,
            "اسم_العميل": b.customer_name,
            "هاتف_العميل": b.customer_phone,
            "العنوان": b.customer_address,
            "تاريخ_الحجز": b.booking_date.isoformat() if b.booking_date else None,
            "وقت_الحجز": str(b.booking_time) if b.booking_time else None,
            "اليوم": b.day_name,
            "الحالة": b.booking_status,
            "ملاحظات": b.notes,
        }
        for b in bookings
    ]


@router.post("/")
async def create_booking_dashboard(
    payload: BookingCreate,
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)

    booking = await service.create_booking(
        customer_id=payload.customer_id,
        car_id=payload.car_id,
        booking_date=payload.booking_date,
        booking_time=payload.booking_time,
        customer_name=payload.customer_name,
        customer_phone=payload.customer_phone,
        customer_address=payload.customer_address,
        notes=payload.notes,
    )
    return {"ok": True, "booking_id": booking.booking_id}


@router.put("/{booking_id}")
async def update_booking_dashboard(
    booking_id: int,
    payload: BookingUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)
    booking = await service.update_booking(booking_id, payload.model_dump(exclude_unset=True))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"ok": True}


@router.delete("/{booking_id}")
async def delete_booking_dashboard(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = BookingService(db)
    deleted = await service.delete_booking(booking_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"ok": True}
