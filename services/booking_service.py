from __future__ import annotations

from datetime import date, time, datetime
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.booking import Booking
from models.business_info import BusinessInfo


class BookingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def format_time_12h(self, t: time) -> str:
        return t.strftime("%I:%M %p").lstrip("0")

    def format_time_string_12h(self, value: str) -> str:
        parsed = datetime.strptime(value, "%H:%M").time()
        return parsed.strftime("%I:%M %p").lstrip("0")

    async def get_setting(self, key: str) -> Optional[BusinessInfo]:
        result = await self.db.execute(
            select(BusinessInfo).where(BusinessInfo.info_key == key)
        )
        return result.scalar_one_or_none()

    async def get_booking_settings(self) -> dict:
        row = await self.get_setting("booking_settings")
        if row and isinstance(row.info_value, dict):
            return row.info_value

        return {
            "working_days": ["Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"],
            "start_time": "10:00",
            "end_time": "18:00",
            "slot_duration_minutes": 60,
            "emergency_closed_dates": [],
        }

    async def get_business_contact(self) -> dict:
        row = await self.get_setting("business_contact")
        if row and isinstance(row.info_value, dict):
            return row.info_value

        return {
            "phone": "",
            "address": "",
            "location_url": "",
        }

    async def is_within_working_hours(self, booking_date: date, booking_time: time) -> tuple[bool, str]:
        settings = await self.get_booking_settings()

        working_days = settings.get("working_days", [])
        start_time = settings.get("start_time", "10:00")
        end_time = settings.get("end_time", "18:00")

        emergency_days = settings.get("emergency_closed_dates", [])
        if str(booking_date) in emergency_days:
            return False, "المعرض مغلق في هذا اليوم بسبب إجازة أو ظرف طارئ"

        day_name_en = booking_date.strftime("%A")
        if day_name_en not in working_days:
            return False, "المعرض بيشتغل من السبت للخميس فقط والجمعة إجازة"

        start_h, start_m = map(int, start_time.split(":"))
        end_h, end_m = map(int, end_time.split(":"))

        start_obj = time(start_h, start_m)
        end_obj = time(end_h, end_m)

        if not (start_obj <= booking_time <= end_obj):
            return False, (
                f"مواعيد المعاينة من {self.format_time_string_12h(start_time)} "
                f"إلى {self.format_time_string_12h(end_time)}"
            )

        return True, ""

    async def create_booking(
        self,
        customer_id: Optional[int],
        car_id: int,
        booking_date: date,
        booking_time: time,
        customer_name: Optional[str] = None,
        customer_phone: Optional[str] = None,
        customer_address: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Booking:
        day_name = booking_date.strftime("%A")

        booking = Booking(
            customer_id=customer_id,
            car_id=car_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            booking_date=booking_date,
            booking_time=booking_time,
            day_name=day_name,
            booking_status="confirmed",
            notes=notes,
        )
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def get_working_hours_message(self) -> str:
        settings = await self.get_booking_settings()
        start_12h = self.format_time_string_12h(settings.get("start_time", "10:00"))
        end_12h = self.format_time_string_12h(settings.get("end_time", "18:00"))

        return (
            f"مواعيد المعاينة عندنا من السبت للخميس من الساعة {start_12h} "
            f"إلى {end_12h}\n"
            "الجمعة إجازة\n"
            "تحب حضرتك تشرفنا يوم إيه والساعة كام"
        )

    async def format_booking_confirmation(self, booking: Booking, car_name: str) -> str:
        contact = await self.get_business_contact()

        address = contact.get("address", "")
        location_url = contact.get("location_url", "")
        phone = contact.get("phone", "")

        return (
            f"✅ تمام يا فندم\n"
            f"تم تأكيد حجز معاينة {car_name}\n"
            f"📅 يوم {booking.booking_date.strftime('%Y/%m/%d')}\n"
            f"⏰ الساعة {self.format_time_12h(booking.booking_time)}\n\n"
            f"📍 العنوان التفصيلي:\n{address}\n\n"
            f"🗺️ اللوكيشن:\n{location_url}\n\n"
            f"📞 رقم التواصل:\n{phone}"
        )

    async def list_bookings(self) -> List[Booking]:
        result = await self.db.execute(
            select(Booking).order_by(Booking.booking_date.desc(), Booking.booking_time.desc())
        )
        return list(result.scalars().all())

    async def update_booking(self, booking_id: int, data: dict) -> Optional[Booking]:
        result = await self.db.execute(
            select(Booking).where(Booking.booking_id == booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            return None

        for key, value in data.items():
            if hasattr(booking, key):
                setattr(booking, key, value)

        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def delete_booking(self, booking_id: int) -> bool:
        result = await self.db.execute(
            select(Booking).where(Booking.booking_id == booking_id)
        )
        booking = result.scalar_one_or_none()
        if not booking:
            return False

        await self.db.delete(booking)
        await self.db.commit()
        return True
    async def get_booking_by_id(self, booking_id: int) -> Optional[Booking]:
        result = await self.db.execute(
            select(Booking).where(Booking.booking_id == booking_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_booking_for_customer(self, customer_id: Optional[int]) -> Optional[Booking]:
        if not customer_id:
            return None

        result = await self.db.execute(
            select(Booking)
            .where(Booking.customer_id == customer_id)
            .order_by(Booking.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def reschedule_booking(
        self,
        booking_id: int,
        booking_date: date,
        booking_time: time,
    ) -> Optional[Booking]:
        booking = await self.get_booking_by_id(booking_id)
        if not booking:
            return None

        booking.booking_date = booking_date
        booking.booking_time = booking_time
        booking.day_name = booking_date.strftime("%A")

        await self.db.commit()
        await self.db.refresh(booking)
        return booking
