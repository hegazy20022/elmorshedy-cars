import logging
from sqlalchemy import select

from app.observability.metrics import Metrics
from graph.state import AgentState
from models.business_info import BusinessInfo
from services.intent_service import INTENT_BOOKING_REQUEST

logger = logging.getLogger(__name__)


async def create_booking_node(state: AgentState, services: dict) -> AgentState:
    memory = services["memory"]
    booking_svc = services["booking"]
    customer_svc = services["customer"]
    car_svc = services["car"]
    entity_svc = services["entity"]

    conv_state = await memory.get_state(state.telegram_user_id)
    current_step = conv_state.current_step if conv_state else None
    ctx = conv_state.context or {} if conv_state else {}

    customer, _ = await customer_svc.get_or_create(
        telegram_user_id=state.telegram_user_id,
        full_name=None,
        username=None,
    )

    # =========================
    # استكمال بيانات الحجز
    # =========================
    if current_step == "awaiting_booking_customer_info":
        pending_booking = await memory.get_pending_booking(state.telegram_user_id)

        if not pending_booking:
            await memory.clear_pending_booking(state.telegram_user_id)
            await memory.update_state(state.telegram_user_id, current_step=None)
            return state

        extracted_customer = entity_svc.extract_customer_info(state.normalized_text)
        has_new_data = any([extracted_customer.get("full_name"), extracted_customer.get("phone"), extracted_customer.get("address")])

        # إذا العميل بعت بيانات جديدة، نحدثها
        if has_new_data:
            full_name = extracted_customer.get("full_name") or customer.full_name or ctx.get("customer_name")
            phone = extracted_customer.get("phone") or customer.phone or ctx.get("customer_phone")
            address = extracted_customer.get("address") or customer.address or ctx.get("customer_address")

            await customer_svc.update_customer_info(
                state.telegram_user_id,
                full_name=full_name,
                phone=phone,
                address=address,
            )
            
            await memory.set_customer_info(
                state.telegram_user_id,
                full_name=full_name,
                phone=phone,
                address=address,
            )
        else:
            # لو مبعتش بيانات جديدة بس بعت رسالة تانية (تأكيد مثلاً)، نستخدم المتاح
            full_name = customer.full_name or ctx.get("customer_name") or "عميل تليجرام"
            phone = customer.phone or ctx.get("customer_phone")
            address = customer.address or ctx.get("customer_address")

        # إتمام الحجز بما هو متاح (سواء كمل البيانات أو لأ)
        booking = await booking_svc.create_booking(
            customer_id=customer.customer_id,
            car_id=pending_booking["car_id"],
            booking_date=pending_booking["booking_date"],
            booking_time=pending_booking["booking_time"],
            customer_name=full_name,
            customer_phone=phone,
            customer_address=address,
        )

        car = await car_svc.get_car_by_id(pending_booking["car_id"])
        state.booking = booking
        Metrics.inc_bookings()

        await memory.set_last_booking_info(
            state.telegram_user_id,
            booking_id=booking.booking_id,
            booking_date=booking.booking_date.strftime("%Y/%m/%d"),
            booking_time=booking_svc.format_time_12h(booking.booking_time),
            car_name=car.car_name if car else "العربية",
        )

        await memory.clear_pending_booking(state.telegram_user_id)

        state.response_text = await booking_svc.format_booking_confirmation(
            booking,
            car.car_name if car else "العربية",
        )
        state.should_stop = True
        return state

    # =========================
    # الحجز الطبيعي
    # =========================
    pending_booking = await memory.get_pending_booking(state.telegram_user_id)

    has_booking_context = (
        state.extracted_date is not None
        or state.extracted_time is not None
        or pending_booking is not None
    )

    if state.intent != INTENT_BOOKING_REQUEST or state.should_stop or not has_booking_context:
        return state

    extracted_customer = entity_svc.extract_customer_info(state.normalized_text)

    if (
        extracted_customer.get("full_name")
        or extracted_customer.get("phone")
        or extracted_customer.get("address")
    ):
        await customer_svc.update_customer_info(
            state.telegram_user_id,
            full_name=extracted_customer.get("full_name"),
            phone=extracted_customer.get("phone"),
            address=extracted_customer.get("address"),
        )

        await memory.set_customer_info(
            state.telegram_user_id,
            full_name=extracted_customer.get("full_name"),
            phone=extracted_customer.get("phone"),
            address=extracted_customer.get("address"),
        )

        customer = await customer_svc.get_by_telegram_id(state.telegram_user_id)

    car_id = state.last_car_id or await memory.get_last_car_id(state.telegram_user_id)

    if not car_id:
        state.response_text = "قبل الحجز قوللي حضرتك عايز تعاين أنهي عربية"
        state.should_stop = True
        return state

    car = await car_svc.get_car_by_id(car_id)

    if not car:
        state.response_text = "العربية دي مش موجودة حاليًا"
        state.should_stop = True
        return state

    # التأكد من أن المستخدم أدخل التاريخ والوقت في المحادثة الحالية
    # لا نعتمد على التاريخ والوقت القديم المخزن في الذاكرة بدون سؤال المستخدم
    if not state.extracted_date or not state.extracted_time:
        state.response_text = await booking_svc.get_working_hours_message()
        state.should_stop = True
        return state

    result = await booking_svc.db.execute(
        select(BusinessInfo).where(BusinessInfo.info_key == "booking_settings")
    )
    row = result.scalar_one_or_none()

    if row and isinstance(row.info_value, dict):
        emergency_days = row.info_value.get("emergency_closed_dates", [])
        if str(state.extracted_date) in emergency_days:
            state.response_text = "المعرض مغلق في هذا اليوم بسبب إجازة أو ظرف طارئ"
            state.should_stop = True
            return state

    full_name = customer.full_name
    phone = customer.phone
    address = customer.address

    # التحقق من أن الاسم ليس مجرد حروف تليجرام الافتراضية أو قصيراً جداً
    is_weak_name = False
    if full_name:
        clean_name = full_name.strip()
        # لو الاسم كلمة واحدة أو أقل من 4 حروف نعتبره غير كافي للمعاملات الرسمية
        if len(clean_name) <= 3 or " " not in clean_name:
            is_weak_name = True

    missing_fields = []
    if not full_name or is_weak_name:
        missing_fields.append("الاسم")
    if not phone:
        missing_fields.append("رقم الموبايل")
    if not address:
        missing_fields.append("العنوان")

    if missing_fields:
        # هنا هنسأله مرة واحدة بذوق
        await memory.set_pending_booking(
            state.telegram_user_id,
            {
                "car_id": car_id,
                "booking_date": state.extracted_date,
                "booking_time": state.extracted_time,
            },
        )

        state.response_text = (
            "تمام يا فندم، أنا جهزت الحجز مبدئيًا ✅\n"
            "بس لو ممكن تسيب بياناتك (الاسم، الموبايل، العنوان) عشان نسهل التواصل معاك، اكتبهم هنا.\n"
            "أو لو تحب نأكد بالحالة دي قولي تمام."
        )
        state.should_stop = True
        return state
    
    # لو البيانات أصلاً موجودة، نحجز فوراً
    booking = await booking_svc.create_booking(
        customer_id=customer.customer_id,
        car_id=car_id,
        booking_date=state.extracted_date,
        booking_time=state.extracted_time,
        customer_name=full_name,
        customer_phone=phone,
        customer_address=address,
    )

    state.booking = booking
    Metrics.inc_bookings()

    await memory.set_last_booking_info(
        state.telegram_user_id,
        booking_id=booking.booking_id,
        booking_date=booking.booking_date.strftime("%Y/%m/%d"),
        booking_time=booking_svc.format_time_12h(booking.booking_time),
        car_name=car.car_name if car else "العربية",
    )

    logger.info(
        "booking_created",
        extra={
            "extra_data": {
                "telegram_user_id": state.telegram_user_id,
                "customer_id": customer.customer_id,
                "car_id": car_id,
                "booking_date": str(state.extracted_date),
                "booking_time": str(state.extracted_time),
            }
        },
    )

    state.response_text = await booking_svc.format_booking_confirmation(
        booking,
        car.car_name,
    )
    state.should_stop = True
    return state
