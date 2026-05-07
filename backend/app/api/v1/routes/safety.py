"""User safety controls — opt-in for fire SMS, quiet hours, bedroom mode, consent."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.auth import current_user

router = APIRouter(prefix="/safety", tags=["safety"])


class SafetyUpdate(BaseModel):
    fire_sms_enabled: bool | None = None
    quiet_hours_start: int | None = None  # 0-23
    quiet_hours_end: int | None = None
    bedroom_mode: bool | None = None
    consent_given: bool | None = None


@router.get("/me")
async def get_settings(user=Depends(current_user)):
    return {
        "fire_sms_enabled": user.fire_sms_enabled,
        "fire_sms_opted_in_at": user.fire_sms_opted_in_at,
        "quiet_hours_start": user.quiet_hours_start,
        "quiet_hours_end": user.quiet_hours_end,
        "bedroom_mode": user.bedroom_mode,
        "consent_given": user.consent_given,
    }


@router.patch("/me")
async def update_settings(body: SafetyUpdate, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    if body.fire_sms_enabled is not None:
        user.fire_sms_enabled = body.fire_sms_enabled
        if body.fire_sms_enabled and not user.fire_sms_opted_in_at:
            user.fire_sms_opted_in_at = datetime.now(timezone.utc)
    if body.quiet_hours_start is not None:
        if not (0 <= body.quiet_hours_start <= 23):
            raise HTTPException(400, "Hour must be 0-23")
        user.quiet_hours_start = body.quiet_hours_start
    if body.quiet_hours_end is not None:
        if not (0 <= body.quiet_hours_end <= 23):
            raise HTTPException(400, "Hour must be 0-23")
        user.quiet_hours_end = body.quiet_hours_end
    if body.bedroom_mode is not None:
        user.bedroom_mode = body.bedroom_mode
    if body.consent_given is not None:
        user.consent_given = body.consent_given

    await db.commit()
    return {"ok": True}
