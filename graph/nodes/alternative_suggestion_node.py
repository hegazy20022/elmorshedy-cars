from graph.state import AgentState
from services.intent_service import INTENT_SUGGEST_ALTERNATIVES


async def alternative_suggestion_node(state: AgentState, services: dict) -> AgentState:
    if state.intent != INTENT_SUGGEST_ALTERNATIVES or state.should_stop:
        return state

    car_svc = services["car"]
    memory = services["memory"]

    ref_car_id = state.last_car_id or await memory.get_last_car_id(state.telegram_user_id)
    if not ref_car_id:
        state.response_text = "قوللي حضرتك العربية اللي كنت بتسأل عنها وأنا أرشحلك بدائل قريبة"
        state.should_stop = True
        return state

    ref_car = await car_svc.get_car_by_id(ref_car_id)
    if not ref_car:
        state.response_text = "معلش مش قادر أوصل للعربية المرجعية دلوقتي"
        state.should_stop = True
        return state

    alternatives = await car_svc.get_alternatives(ref_car)
    state.alternative_cars = alternatives

    if not alternatives:
        state.response_text = "حاليًا مفيش بدائل قريبة متاحة لكن ممكن تتوفر قريب إن شاء الله تابع صفحة المعرض"
        state.should_stop = True
        return state

    lines = ["البدائل القريبة من السعر ده"]
    for car in alternatives:
        line = f"🚗 {car.car_name}"
        if car.cash_price is not None:
            line += f" - {int(car.cash_price):,} جنيه"
        lines.append(line)

    state.response_text = "\n".join(lines)
    state.should_stop = True
    return state
