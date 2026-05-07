import uuid
from datetime import datetime

from pydantic import BaseModel


class DeviceCreate(BaseModel):
    name: str
    platform: str


class DevicePatch(BaseModel):
    name: str | None = None
    is_armed: bool | None = None
    battery_pct: int | None = None
    storage_free_mb: int | None = None
    last_seen: datetime | None = None


class DeviceResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    platform: str
    is_armed: bool
    last_seen: datetime | None
    battery_pct: int | None
    storage_free_mb: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PairingTokenResponse(BaseModel):
    token: str
    expires_in_seconds: int
