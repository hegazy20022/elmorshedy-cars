from __future__ import annotations

from typing import Optional, Any, List
from dataclasses import dataclass, field


@dataclass
class AgentState:
    telegram_user_id: str = ""
    customer_id: Optional[int] = None

    raw_input: str = ""
    message_type: str = "text"
    voice_file_id: Optional[str] = None
    normalized_text: str = ""

    mode: str = "AI"
    is_bot_enabled: bool = True
    should_stop: bool = False

    intent: str = ""
    greeted: bool = False
    welcome_text: str = ""

    last_car_id: Optional[int] = None
    last_budget: Optional[float] = None

    brand: Optional[str] = None
    model: Optional[str] = None
    model_year: Optional[int] = None

    extracted_budget: Optional[float] = None
    extracted_car_name: Optional[str] = None
    extracted_date: Optional[Any] = None
    extracted_time: Optional[Any] = None

    preferred_transmission: Optional[str] = None
    preferred_body_type: Optional[str] = None
    preferred_fuel_type: Optional[str] = None
    wants_reliable: bool = False
    wants_family_car: bool = False
    wants_economic: bool = False
    wants_city_car: bool = False

    found_car: Optional[Any] = None
    found_cars: List[Any] = field(default_factory=list)
    car_images: List[str] = field(default_factory=list)
    recommended_cars: List[Any] = field(default_factory=list)
    alternative_cars: List[Any] = field(default_factory=list)
    booking: Optional[Any] = None

    cache_hit: bool = False
    cached_response: Optional[str] = None

    response_text: str = ""
