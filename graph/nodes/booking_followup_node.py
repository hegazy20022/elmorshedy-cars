from graph.state import AgentState
from services.intent_service import INTENT_THANKS, INTENT_CONFIRM_BOOKING


async def booking_followup_node(state: AgentState, services: dict) -> AgentState:
    if state.should_stop:
        return state

    memory = services["memory"]
    customer_svc = services["customer"]

    if state.intent not in [INTENT_THANKS, INTENT_CONFIRM_BOOKING]:
        return state

    last_booking = await memory.get_last_booking_info(state.telegram_user_id)
    customer_obj = await customer_svc.get_by_telegram_id(state.telegram_user_id)

    if not last_booking.get("booking_date") or not last_booking.get("booking_time"):
        if state.intent == INTENT_THANKS:
            state.response_text = "العفو يا فندم تحت أمرك في أي وقت"
        else:
            state.response_text = "تمام يا فندم تحت أمرك"
        state.should_stop = True
        return state

    customer_name = customer_obj.full_name if customer_obj and customer_obj.full_name else "يا فندم"
    car_name = last_booking.get("car_name") or "العربية"
    booking_date = last_booking.get("booking_date")
    booking_time = last_booking.get("booking_time")

    if state.intent == INTENT_THANKS:
        state.response_text = (
            f"العفو {customer_name} 🌷\n"
            f"معاد حجز معاينة {car_name} confirmed\n"
            f"📅 يوم {booking_date}\n"
            f"⏰ الساعة {booking_time}\n"
            f"مستنين حضرتك تنورنا"
        )
        state.should_stop = True
        return state

    if state.intent == INTENT_CONFIRM_BOOKING:
        state.response_text = (
            f"تمام {customer_name} ✅\n"
            f"معاد حضرتك مؤكد\n"
            f"🚗 {car_name}\n"
            f"📅 يوم {booking_date}\n"
            f"⏰ الساعة {booking_time}\n"
            f"مستنينك تنورنا في المعرض"
        )
        state.should_stop = True
        return state

    return state
