from graph.state import AgentState
from services.intent_service import INTENT_ASK_SPECIFIC_CAR


async def car_lookup_node(state: AgentState, services: dict) -> AgentState:
    if state.intent != INTENT_ASK_SPECIFIC_CAR or state.should_stop:
        return state

    car_svc = services["car"]
    memory = services["memory"]
    cache_svc = services["cache"]
    ai = services["ai"]
    entity_svc = services["entity"]

    # استكمال بيانات الفلاتر من الرسالة
    extracted_filters = entity_svc.extract_car_filters(state.normalized_text or "")
    if extracted_filters.get("brand") and not state.brand:
        state.brand = extracted_filters["brand"]
    if extracted_filters.get("model") and not state.model:
        state.model = extracted_filters["model"]
    if extracted_filters.get("model_year") and not state.model_year:
        state.model_year = extracted_filters["model_year"]

    # لو المستخدم قال ماركة فقط بدون موديل ولا سنة
    if state.brand and not state.model and not state.model_year:
        state.response_text = ai.get_brand_only_clarification(state.brand)
        await memory.set_pending_car_clarification(
            state.telegram_user_id, state.brand, state.model, state.model_year
        )
        state.should_stop = True
        return state

    cached = await cache_svc.get_cached_response(
        intent=INTENT_ASK_SPECIFIC_CAR,
        raw_question=state.normalized_text,
        brand=state.brand,
        model=state.model,
        model_year=state.model_year,
    )
    if cached:
        state.cache_hit = True
        state.response_text = cached.cached_answer
        

        if cached.car_id:
            state.last_car_id = cached.car_id
            await memory.set_last_car(state.telegram_user_id, cached.car_id)
            
            car = await car_svc.get_car_by_id(cached.car_id)
            if car:
                state.found_car = car
                await memory.update_state(
                    state.telegram_user_id,
                    context_updates={
                        "last_brand": car.brand,
                        "last_model": car.model,
                        "last_model_year": car.model_year,
                    },
                )
        
        state.should_stop = True
        return state

    cars = await car_svc.search_cars(state.brand, state.model, state.model_year)

    if not cars and state.normalized_text:
        cars = await car_svc.search_loose_by_text(state.normalized_text)

    # لو مفيش نفس السنة المطلوبة لكن فيه أقرب سنة لنفس البراند/الموديل
    if not cars and (state.brand or state.model):
        closest_matches = await car_svc.find_closest_year_matches(
            brand=state.brand,
            model=state.model,
            model_year=state.model_year,
            limit=3,
        )

        if closest_matches:
            best_match = closest_matches[0]
            state.found_car = best_match
            state.found_cars = closest_matches

            financing = await car_svc.get_financing_options(best_match.car_id)
            details = await car_svc.format_car_details(best_match, financing)

            intro_parts = []
            if state.brand and state.model and state.model_year:
                intro_parts.append(
                    f"الموديل {state.brand} {state.model} سنة {state.model_year} مش متوفر حاليًا"
                )
            elif state.brand and state.model:
                intro_parts.append(
                    f"{state.brand} {state.model} بالمواصفات المطلوبة مش متوفرة حاليًا"
                )
            else:
                intro_parts.append("العربية المطلوبة بالمواصفات دي مش متوفرة حاليًا")

            intro_parts.append("لكن أقرب متاح عندنا هو")
            intro_text = "\n".join(intro_parts)

            await memory.set_last_car(state.telegram_user_id, best_match.car_id)
            await memory.update_state(
                state.telegram_user_id,
                context_updates={
                    "last_brand": best_match.brand,
                    "last_model": best_match.model,
                    "last_model_year": best_match.model_year,
                },
            )

            state.response_text = f"{intro_text}\n\n{details}"
            state.should_stop = True
            return state

    if not cars:
        state.response_text = ai.get_not_available_message()
        state.should_stop = True
        return state

    if len(cars) > 1 and not state.model and not state.model_year:
        state.response_text = ai.get_multiple_matches_message(cars)
        state.should_stop = True
        return state

    car = cars[0]
    state.found_car = car
    state.found_cars = cars

    financing = await car_svc.get_financing_options(car.car_id)
    state.car_images = await car_svc.get_car_images(car.car_id)
    response = await car_svc.format_car_details(car, financing)

    state.last_car_id = car.car_id
    await memory.set_last_car(state.telegram_user_id, car.car_id)
    await memory.update_state(
        state.telegram_user_id,
        context_updates={
            "last_brand": car.brand,
            "last_model": car.model,
            "last_model_year": car.model_year,
        },
    )

    await cache_svc.increment_or_create(
        intent=INTENT_ASK_SPECIFIC_CAR,
        raw_question=state.normalized_text,
        response_text=response,
        car_id=car.car_id,
        brand=car.brand,
        model=car.model,
        model_year=car.model_year,
    )

    state.response_text = response
    state.should_stop = True
    return state
