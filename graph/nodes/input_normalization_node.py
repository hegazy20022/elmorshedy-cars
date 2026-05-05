from graph.state import AgentState


async def input_normalization_node(state: AgentState, services: dict) -> AgentState:
    voice_svc = services["voice"]

    if state.message_type == "voice" and state.voice_file_id:
        text = await voice_svc.transcribe_voice(state.voice_file_id)
        if not text:
            state.response_text = await voice_svc.get_voice_fallback_message()
            state.should_stop = True
            return state
        state.normalized_text = text.strip()
    else:
        state.normalized_text = (state.raw_input or "").strip()

    return state
