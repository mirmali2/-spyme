import uuid
from datetime import datetime

from pydantic import BaseModel


class ClipCreate(BaseModel):
    device_id: uuid.UUID
    storage_key: str
    thumbnail_key: str | None = None
    duration_sec: int | None = None
    size_bytes: int | None = None


class ClipResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    storage_key: str
    thumbnail_key: str | None
    duration_sec: int | None
    size_bytes: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UploadUrlRequest(BaseModel):
    device_id: uuid.UUID
    filename: str


class UploadUrlResponse(BaseModel):
    upload_url: str
    storage_key: str
