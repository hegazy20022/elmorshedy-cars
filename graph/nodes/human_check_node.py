from graph.state import AgentState


async def human_check_node(state: AgentState, services: dict) -> AgentState:
    memory = services["memory"]

    conv_state = await memory.get_state(state.telegram_user_id)
    if conv_state:
        state.mode = conv_state.mode
        ctx = conv_state.context or {}
        state.greeted = ctx.get("greeted", False)
        state.last_car_id = ctx.get("last_car_id")
        state.last_budget = ctx.get("last_budget")
        state.brand = ctx.get("last_brand")
        state.model = ctx.get("last_model")
        state.model_year = ctx.get("last_model_year")

    if state.mode in ("OWNER", "PAUSED"):
        state.should_stop = True
        state.response_text = ""

    return state
