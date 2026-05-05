from graph.state import AgentState


async def bot_enabled_check_node(state: AgentState, services: dict) -> AgentState:
    bot_ctrl = services["bot_control"]
    state.is_bot_enabled = await bot_ctrl.is_bot_enabled()

    if not state.is_bot_enabled:
        state.response_text = "شكرًا لتواصلك مع معرض المرشدي وسيتم الرد عليك في أقرب وقت"
        state.should_stop = True

    return state
