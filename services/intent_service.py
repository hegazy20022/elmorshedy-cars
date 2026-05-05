from __future__ import annotations
import re
from typing import Optional
from decimal import Decimal

INTENT_GREETING = "greeting"
INTENT_ASK_SPECIFIC_CAR = "ask_specific_car"
INTENT_RECOMMEND_BY_BUDGET = "recommend_by_budget"
INTENT_SUGGEST_ALTERNATIVES = "suggest_alternatives"
INTENT_BOOKING_REQUEST = "booking_request"
INTENT_THANKS = "thanks"
INTENT_CONFIRM_BOOKING = "confirm_booking"
INTENT_RESCHEDULE_BOOKING = "reschedule_booking"
INTENT_UNKNOWN = "unknown"

ARABIC_TO_ENGLISH_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


class IntentService:
    def classify(self, text: str) -> str:
        text_clean = (text or "").strip().lower()
        normalized = text_clean.translate(ARABIC_TO_ENGLISH_DIGITS)

        greeting_keywords = [
            "اهلا", "أهلا", "السلام", "سلام", "هاي", "hello", "hi",
            "هالو", "هلا", "الو", "ألو", "صباح الخير", "مساء الخير",
            "ازيك", "عامل ايه", "عامل إيه", "اخبارك", "أخبارك"
        ]
        if self._contains_any(normalized, greeting_keywords):
            return INTENT_GREETING

        if self._contains_any(normalized, [
            "شكرا", "شكرًا", "متشكر", "متشكرين", "تسلم", "تسلمي",
            "ميرسي", "تشرفت بيكم", "تشرفت", "الف شكر", "ألف شكر"
        ]):
            return INTENT_THANKS

        if self._contains_any(normalized, [
            "تمام", "تمام كده", "أكيد", "اكيد", "أكدلي", "اكدلي",
            "ثبتلي", "ثبته", "تأكيد", "تاكيد", "confirm", "confirmed",
            "ماشي", "موافق", "تمام المعاد", "اتفقنا", "اشطا", "قشطة", "اشطه", "قشطه"
        ]):
            return INTENT_CONFIRM_BOOKING

        if self._contains_any(normalized, [
            "غير المعاد", "غيّر المعاد", "أغير المعاد", "اغير المعاد",
            "تغيير المعاد", "تعديل المعاد", "أعدل المعاد", "اعدل المعاد",
            "أأجل", "اجل", "تأجيل", "أقدم المعاد", "اقدم المعاد",
            "أبدل المعاد", "ابدل المعاد", "عايز معاد تاني", "عايز يوم تاني",
            "المعاد مش مناسب", "ينفع أغير", "ينفع اغير", "ينفع أأجل", "ينفع اجل"
        ]):
            return INTENT_RESCHEDULE_BOOKING

        if self._contains_any(normalized, [
            "بديل", "بدائل", "غيرها", "تاني", "قريب من السعر",
            "شبه", "أرخص", "اغلى", "أغلى"
        ]):
            return INTENT_SUGGEST_ALTERNATIVES

        if self._contains_any(normalized, [
            "احجز", "حجز", "ميعاد", "معاد", "معاينة", "أجي", "اجي",
            "أزور", "ازور", "بكرة", "بكره", "الساعة", "عايز احجز","ابص عالعربيه"
        ]):
            return INTENT_BOOKING_REQUEST

        budget = self.extract_budget(normalized)
        if budget is not None:
            return INTENT_RECOMMEND_BY_BUDGET

        ask_keywords = [
            "سعر", "بكام", "قسط", "رخصة", "حالة", "تفاصيل", "عندكو", "عندكم",
            "متاح", "موجود", "وريني", "ايه", "العربية دي", "العربيه دي",
            "العربية دى", "العربيه دى", "اللي في الإعلان", "اللى في الإعلان",
            "اللي نزلتوها", "اللى نزلتوها", "اللي نزلت", "اللى نزلت",
            "العربية اللي", "العربيه اللي", "العربية اللى", "العربيه اللى",
            "مواصفات", "بيانات", "صور", "شكلها", "عنها"
        ]
        car_keywords = [
            "تويوتا", "تيوتا", "هيونداي", "هيونداى", "كيا", "نيسان", "شيفروليه", "شفروليه", "سكودا", "فيات",
            "رينو", "بي واي دي", "بى واى دى", "اوبل", "أوبل",
            "كورولا", "كرولا", "كرولة",   # كورولا وأخطاؤها الشائعة
            "يارس", "إلنترا", "النترا", "انترا", "الانترا",  # النترا وأخطاؤها
            "سيراتو", "سراتو", "سريتو",   # سيراتو وأخطاؤها
            "أكسنت", "اكسنت", "اكسينت",
            "صني", "لانسر", "أوبترا", "اوبترا", "اوبتره",
            "افانزا", "أفانزا", "مرسيدس", "بى ام", "بى ام دبيو", "بي ام دبليو", "bmw",
            "مارسيدس", "جولف", "دايو"
        ]

        if self._contains_any(normalized, ask_keywords) and self._contains_any(normalized, car_keywords):
            return INTENT_ASK_SPECIFIC_CAR

        if self._contains_any(normalized, car_keywords):
            return INTENT_ASK_SPECIFIC_CAR

        # التعرف على السنة فقط كاستفسار عن عربية
        year_match = re.search(r"(?:^|\s|ال)(19\d{2}|20\d{2})\b", normalized)
        if year_match and not self.extract_budget(normalized):
            return INTENT_ASK_SPECIFIC_CAR
            
        # التعرف على الضمائر أو "دي" كاستفسار عن عربية (لو فيه سياق سابق)
        if self._contains_any(normalized, ["دي", "دى", "مواصفاتها", "سعرها", "صورتها", "تفاصيلها"]):
            return INTENT_ASK_SPECIFIC_CAR

        return INTENT_UNKNOWN

    def extract_budget(self, text: str) -> Optional[Decimal]:
        text = (text or "").translate(ARABIC_TO_ENGLISH_DIGITS)
        text = text.replace("،", "").replace(",", "")
        text = text.replace("ألف", "الف").strip()
        phone_match = re.search(r"\b01[0125]\d{8}\b", text)
        if phone_match:
           return None

        personal_info_hints = [
        "رقمي", "رقم الموبايل", "الموبايل", "هاتفي", "هاتف",
        "رقم التواصل", "الاسم", "اسمي", "عنواني", "العنوان","اسمى"
          ]
        if any(hint in text.lower() for hint in personal_info_hints):
           return None
        has_budget_hint = any(
            k in text.lower()
            for k in [
                "الف", "k", "مليون", "million", "m",
                "ميزانية", "معايا", "في حدود", "بحدود",
                "اقل من", "أقل من", "اكتر من", "أكتر من",
                "كاش", "قسط", "سعر", "بكام"
            ]
        )

        patterns = [
            (r"(\d+(?:\.\d+)?)\s*(الف|k)\b", lambda m: float(m.group(1)) * 1000),
            (r"(\d+(?:\.\d+)?)\s*(مليون|million|m)\b", lambda m: float(m.group(1)) * 1_000_000),
            (r"\b(\d{6,})\b", lambda m: float(m.group(1))),
            (r"\b(\d{3,5})\b", lambda m: float(m.group(1)) * (1000 if float(m.group(1)) < 10000 else 1)),
        ]

        for pattern, converter in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    raw_value = match.group(1)

                    if raw_value.isdigit():
                        num = int(raw_value)
                        if 1950 <= num <= 2035 and not has_budget_hint:
                            continue

                    value = converter(match)
                    if value >= 1000:
                        return Decimal(str(int(value)))
                except Exception:
                    continue

        return None

    def extract_car_name(self, text: str) -> Optional[str]:
        text_clean = (text or "").strip()
        if not text_clean:
            return None

        known_keywords = [
            "تويوتا", "كورولا", "هيونداي", "النترا", "إلنترا", "كيا", "سيراتو",
            "بي ام", "bmw", "مرسيدس", "نيسان", "شيفروليه", "رينو", "سكودا",
            "يارس", "صني", "اوبترا", "أوبترا", "افانزا", "أفانزا"
        ]

        found = [kw for kw in known_keywords if kw.lower() in text_clean.lower()]
        if found:
            return " ".join(found)

        return None

    def _contains_any(self, text: str, keywords: list[str]) -> bool:
        return any(k.lower() in text.lower() for k in keywords)
