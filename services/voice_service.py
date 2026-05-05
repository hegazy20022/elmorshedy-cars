from __future__ import annotations

from typing import Optional


class VoiceService:
    def __init__(self, bot=None):
        self.bot = bot

    async def transcribe_voice(self, file_id: str) -> Optional[str]:
        return None

    async def get_voice_fallback_message(self) -> str:
        return "عذرًا يا فندم مش قادر أفهم الرسالة الصوتية دلوقتي ممكن تكتب طلبك بالنص"
