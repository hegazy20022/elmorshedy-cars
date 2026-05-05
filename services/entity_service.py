from __future__ import annotations
import re
from datetime import date, time, datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Tuple

CAIRO_TZ = ZoneInfo("Africa/Cairo")
ARABIC_TO_ENGLISH_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

BRAND_MAPPING = {
    "تويوتا": "تويوتا", "تيوتا": "تويوتا",
    "هيونداي": "هيونداي", "هيونداى": "هيونداي",
    "كيا": "كيا",
    "نيسان": "نيسان",
    "شيفروليه": "شيفروليه", "شفروليه": "شيفروليه",
    "بي واي دي": "بي واي دي", "بى واى دى": "بي واي دي",
    "سكودا": "سكودا",
    "فيات": "فيات",
    "أوبل": "أوبل", "اوبل": "أوبل",
    "رينو": "رينو",
    "مرسيدس": "مرسيدس", "مارسيدس": "مرسيدس",
    "بي ام": "بي ام دبليو", "بى ام": "بي ام دبليو", "bmw": "بي ام دبليو",
    "جولف": "فولكس فاجن", "دايو": "دايو"
}


MODELS_AR = [
    "كورولا", "يارس", "أفانزا", "افانزا", "إلنترا", "النترا", "سيراتو", "أكسنت", "اكسنت", "صني", "لانسر", "أوبترا", "اوبترا"
]


MODEL_CORRECTIONS = {
    "كرولا": "كورولا",
    "كرولة": "كورولا",
    "اكورا": "كورولا",
    "النترا": "النترا",
    "الانترا": "النترا",
    "انترا": "النترا",
    "سيراتو": "سيراتو",
    "سراتو": "سيراتو",
    "سريتو": "سيراتو",
    "اكسنت": "أكسنت",
    "اكسينت": "أكسنت",
    "اوبترا": "أوبترا",
    "اوبتره": "أوبترا",
}

DAY_MAP = {
    "السبت": 5, "سبت": 5,
    "الأحد": 6, "احد": 6, "أحد": 6,
    "الاثنين": 0, "الإثنين": 0, "اثنين": 0, "اتنين": 0, "الأتنين": 0,
    "الثلاثاء": 1, "ثلاثاء": 1, "تلات": 1, "الثلاث": 1, "التلات": 1,
    "الأربعاء": 2, "الاربعاء": 2, "أربعاء": 2, "اربع": 2, "الأربع": 2, "الاربع": 2,
    "الخميس": 3, "خميس": 3,
    "الجمعة": 4, "جمعة": 4,
}


