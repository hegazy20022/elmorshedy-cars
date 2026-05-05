import pytest
from services.intent_service import IntentService
from services.entity_service import EntityService


def test_intent_service_extract_budget():
    service = IntentService()
    result = service.extract_budget("معايا 300 ألف")
    assert result is not None
    assert int(result) == 300000


def test_entity_service_extract_car_filters():
    service = EntityService()
    result = service.extract_car_filters("عايز تفاصيل تويوتا كورولا 2007")
    assert result["brand"] == "تويوتا"
    assert result["model"] == "كورولا"
    assert result["model_year"] == 2007


def test_entity_service_extract_preferences():
    service = EntityService()
    result = service.extract_preferences("عايز عربية اعتمادية واقتصادية أوتوماتيك")
    assert result["wants_reliable"] is True
    assert result["wants_economic"] is True
    assert result["preferred_transmission"] == "automatic"
