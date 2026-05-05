from graph.state import AgentState
from services.intent_service import INTENT_RESCHEDULE_BOOKING


async def reschedule_booking_node(state: AgentState, services: dict) -> AgentState:
    if state.should_stop:
        return state

    memory = services["memory"]
    booking_svc = services["booking"]
    customer_svc = services["customer"]
    entity_svc = services["entity"]

    conv_state = await memory.get_state(state.telegram_user_id)
    current_step = conv_state.current_step if conv_state else None

    customer = await customer_svc.get_by_telegram_id(state.telegram_user_id)

    # استكمال خطوة تغيير المعاد
    if current_step == "awaiting_reschedule_datetime":
        text = state.normalized_text or state.raw_input or ""
        ext_date, ext_time = entity_svc.extract_datetime(text)

        if not ext_date or not ext_time:
            state.response_text = "تمام يا فندم تحب تغير المعاد ليوم إيه والساعة كام"
            state.should_stop = True
            return state

        is_valid, reason = await booking_svc.is_within_working_hours(ext_date, ext_time)
        if not is_valid:
            state.response_text = reason
            state.should_stop = True
            return state

        last_booking = await memory.get_last_booking_info(state.telegram_user_id)
        booking_id = last_booking.get("booking_id")

        if not booking_id:
            state.response_text = "معلش يا فندم مش لاقي حجز محفوظ عشان أغير معاده"
            state.should_stop = True
            return state

        booking = await booking_svc.reschedule_booking(
            booking_id=booking_id,
            booking_date=ext_date,
            booking_time=ext_time,
        )
        if not booking:
            state.response_text = "معلش يا فندم حصل مشكلة وأنا بغير المعاد"
            state.should_stop = True
            return state

        await memory.update_state(
            state.telegram_user_id,
            current_step=None,
        )

        await memory.set_last_booking_info(
            state.telegram_user_id,
            booking_id=booking.booking_id,
            booking_date=booking.booking_date.strftime("%Y/%m/%d"),
            booking_time=booking_svc.format_time_12h(booking.booking_time),
        )

        state.response_text = (
            f"تم تعديل معاد الحجز بنجاح ✅\n"
            f"📅 المعاد الجديد يوم {booking.booking_date.strftime('%Y/%m/%d')}\n"
            f"⏰ الساعة {booking_svc.format_time_12h(booking.booking_time)}\n"
            f"مستنينك تنورنا"
        )
        state.should_stop = True
        return state

    # بداية طلب تغيير الحجز
    if state.intent != INTENT_RESCHEDULE_BOOKING:
        return state

    if not customer:
        state.response_text = "معلش يا فندم مش لاقي بيانات حضرتك الحالية"
        state.should_stop = True
        return state

    latest_booking = await booking_svc.get_latest_booking_for_customer(customer.customer_id)
    if not latest_booking:
        state.response_text = "معلش يا فندم مش لاقي حجز سابق عشان أغير معاده"
        state.should_stop = True
        return state

    # إذا كانت الرسالة الأولى تحتوي بالفعل على التاريخ والوقت الجديد (رسالة مركبة)
    if state.extracted_date and state.extracted_time:
        is_valid, reason = await booking_svc.is_within_working_hours(state.extracted_date, state.extracted_time)
        if is_valid:
            booking = await booking_svc.reschedule_booking(
                booking_id=latest_booking.booking_id,
                booking_date=state.extracted_date,
                booking_time=state.extracted_time,
            )
            if booking:
                await memory.update_state(
                    state.telegram_user_id,
                    current_step=None,
                )
                await memory.set_last_booking_info(
                    state.telegram_user_id,
                    booking_id=booking.booking_id,
                    booking_date=booking.booking_date.strftime("%Y/%m/%d"),
                    booking_time=booking_svc.format_time_12h(booking.booking_time),
                )
                state.response_text = (
                    f"تمام يا فندم، تم تعديل معاد الحجز بنجاح ✅\n"
                    f"📅 المعاد الجديد يوم {booking.booking_date.strftime('%Y/%m/%d')}\n"
                    f"⏰ الساعة {booking_svc.format_time_12h(booking.booking_time)}\n"
                    f"مستنينك تنورنا"
                )
                state.should_stop = True
                return state

    await memory.set_last_booking_info(
        state.telegram_user_id,
        booking_id=latest_booking.booking_id,
        booking_date=latest_booking.booking_date.strftime("%Y/%m/%d"),
        booking_time=booking_svc.format_time_12h(latest_booking.booking_time),
    )

    await memory.update_state(
        state.telegram_user_id,
        current_step="awaiting_reschedule_datetime",
    )

    state.response_text = (
        f"تمام يا فندم\n"
        f"معاد حضرتك الحالي يوم {latest_booking.booking_date.strftime('%Y/%m/%d')} "
        f"الساعة {booking_svc.format_time_12h(latest_booking.booking_time)}\n"
        f"تحب تغيره ليوم إيه والساعة كام"
    )
    state.should_stop = True
    return state
