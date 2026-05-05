import pytest
from models.car import Car
from models.customer import Customer


@pytest.mark.asyncio
async def test_create_booking(client, db_session):
    car = Car(
        car_name="تويوتا كورولا",
        brand="تويوتا",
        model="كورولا",
        model_year=2007,
        is_available=True,
        is_sold=False,
    )
    customer = Customer(
        telegram_user_id="999111",
        full_name="أحمد",
    )

    db_session.add(car)
    db_session.add(customer)
    await db_session.commit()
    await db_session.refresh(car)
    await db_session.refresh(customer)

    payload = {
        "car_id": car.car_id,
        "customer_id": customer.customer_id,
        "customer_name": "أحمد",
        "customer_phone": "01000000000",
        "customer_address": "طنطا",
        "booking_date": "2026-04-21",
        "booking_time": "12:00:00",
        "notes": "معاينة أولى"
    }

    response = await client.post("/bookings/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert "booking_id" in data
