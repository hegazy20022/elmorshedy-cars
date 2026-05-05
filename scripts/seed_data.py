import asyncio
from decimal import Decimal

from app.core.database import AsyncSessionLocal
from models.car import Car
from models.car_financing_option import CarFinancingOption
from models.customer import Customer
from models.booking import Booking
from models.cache_entry import CacheEntry
from models.business_info import BusinessInfo


async def seed():
    async with AsyncSessionLocal() as db:
        # business settings check
        existing_settings = await db.execute(
            BusinessInfo.__table__.select().where(BusinessInfo.info_key == "bot_enabled")
        )
        if not existing_settings.first():
            db.add(BusinessInfo(info_key="bot_enabled", info_value={"value": True}))

        # cars
        car1 = Car(
            car_name="تويوتا كورولا",
            brand="تويوتا",
            model="كورولا",
            model_year=2007,
            color="فضي",
            description="عربية بحالة جيدة فبريكة جوه تكييف شغال ومناسبة للاستخدام اليومي",
            license_status="سارية",
            cash_price=Decimal("320000"),
            installment_price=Decimal("370000"),
            transmission="automatic",
            fuel_type="petrol",
            body_type="sedan",
            seats_count=5,
            engine_cc=1600,
            usage_tags=["اعتمادية", "اقتصادية", "عائلية"],
            maintenance_level="low",
            city_friendly=True,
            family_friendly=True,
            fuel_economy_level="high",
            mileage=185000,
            paint_status="partial_repaint",
            is_sold=False,
            is_available=True,
        )

        car2 = Car(
            car_name="هيونداي النترا",
            brand="هيونداي",
            model="النترا",
            model_year=2010,
            color="أسود",
            description="عربية نظيفة ومريحة في السفر ومناسبة للعيلة",
            license_status="سارية",
            cash_price=Decimal("390000"),
            installment_price=Decimal("440000"),
            transmission="automatic",
            fuel_type="petrol",
            body_type="sedan",
            seats_count=5,
            engine_cc=1600,
            usage_tags=["عائلية", "مدينة"],
            maintenance_level="medium",
            city_friendly=True,
            family_friendly=True,
            fuel_economy_level="medium",
            mileage=160000,
            paint_status="original",
            is_sold=False,
            is_available=True,
        )

        db.add_all([car1, car2])
        await db.flush()

        financing1 = CarFinancingOption(
            car_id=car1.car_id,
            down_payment=Decimal("120000"),
            installment_months=36,
            installment_value=Decimal("7000"),
            total_price=Decimal("372000"),
            notes="بدون ضامن",
        )

        financing2 = CarFinancingOption(
            car_id=car2.car_id,
            down_payment=Decimal("150000"),
            installment_months=48,
            installment_value=Decimal("6500"),
            total_price=Decimal("462000"),
            notes="بإجراءات ميسرة",
        )

        customer = Customer(
            telegram_user_id="123456789",
            full_name="عبدالرحمن",
            phone="01000000000",
            address="طنطا",
            username="abdo_test",
            preferred_car_id=None,
        )

        db.add(financing1)
        db.add(financing2)
        db.add(customer)

        await db.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
