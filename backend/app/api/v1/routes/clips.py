"""
Clip metadata endpoints.

We DO NOT store video bytes. We only store:
  - The fact that a clip was recorded (size, duration, event ID)
  - WHERE it lives ('on-device' | 'phone' | 'google_drive' | 'spyme_cloud')
  - For 'google_drive' only: the Drive file_id (NOT the file)

This keeps liability + storage costs at zero, gives users full ownership.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.clip import Clip
from app.utils.auth import current_user

router = APIRouter(prefix="/clips", tags=["clips"])


class ClipMetadata(BaseModel):
    device_id: uuid.UUID
    duration_sec: int | None = None
    size_bytes: int | None = None
    location: str = "on-device"   # on-device | phone | google_drive | spyme_cloud
    drive_file_id: str | None = None  # only for google_drive


class ClipResponse(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    location: str
    duration_sec: int | None
    size_bytes: int | None
    created_at: str
    drive_file_id: str | None


@router.get("", response_model=list[dict])
async def list_clips(device_id: uuid.UUID | None = None, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    q = select(Clip)
    if device_id:
        q = q.where(Clip.device_id == device_id)
    q = q.order_by(Clip.created_at.desc()).limit(100)
    rows = (await db.scalars(q)).all()
    return [
        {
            "id": str(c.id),
            "device_id": str(c.device_id),
            "duration_sec": c.duration_sec,
            "size_bytes": c.size_bytes,
            "location": c.storage_key.split(":", 1)[0] if ":" in c.storage_key else "on-device",
            "drive_file_id": c.storage_key.split(":", 1)[1] if c.storage_key.startswith("google_drive:") else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in rows
    ]


@router.post("", response_model=dict, status_code=201)
async def register_clip_metadata(body: ClipMetadata, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Record THAT a clip exists somewhere. We never receive the file."""
    if body.location == "google_drive" and body.drive_file_id:
        storage_key = f"google_drive:{body.drive_file_id}"
    else:
        storage_key = f"{body.location}:{uuid.uuid4()}"

    clip = Clip(
        device_id=body.device_id,
        storage_key=storage_key,
        duration_sec=body.duration_sec,
        size_bytes=body.size_bytes,
    )
    db.add(clip)
    await db.commit()
    await db.refresh(clip)
    return {"id": str(clip.id), "location": body.location, "stored_on_backend": False}


@router.delete("/{clip_id}", status_code=204)
async def delete_clip_metadata(clip_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Removes only the metadata record. The actual file (if any) stays where the user put it."""
    clip = await db.get(Clip, clip_id)
    if not clip:
        raise HTTPException(404, "Not found")
    await db.delete(clip)
    await db.commit()
