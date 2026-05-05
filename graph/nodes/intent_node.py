import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from graph.state import AgentState
from services.intent_service import (
    INTENT_BOOKING_REQUEST,
    INTENT_UNKNOWN,
    INTENT_RECOMMEND_BY_BUDGET,
    INTENT_ASK_SPECIFIC_CAR,
    INTENT_THANKS,
    INTENT_CONFIRM_BOOKING,
    INTENT_RESCHEDULE_BOOKING,
    INTENT_GREETING,
)

logger = logging.getLogger(__name__)


async def intent_node(state: AgentState, services: dict) -> AgentState:
    intent_svc = services["intent"]
    entity_svc = services["entity"]
    ai_svc = services["ai"]
    memory = services["memory"]

    text = state.normalized_text or state.raw_input or ""
    text_words_count = len(text.split()) if text else 0

    conv_state = await memory.get_state(state.telegram_user_id)
    current_step = conv_state.current_step if conv_state else None
    
    # تحميل السياق السابق من الذاكرة
    history_ctx = conv_state.context if conv_state else {}
    last_brand = history_ctx.get("last_brand")
    last_model = history_ctx.get("last_model")
    last_year = history_ctx.get("last_model_year")
    last_car_id = history_ctx.get("last_car_id")
    
    # بناء تاريخ بسيط للـ AI
    history_str = ""
    if last_brand or last_model:
        history_str = f"آخر عربية اتكلمنا عنها: {last_brand or ''} {last_model or ''} {last_year or ''}"

    # =========================
    # 1) تحديد النية بالـ rules الأول
    # =========================
    state.intent = intent_svc.classify(text)
            
    # لو العميل استخدم نية واضحة وهو جوه خطوة تانية، نخرجه من الخطوة فوراً
    # استثناء: لو الخطوة والنية متوافقين (مثلاً نية حجز وهو في خطوة بيانات الحجز)
    should_clear_step = False
    if current_step:
        if state.intent in [INTENT_THANKS, INTENT_GREETING, INTENT_RECOMMEND_BY_BUDGET, INTENT_ASK_SPECIFIC_CAR]:
            should_clear_step = True
        elif current_step == "awaiting_reschedule_datetime" and state.intent == INTENT_BOOKING_REQUEST:
            should_clear_step = True
        elif current_step == "awaiting_booking_customer_info" and state.intent == INTENT_RESCHEDULE_BOOKING:
            should_clear_step = True
        
    if should_clear_step:
        await memory.update_state(state.telegram_user_id, current_step=None)
        current_step = None

    # =========================
    # 2) استخراج بيانات العربية
    # =========================
    filters = entity_svc.extract_car_filters(text)
    state.brand = filters.get("brand")
    state.model = filters.get("model")
    state.model_year = filters.get("model_year")

    extract_car_name = getattr(intent_svc, "extract_car_name", None)
    if callable(extract_car_name):
        car_name = extract_car_name(text)
        if car_name:
            state.extracted_car_name = car_name

    # =========================
    # 3) استخراج التفضيلات
    # =========================
    preferences = entity_svc.extract_preferences(text)
    state.preferred_transmission = preferences.get("preferred_transmission")
    state.preferred_body_type = preferences.get("preferred_body_type")
    state.preferred_fuel_type = preferences.get("preferred_fuel_type")
    state.wants_reliable = preferences.get("wants_reliable", False)
    state.wants_family_car = preferences.get("wants_family_car", False)
    state.wants_economic = preferences.get("wants_economic", False)
    state.wants_city_car = preferences.get("wants_city_car", False)

    # =========================
    # 4) استخراج الميزانية
    # مهم جدا لا تستخرج ميزانية أثناء إدخال بيانات الحجز
    # =========================
    if current_step not in ["awaiting_booking_customer_info", "awaiting_reschedule_datetime"]:
        extract_budget = getattr(intent_svc, "extract_budget", None)
        if callable(extract_budget):
            budget = extract_budget(text)
            if budget is not None:
                try:
                    state.extracted_budget = float(budget)
                except Exception:
                    state.extracted_budget = budget

    # =========================
    # 5) هل نحتاج Gemini fallback
    # =========================
    missing_entities = (
        (state.intent == INTENT_RECOMMEND_BY_BUDGET and not state.extracted_budget)
        or (
            state.intent == INTENT_ASK_SPECIFIC_CAR
            and not (state.brand or state.model or state.model_year or getattr(state, "extracted_car_name", None))
        )
    )

    should_use_ai_fallback = (
        state.intent == INTENT_UNKNOWN
        or missing_entities
    )

    # =========================
    # 6) Gemini يدخل فقط لو rules مش كفاية
    # =========================
    if should_use_ai_fallback:
        ai_result = await ai_svc.detect_intent_and_entities(text, current_step=current_step, history=history_str)

        ai_intent = ai_result.get("intent")
        ai_budget = ai_result.get("budget")
        ai_brand = ai_result.get("brand")
        ai_model = ai_result.get("model")
        ai_year = ai_result.get("model_year")
        ai_car_name = ai_result.get("car_name")
        clear_current_step = ai_result.get("clear_current_step", False)
        direct_response = ai_result.get("direct_response")
        
        if clear_current_step and current_step:
            await memory.update_state(state.telegram_user_id, current_step=None)
            current_step = None
            
        if direct_response:
            state.response_text = direct_response
            state.should_stop = True
            return state

        if ai_intent and ai_intent != "unknown":
            state.intent = ai_intent

        if (
            ai_budget
            and not state.extracted_budget
            and current_step not in ["awaiting_booking_customer_info", "awaiting_reschedule_datetime"]
        ):
            state.extracted_budget = ai_budget

        if ai_car_name and not getattr(state, "extracted_car_name", None):
            state.extracted_car_name = ai_car_name

        # تحديث البراند والموديل والسنة من الـ AI
        if ai_brand and not state.brand:
            state.brand = ai_brand
        if ai_model and not state.model:
            state.model = ai_model
        if ai_year and not state.model_year:
            state.model_year = ai_year

        if ai_car_name and not (state.brand or state.model or state.model_year):
            ai_filters = entity_svc.extract_car_filters(ai_car_name)
            state.brand = ai_filters.get("brand")
            state.model = ai_filters.get("model")
            state.model_year = ai_filters.get("model_year")

        if not (
            state.preferred_transmission
            or state.preferred_body_type
            or state.preferred_fuel_type
            or state.wants_reliable
            or state.wants_family_car
            or state.wants_economic
            or state.wants_city_car
        ):
            ai_preferences = entity_svc.extract_preferences(text + " " + (ai_car_name or ""))
            state.preferred_transmission = ai_preferences.get("preferred_transmission")
            state.preferred_body_type = ai_preferences.get("preferred_body_type")
            state.preferred_fuel_type = ai_preferences.get("preferred_fuel_type")
            state.wants_reliable = ai_preferences.get("wants_reliable", False)
            state.wants_family_car = ai_preferences.get("wants_family_car", False)
            state.wants_economic = ai_preferences.get("wants_economic", False)
            state.wants_city_car = ai_preferences.get("wants_city_car", False)

    # =========================
    # 7) دمج السياق السابق لو مفيش بيانات جديدة والنية هي سؤال عن عربية
    # =========================
    if state.intent == INTENT_ASK_SPECIFIC_CAR:
        if not state.brand and not state.model and not state.model_year:
            # لو العميل بيسأل "مواصفاتها" مثلاً ومفيش براند/موديل في الرسالة الحالية
            state.brand = last_brand
            state.model = last_model
            state.model_year = last_year
            state.last_car_id = last_car_id
        elif state.brand == last_brand and not state.model and not state.model_year:
            # لو العميل ذكر الماركة بس بس هو أصلاً بيتكلم عن موديل معين
            state.model = last_model
            state.model_year = last_year
        elif not state.brand and not state.model and state.model_year:
            # لو العميل ذكر السنة بس (مثلاً 2007) وهو بيتكلم عن تويوتا كورولا
            state.brand = last_brand
            state.model = last_model
        elif not state.brand and state.model and not state.model_year:
            # لو العميل ذكر الموديل بس وهو بيتكلم عن ماركة معينة
            state.brand = last_brand

    # =========================
    # 8) حفظ آخر ميزانية
    # =========================
    if state.extracted_budget:
        state.last_budget = state.extracted_budget

    # =========================
    # 8) استخراج التاريخ والوقت للحجز أو تعديل الحجز
    # =========================
    ext_date, ext_time = None, None
    if state.intent in [INTENT_BOOKING_REQUEST, INTENT_RESCHEDULE_BOOKING]:
        now = datetime.now(ZoneInfo("Africa/Cairo"))
        ext_date, ext_time = entity_svc.extract_datetime(text, now)

    if ext_date:
        state.extracted_date = ext_date
    if ext_time:
        state.extracted_time = ext_time

    # التحقق من نية الحجز
    # لو العميل قال "عايز احجز" ومفيش تاريخ/وقت، ده مش معناه unknown
    # المفروض نكمل وworking_hours_check_node هيسأله عن الميعاد
    # بس لو مفيش عربية محددة خالص في السياق، نسأله عن العربية الأول
    if current_step is None and state.intent == INTENT_BOOKING_REQUEST:
        pending_booking = await memory.get_pending_booking(state.telegram_user_id)
        has_car_context = bool(
            state.last_car_id
            or await memory.get_last_car_id(state.telegram_user_id)
            or pending_booking
        )
        # لو مفيش عربية في السياق ومفيش تاريخ ومفيش وقت، يبقى مش عارف يحجز على إيه
        # في الحالة دي نسيبه يكمل لـ create_booking_node اللي هيطلب منه العربية
        # ما نعملوش UNKNOWN خالص عشان ده بيضيع نية الحجز الواضحة

    logger.info(
        "intent_detected",
        extra={
            "extra_data": {
                "telegram_user_id": state.telegram_user_id,
                "intent": state.intent,
                "current_step": current_step,
                "used_ai_fallback": should_use_ai_fallback,
                "budget": getattr(state, "extracted_budget", None),
                "brand": state.brand,
                "model": state.model,
                "model_year": state.model_year,
                "preferred_transmission": state.preferred_transmission,
                "preferred_body_type": state.preferred_body_type,
                "preferred_fuel_type": state.preferred_fuel_type,
                "has_date": getattr(state, "extracted_date", None) is not None,
                "has_time": getattr(state, "extracted_time", None) is not None,
            }
        },
    )

    return state