class EntityService:
    def extract_car_filters(self, text: str) -> dict:
        text_clean = (text or "").lower().translate(ARABIC_TO_ENGLISH_DIGITS)

        brand = None
        for key, value in BRAND_MAPPING.items():
            if key in text_clean:
                brand = value
                break

        model = None
        for wrong, correct in MODEL_CORRECTIONS.items():
            if wrong in text_clean:
                model = correct
                break
        if not model:
            model = next((m for m in MODELS_AR if m in text_clean), None)

        # تحسين البحث عن السنة ليشمل الحالات اللي بتبدأ بـ "ال" زي "ال2007"
        year_match = re.search(r"(?:^|\s|ال)(19\d{2}|20\d{2})\b", text_clean)
        model_year = int(year_match.group(1)) if year_match else None

        return {
            "brand": brand,
            "model": model,
            "model_year": model_year,
        }

    def extract_customer_info(self, text: str) -> dict:
       text_value = (text or "").strip()

       name = None
       phone = None
       address = None

       phone_match = re.search(r"(01[0125]\d{8})", text_value)
       if phone_match:
          phone = phone_match.group(1)

       name_match = re.search(
        r"(?:الاسم|اسمي|انا|أنا)\s*[:：\-]?\s*([^\n\r\d،,]+)",
        text_value,
        re.IGNORECASE,
    )
       if name_match:
          name = name_match.group(1).strip()

       address_match = re.search(
        r"(?:العنوان|عنواني|ساكن في|ساكن فى|من)\s*[:：\-]?\s*([^\n\r]+)",
        text_value,
        re.IGNORECASE,
    )
       if address_match:
          address = address_match.group(1).strip(" ،,")

       return {
        "full_name": name,
        "phone": phone,
        "address": address,
    }
        
    def extract_preferences(self, text: str) -> dict:
        text_lower = (text or "").lower()

        preferences = {
            "preferred_transmission": None,
            "preferred_body_type": None,
            "preferred_fuel_type": None,
            "wants_reliable": False,
            "wants_family_car": False,
            "wants_economic": False,
            "wants_city_car": False,
        }

        if any(k in text_lower for k in ["اوتوماتيك", "أوتوماتيك", "automatic"]):
            preferences["preferred_transmission"] = "automatic"
        elif any(k in text_lower for k in ["مانيوال", "manual"]):
            preferences["preferred_transmission"] = "manual"

        if any(k in text_lower for k in ["suv", "جيب", "كروس اوفر", "كروس"]):
            preferences["preferred_body_type"] = "suv"
        elif any(k in text_lower for k in ["سيدان", "sedan"]):
            preferences["preferred_body_type"] = "sedan"
        elif any(k in text_lower for k in ["هاتشباك", "هاتش", "hatchback"]):
            preferences["preferred_body_type"] = "hatchback"

        if any(k in text_lower for k in ["بنزين", "petrol"]):
            preferences["preferred_fuel_type"] = "petrol"
        elif any(k in text_lower for k in ["ديزل", "diesel"]):
            preferences["preferred_fuel_type"] = "diesel"
        elif any(k in text_lower for k in ["هايبرد", "hybrid"]):
            preferences["preferred_fuel_type"] = "hybrid"
        elif any(k in text_lower for k in ["غاز", "gas"]):
            preferences["preferred_fuel_type"] = "gas"

        if any(k in text_lower for k in ["اعتماديه", "اعتمادية", "تعيش", "عمليه", "عملية"]):
            preferences["wants_reliable"] = True

        if any(k in text_lower for k in ["عائليه", "عائلية", "للعيله", "للعيلة", "اسره", "أسرة"]):
            preferences["wants_family_car"] = True

        if any(k in text_lower for k in ["اقتصاديه", "اقتصادية", "موفره", "موفرة", "بنزين قليل"]):
            preferences["wants_economic"] = True

        if any(k in text_lower for k in ["للبلد", "للمدينه", "للمدينة", "زحمه", "زحمة", "سهله في الركنه", "سهلة في الركنة"]):
            preferences["wants_city_car"] = True

        return preferences

    def extract_datetime(self, text: str, now: Optional[datetime] = None) -> Tuple[Optional[date], Optional[time]]:
        if now is None:
            now = datetime.now(CAIRO_TZ)
        return self._extract_date(text, now), self._extract_time(text)

    def _extract_date(self, text: str, now: datetime) -> Optional[date]:
        text_lower = (text or "").strip()

        if re.search(r"(النهارده|اليوم)", text_lower):
            return now.date()

        if re.search(r"(بكرة|بكره)", text_lower):
            return (now + timedelta(days=1)).date()

        if re.search(r"(بعد بكرة|بعد بكره)", text_lower):
            return (now + timedelta(days=2)).date()

        for day_name, weekday in DAY_MAP.items():
            if day_name in text_lower:
                days_ahead = (weekday - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                return now.date() + timedelta(days=days_ahead)

        date_match = re.search(r"(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{4}))?", text_lower)
        if date_match:
            try:
                d = int(date_match.group(1))
                m = int(date_match.group(2))
                y = int(date_match.group(3)) if date_match.group(3) else now.year
                return date(y, m, d)
            except ValueError:
                return None

        return None

    def _extract_time(self, text: str) -> Optional[time]:
        text_lower = (text or "").strip().translate(ARABIC_TO_ENGLISH_DIGITS)

        # استخراج الدقائق من الكلمات العربية
        extra_minutes = 0
        if re.search(r"إلا\s*ربع|الا\s*ربع", text_lower):
            extra_minutes = -15  # سيُطبق على الساعة التالية
        elif re.search(r"ونص|ونص|و\s*نص", text_lower):
            extra_minutes = 30
        elif re.search(r"وربع|و\s*ربع", text_lower):
            extra_minutes = 15

        time_match = re.search(
            r"(?:الساعة\s*)?(\d{1,2})(?::(\d{2}))?\s*(صباحاً?|الصبح|am|مساءً?|العصر|المغرب|الليل|pm|الضهر|الظهر)?",
            text_lower,
            re.IGNORECASE,
        )
        if not time_match:
            return None

        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        period = (time_match.group(3) or "").strip().lower()

        # تطبيق الدقائق الإضافية من "ونص" أو "وربع" أو "إلا ربع"
        if extra_minutes == -15:
            # "إلا ربع" يعني الساعة التالية ناقص ربع
            hour += 1
            minute = 45
        elif extra_minutes > 0 and minute == 0:
            minute = extra_minutes

        if period in ("مساءً", "مساء", "العصر", "المغرب", "الليل", "pm"):
            if hour < 12:
                hour += 12
        elif period in ("صباحاً", "صباح", "الصبح", "am"):
            if hour == 12:
                hour = 0
        elif period in ("الضهر", "الظهر"):
            if hour < 12:
                hour += 12
        else:
            if 1 <= hour <= 7:
                hour += 12

        try:
            return time(hour % 24, minute)
        except ValueError:
            return None
