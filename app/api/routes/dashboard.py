from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/meta")
async def dashboard_meta():
    return {
        "main_page": "الحجوزات",
        "tables": [
            {"key": "bookings", "label_ar": "الحجوزات"},
            {"key": "cars", "label_ar": "العربيات"},
            {"key": "conversations", "label_ar": "المحادثات"},
            {"key": "control", "label_ar": "التحكم"},
            {"key": "cache", "label_ar": "الكاش"},
        ]
    }
