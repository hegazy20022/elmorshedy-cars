import asyncio
import os
import sys

# Fix encoding for Arabic output on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.getcwd())

from app.core.database import AsyncSessionLocal
from models.car import Car
from sqlalchemy import select, update

BRAND_FIXES = {
    "تيوتا": "تويوتا",
    "تويتا": "تويوتا",
    "هيونداى": "هيونداي",
    "بى ام": "بي ام دبليو",
    "بي ام": "بي ام دبليو",
    "بى واى دى": "بي واي دي",
    "مارسيدس": "مرسيدس",
}

# تصحيح أسماء الموديلات في قاعدة البيانات
MODEL_FIXES = {
    "كرولا": "كورولا",
    "كرولة": "كورولا",
    "انترا": "النترا",
    "الانترا": "النترا",
    "سراتو": "سيراتو",
    "سريتو": "سيراتو",
    "اكسينت": "أكسنت",
    "اوبتره": "أوبترا",
}

async def fix_brands():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Car))
        cars = result.scalars().all()
        
        updates_count = 0
        for car in cars:
            original_brand = car.brand or ""
            original_model = car.model or ""
            original_name = car.car_name or ""
            
            # تصحيح الماركة
            new_brand = original_brand
            for wrong, correct in BRAND_FIXES.items():
                if wrong in original_brand:
                    new_brand = original_brand.replace(wrong, correct)
                    break
            
            # تصحيح الموديل
            new_model = original_model
            for wrong, correct in MODEL_FIXES.items():
                if wrong in original_model:
                    new_model = original_model.replace(wrong, correct)
                    break
            
            # تصحيح اسم العربية الكامل (brand + model variations)
            new_name = original_name
            for wrong, correct in {**BRAND_FIXES, **MODEL_FIXES}.items():
                if wrong in new_name:
                    new_name = new_name.replace(wrong, correct)
            
            if new_brand != original_brand or new_model != original_model or new_name != original_name:
                print(f"Updating Car ID {car.car_id}:")
                if new_brand != original_brand:
                    print(f"  Brand: '{original_brand}' -> '{new_brand}'")
                if new_model != original_model:
                    print(f"  Model: '{original_model}' -> '{new_model}'")
                if new_name != original_name:
                    print(f"  Name:  '{original_name}' -> '{new_name}'")
                
                car.brand = new_brand
                car.model = new_model
                car.car_name = new_name
                updates_count += 1
        
        if updates_count > 0:
            await db.commit()
            print(f"\nSuccessfully updated {updates_count} cars.")
        else:
            print("\nNo data needed fixing.")

if __name__ == "__main__":
    asyncio.run(fix_brands())
