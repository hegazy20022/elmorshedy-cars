from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.customer import Customer


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, telegram_user_id: str, username: Optional[str] = None, full_name: Optional[str] = None) -> tuple[Customer, bool]:
        result = await self.db.execute(
            select(Customer).where(Customer.telegram_user_id == telegram_user_id)
        )
        customer = result.scalar_one_or_none()

        if customer:
            updated = False
            if username and customer.username != username:
                customer.username = username
                updated = True
            if full_name and not customer.full_name:
                customer.full_name = full_name
                updated = True
            if updated:
                await self.db.commit()
                await self.db.refresh(customer)
            return customer, False

        customer = Customer(
            telegram_user_id=telegram_user_id,
            username=username,
            full_name=full_name,
        )
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer, True

    async def get_by_telegram_id(self, telegram_user_id: str) -> Optional[Customer]:
        result = await self.db.execute(
            select(Customer).where(Customer.telegram_user_id == telegram_user_id)
        )
        return result.scalar_one_or_none()

    async def update_customer_info(
        self,
        telegram_user_id: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Optional[Customer]:
        customer = await self.get_by_telegram_id(telegram_user_id)
        if not customer:
            return None

        if full_name:
            customer.full_name = full_name
        if phone:
            customer.phone = phone
        if address:
            customer.address = address

        await self.db.commit()
        await self.db.refresh(customer)
        return customer
