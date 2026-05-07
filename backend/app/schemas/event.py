import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventCreate(BaseModel):
    device_id: uuid.UUID
    type: str  # motion | person | multi_person | reaching | theft
    confidence: float | None = None
    clip_id: uuid.UUID | None = None
    metadata: dict[str, Any] | None = Field(default=None, alias="metadata")


class EventResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    type: str
    confidence: float | None
    triggered_at: datetime
    clip_id: uuid.UUID | None
    event_metadata: dict | None = None

    model_config = {"from_attributes": True}
