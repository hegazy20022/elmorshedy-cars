from decimal import Decimal

from graph.state import AgentState
from services.intent_service import INTENT_RECOMMEND_BY_BUDGET


async def recommendation_node(state: AgentState, services: dict) -> AgentState:
    if state.intent != INTENT_RECOMMEND_BY_BUDGET or state.should_stop:
        return state

    car_svc = services["car"]
    memory = services["memory"]
    ai = services["ai"]

    budget = state.extracted_budget

    if not budget and getattr(state, "last_budget", None):
        budget = state.last_budget

    if not budget:
        budget = await memory.get_last_budget(state.telegram_user_id)

    if not budget:
        state.response_text = "تمام يا فندم تحب تقولي الميزانية المتاحة مع حضرتك كام"
        state.should_stop = True
        return state

    state.extracted_budget = budget
    state.last_budget = budget

    cars = await car_svc.recommend_by_budget_and_preferences(
        budget=Decimal(str(budget)),
        preferred_transmission=state.preferred_transmission,
        preferred_body_type=state.preferred_body_type,
        preferred_fuel_type=state.preferred_fuel_type,
        wants_reliable=state.wants_reliable,
        wants_family_car=state.wants_family_car,
        wants_economic=state.wants_economic,
        wants_city_car=state.wants_city_car,
        limit=5,
    )

    state.recommended_cars = cars

    if not cars:
        state.response_text = ai.get_no_cars_found_message(budget)
        state.should_stop = True
        return state

    lines = [f"فيه شوية اختيارات قريبة من ميزانية {int(budget):,} جنيه"]

    for item in cars:
        car = item["car"]
        reasons = item.get("reasons", [])

        line = f"🚗 {car.car_name}"
        if car.cash_price is not None:
            line += f" - {int(car.cash_price):,} جنيه"

        if reasons:
            line += f"\n✅ {' - '.join(reasons)}"

        lines.append(line)

    lines.append("وعند تشريف حضرتك المعرض إن شاء الله ممكن يكون فيه كلام في السعر")
    lines.append("ولو تحب أحجز لحضرتك معاد للمعاينة")

    state.response_text = "\n".join(lines)

    await memory.set_last_budget(state.telegram_user_id, budget)

    if cars:
        first_car = cars[0]["car"]
        await memory.set_last_car(state.telegram_user_id, first_car.car_id)
        # حفظ بيانات العربية في السياق عشان لو العميل سأل عن تفاصيلها يعرف إحنا بنتكلم عن إيه
        await memory.update_state(
            state.telegram_user_id,
            context_updates={
                "last_brand": first_car.brand,
                "last_model": first_car.model,
                "last_model_year": first_car.model_year,
            }
        )

    state.should_stop = True
    return state
