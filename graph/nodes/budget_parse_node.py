from graph.state import AgentState
from services.intent_service import INTENT_RECOMMEND_BY_BUDGET


async def budget_parse_node(state: AgentState, services: dict) -> AgentState:
    if state.intent != INTENT_RECOMMEND_BY_BUDGET or state.should_stop:
        return state

    if not state.extracted_budget:
        state.response_text = "تمام يا فندم تحب تقوللي الميزانية المتاحة مع حضرتك كام"
        state.should_stop = True

    return state
