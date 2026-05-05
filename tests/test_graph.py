import pytest
from graph.builder import AgentGraph
from graph.state import AgentState


class FakeAI:
    async def generate_response(self, state, base_response):
        return base_response

    async def detect_intent_and_entities(self, text, current_step=None):
        return {
            "intent": "unknown",
            "budget": None,
            "car_name": None,
            "clear_current_step": False,
            "direct_response": None
        }

    def get_welcome_message(self):
        return "أهلاً وسهلاً"

    def get_unknown_intent_message(self):
        return "مش فاهم"

    def get_brand_only_clarification(self, brand):
        return f"حددلي موديل {brand}"

    def get_not_available_message(self):
        return "غير متوفرة"

    def get_multiple_matches_message(self, cars):
        return "فيه أكتر من عربية"

    def get_no_cars_found_message(self, budget=None):
        return "مفيش نتائج"


class FakeIntent:
    def classify(self, text):
        return "greeting"

    def extract_budget(self, text):
        return None


class FakeEntity:
    def extract_car_filters(self, text):
        return {"brand": None, "model": None, "model_year": None}

    def extract_preferences(self, text):
        return {
            "preferred_transmission": None,
            "preferred_body_type": None,
            "preferred_fuel_type": None,
            "wants_reliable": False,
            "wants_family_car": False,
            "wants_economic": False,
            "wants_city_car": False,
        }

    def extract_datetime(self, text, now=None):
        return None, None


class FakeMemory:
    async def get_state(self, telegram_user_id):
        return None

    async def get_pending_booking(self, telegram_user_id):
        return None

    async def mark_greeted(self, telegram_user_id):
        return None

    async def get_last_car_id(self, telegram_user_id):
        return None


class FakeBotControl:
    async def is_bot_enabled(self):
        return True


class FakeVoice:
    async def transcribe_voice(self, file_id):
        return None

    async def get_voice_fallback_message(self):
        return "اكتب رسالتك"


@pytest.mark.asyncio
async def test_graph_greeting_flow():
    services = {
        "ai": FakeAI(),
        "intent": FakeIntent(),
        "entity": FakeEntity(),
        "memory": FakeMemory(),
        "bot_control": FakeBotControl(),
        "voice": FakeVoice(),
        "car": None,
        "booking": None,
        "cache": None,
        "chat": None,
        "customer": None,
        "analytics": None,
    }

    graph = AgentGraph(services)
    state = AgentState(
        telegram_user_id="123",
        raw_input="اهلا",
        message_type="text",
    )

    result = await graph.run(state)
    assert result.response_text
    assert "أهلاً" in result.response_text
