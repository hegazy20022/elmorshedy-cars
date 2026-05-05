from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CacheUpdate(BaseModel):
    cached_answer: Optional[str] = None
    repeat_count: Optional[int] = None
    is_active: Optional[bool] = None


class CacheResponse(BaseModel):
    cache_id: int
    car_id: Optional[int] = None
    intent: str
    raw_question: Optional[str] = None
    normalized_question: Optional[str] = None
    cache_key: str
    repeat_count: int
    cached_answer: Optional[str] = None
    is_active: bool
    expires_at: Optional[str] = None
    last_hit_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
