from graph.state import AgentState
from services.intent_service import INTENT_BOOKING_REQUEST


async def working_hours_check_node(state: AgentState, services: dict) -> AgentState:
    if state.intent != INTENT_BOOKING_REQUEST or state.should_stop:
        return state

    memory = services["memory"]
    booking_svc = services["booking"]

    conv_state = await memory.get_state(state.telegram_user_id)
    current_step = conv_state.current_step if conv_state else None

    # مهم جدا
    # لو العميل بيكمل بيانات الحجز الاسم والفون والعنوان
    # سيب الرسالة تعدي لـ create_booking_node
    if current_step == "awaiting_booking_customer_info":
        return state

    # لو في أي خطوة خاصة بتعديل المعاد سيبها لنود تعديل المعاد
    if current_step == "awaiting_reschedule_datetime":
        return state

    if not state.extracted_date or not state.extracted_time:
        state.response_text = await booking_svc.get_working_hours_message()
        state.should_stop = True
        return state

    is_valid, reason = await booking_svc.is_within_working_hours(
        state.extracted_date,
        state.extracted_time,
    )

    if not is_valid:
        state.response_text = reason
        state.should_stop = True
        return state

    return state
