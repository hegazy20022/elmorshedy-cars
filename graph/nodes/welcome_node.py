from graph.state import AgentState
from services.intent_service import INTENT_GREETING


async def welcome_node(state: AgentState, services: dict) -> AgentState:
    ai = services["ai"]

    if state.intent == INTENT_GREETING:
        state.response_text = ai.get_welcome_message()
        state.should_stop = True
        return state

    return state
