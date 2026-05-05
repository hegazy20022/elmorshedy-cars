import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from models.car import Car
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Car))
        cars = result.scalars().all()
        print(f"Found {len(cars)} cars:")
        for car in cars:
            brand_safe = car.brand.encode('ascii', 'backslashreplace').decode('ascii')
            model_safe = car.model.encode('ascii', 'backslashreplace').decode('ascii')
            print(f"- {brand_safe} | {model_safe} | {car.model_year} | Available: {car.is_available} | Sold: {car.is_sold}")

if __name__ == "__main__":
    asyncio.run(main())
