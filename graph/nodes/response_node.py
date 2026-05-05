from graph.state import AgentState


async def response_node(state: AgentState, services: dict) -> AgentState:
    ai = services["ai"]

    base_response = state.response_text or ai.get_unknown_intent_message()

    if state.welcome_text:
        base_response = f"{state.welcome_text}\n\n{base_response}"

    final_response = await ai.generate_response(
        state=state,
        base_response=base_response,
    )

    state.response_text = final_response
    return state
