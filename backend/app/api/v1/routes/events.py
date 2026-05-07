import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.event import Event
from app.schemas.event import EventCreate, EventResponse
from app.services.notify import push
from app.services.sms import send_sms
from app.utils.auth import current_user

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
async def list_events(
    device_id: uuid.UUID | None = None,
    type: str | None = None,
    limit: int = Query(50, le=200),
    user=Depends(current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Event)
    if device_id:
        q = q.where(Event.device_id == device_id)
    if type:
        q = q.where(Event.type == type)
    q = q.order_by(Event.triggered_at.desc()).limit(limit)
    rows = await db.scalars(q)
    return rows.all()


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(body: EventCreate, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    event = Event(
        device_id=body.device_id,
        type=body.type,
        confidence=body.confidence,
        clip_id=body.clip_id,
        event_metadata=body.metadata,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    # Smart push titles per event type
    meta = body.metadata or {}
    titles = {
        "person": "Person detected",
        "multi_person": f"⚠️ {meta.get('people_count', 'Multiple')} people detected",
        "reaching": "Person reaching for something",
        "theft": f"🚨 Possible theft — {meta.get('object', 'object taken')}",
        "fire": "🔥 FIRE EMERGENCY",
        "smoke": "💨 Smoke detected",
        "motion": "Motion detected",
    }

    is_critical = body.type == "fire"
    push_priority = "critical" if is_critical else "high"

    if user.fcm_token and body.type in {"person", "multi_person", "theft", "reaching", "fire", "smoke"}:
        push(
            user.fcm_token,
            title=titles.get(body.type, "SPYME Alert"),
            body=meta.get("summary", f"on {body.device_id}"),
            data={
                "event_id": str(event.id),
                "type": body.type,
                "priority": push_priority,
                "vibrate": "true" if body.type in {"fire", "theft"} else "false",
                "siren": "true" if body.type == "fire" else "false",
            },
        )

    # 🔥 CRITICAL: fire triggers SMS to user phone + emergency contact
    # Safety guards added based on Drawback #3 (fire false positives):
    #   1. SMS is OFF by default for the first 14 days — user must opt in explicitly
    #   2. Confidence threshold of 0.65 — below that, push only (no SMS)
    #   3. Pause SMS during quiet hours UNLESS confidence > 0.85 (strong signal)
    if body.type == "fire":
        from datetime import datetime, timezone, timedelta

        now = datetime.now(timezone.utc)
        confidence = body.confidence or 0
        is_quiet_hours = (user.quiet_hours_start <= now.hour < user.quiet_hours_end)
        sms_allowed = (
            user.fire_sms_enabled
            and user.phone_number
            and confidence >= 0.65
            and (not is_quiet_hours or confidence >= 0.85)
        )

        if sms_allowed:
            sms_body = (
                f"FIRE ALARM - SPYME detected fire at {event.triggered_at.strftime('%H:%M:%S')}. "
                f"Confidence {int(confidence * 100)}%. "
                f"Open app to confirm: spyme://event/{event.id}"
            )
            send_sms(user.phone_number, sms_body)
            if user.emergency_contact:
                send_sms(user.emergency_contact, sms_body)

    return event
