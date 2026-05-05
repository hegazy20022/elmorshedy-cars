from app.core.config import settings


def is_owner_chat(chat_id: int) -> bool:
    return int(chat_id) == int(settings.TELEGRAM_OWNER_CHAT_ID)
