import pytest
from models.business_info import BusinessInfo


@pytest.mark.asyncio
async def test_enable_disable_bot(client, db_session):
    row = BusinessInfo(info_key="bot_enabled", info_value={"value": True})
    db_session.add(row)
    await db_session.commit()

    disable_response = await client.post("/control/bot/disable")
    assert disable_response.status_code == 200
    assert disable_response.json()["bot_enabled"] is False

    enable_response = await client.post("/control/bot/enable")
    assert enable_response.status_code == 200
    assert enable_response.json()["bot_enabled"] is True
