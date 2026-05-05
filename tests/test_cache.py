import pytest
from services.cache_service import CacheService


@pytest.mark.asyncio
async def test_cache_create_and_get(db_session):
    service = CacheService(db_session)

    entry = await service.increment_or_create(
        intent="ask_specific_car",
        raw_question="تفاصيل تويوتا كورولا 2007",
        response_text="دي تفاصيل العربية",
        car_id=None,
        brand="تويوتا",
        model="كورولا",
        model_year=2007,
    )

    assert entry.cache_id is not None
    assert entry.repeat_count == 1

    await service.increment_or_create(
        intent="ask_specific_car",
        raw_question="تفاصيل تويوتا كورولا 2007؟",
        response_text="دي تفاصيل العربية",
        car_id=None,
        brand="تويوتا",
        model="كورولا",
        model_year=2007,
    )

    result = await service.get_entry(entry.cache_id)
    assert result is not None
    assert result.repeat_count >= 2
