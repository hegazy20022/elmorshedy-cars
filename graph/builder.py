from graph.state import AgentState

from graph.nodes.input_normalization_node import input_normalization_node
from graph.nodes.bot_enabled_check_node import bot_enabled_check_node
from graph.nodes.human_check_node import human_check_node
from graph.nodes.intent_node import intent_node
from graph.nodes.welcome_node import welcome_node
from graph.nodes.car_lookup_node import car_lookup_node
from graph.nodes.budget_parse_node import budget_parse_node
from graph.nodes.recommendation_node import recommendation_node
from graph.nodes.alternative_suggestion_node import alternative_suggestion_node
from graph.nodes.working_hours_check_node import working_hours_check_node
from graph.nodes.create_booking_node import create_booking_node
from graph.nodes.reschedule_booking_node import reschedule_booking_node
from graph.nodes.booking_followup_node import booking_followup_node
from graph.nodes.response_node import response_node


class AgentGraph:
    def __init__(self, services: dict):
        self.services = services
        self.main_nodes = [
            input_normalization_node,
            bot_enabled_check_node,
            human_check_node,
            intent_node,
            welcome_node,
            car_lookup_node,
            budget_parse_node,
            recommendation_node,
            alternative_suggestion_node,
            working_hours_check_node,
            create_booking_node,
            reschedule_booking_node,
            booking_followup_node,
        ]

    async def run(self, state: AgentState) -> AgentState:
        for node in self.main_nodes:
            state = await node(state, self.services)
            if state.should_stop:
                break

        state = await response_node(state, self.services)
        return state
