# =========================
# TABLE NAMES
# =========================

TABLE_LABELS_AR = {
    "bookings": "الحجوزات",
    "cars": "العربيات",
    "conversations": "المحادثات",
    "control": "التحكم",
    "cache": "الكاش",
    "logs": "السجلات والأخطاء",
    "metrics": "المؤشرات",
}


COLUMN_LABELS_AR = {
    "bookings": {
        "booking_id": "رقم الحجز",
        "car_id": "رقم العربية",
        "customer_id": "رقم العميل",
        "customer_name": "اسم العميل",
        "customer_phone": "هاتف العميل",
        "customer_address": "العنوان",
        "booking_date": "تاريخ الحجز",
        "booking_time": "وقت الحجز",
        "day_name": "اليوم",
        "booking_status": "الحالة",
        "notes": "ملاحظات",
        "created_at": "تاريخ الإنشاء",
        "updated_at": "آخر تعديل",
    },

    "cars": {
        "car_id": "رقم العربية",
        "car_name": "اسم العربية",
        "brand": "الماركة",
        "model": "الموديل",
        "model_year": "سنة الإصدار",
        "color": "اللون",
        "description": "الوصف",
        "license_status": "حالة الرخصة",
        "cash_price": "السعر كاش",
        "installment_price": "السعر قسط",
        "transmission": "الفتيس",
        "fuel_type": "نوع الوقود",
        "body_type": "نوع العربية",
        "engine_cc": "سعة الموتور",
        "usage_tags": "الميزات",
        "class_level": "فئه العربيه",
        "city_friendly": "مناسبة للمدينة",
        "family_friendly": "مناسبة للعائلة",
        "fuel_economy_level": "استهلاك البنزين",
        "mileage": "العداد",
        "paint_status": "حالة الرش",
        "is_sold": "تم البيع",
        "is_available": "متاحة",
        "created_at": "تاريخ الإضافة",
        "updated_at": "آخر تعديل",
    },

    "cache": {
        "cache_id": "رقم الكاش",
        "car_id": "رقم العربية",
        "intent": "النية",
        "raw_question": "السؤال الأصلي",
        "normalized_question": "السؤال الموحّد",
        "cache_key": "المفتاح",
        "repeat_count": "عدد التكرار",
        "cached_answer": "الرد المخزن",
        "is_active": "نشط",
        "expires_at": "تاريخ الانتهاء",
        "last_hit_at": "آخر استخدام",
        "created_at": "تاريخ الإنشاء",
        "updated_at": "آخر تعديل",
    },

    "conversations": {
        "telegram_user_id": "رقم تيليجرام",
        "customer_name": "اسم العميل",
        "username": "يوزر العميل",
        "phone": "الهاتف",
        "last_message": "آخر رسالة",
        "mode": "وضع المحادثة",
        "context": "السياق",
    },

    "logs": {
        "level": "المستوى",
        "message": "الرسالة",
        "logger": "المصدر",
        "time": "الوقت",
        "exception": "الاستثناء",
        "path": "المسار",
        "method": "الطريقة",
        "request_id": "رقم الطلب",
        "status_code": "كود الحالة",
        "duration_ms": "المدة (مللي ثانية)",
        "telegram_user_id": "رقم تيليجرام",
        "intent": "النية",
        "car_id": "رقم العربية",
        "customer_id": "رقم العميل",
        "booking_date": "تاريخ الحجز",
        "booking_time": "وقت الحجز",
        "repeat_count": "عدد التكرار",
        "normalized_question": "السؤال الموحّد",
        "error": "الخطأ",
    },

    "metrics": {
        "messages": "عدد الرسائل",
        "bookings": "عدد الحجوزات",
        "errors": "عدد الأخطاء",
        "cache_hits": "نجاح الكاش",
        "cache_misses": "فشل الكاش",
    },
}


VALUE_LABELS_AR = {
    "booking_status": {
        "confirmed": "مؤكد",
        "cancelled": "ملغي",
        "completed": "مكتمل",
    },

    "mode": {
        "AI": "الذكاء الاصطناعي",
        "OWNER": "يدوي بواسطة الأونر",
        "PAUSED": "موقوف",
    },

    "intent": {
        "greeting": "ترحيب",
        "ask_specific_car": "استفسار عن عربية",
        "recommend_by_budget": "ترشيح حسب الميزانية",
        "suggest_alternatives": "اقتراح بدائل",
        "booking_request": "طلب حجز",
        "unknown": "غير معروف",
    },

    "bool": {
        True: "نعم",
        False: "لا",
    },
}
