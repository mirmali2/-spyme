import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.schemas.device import DeviceCreate, DevicePatch, DeviceResponse, PairingTokenResponse
from app.utils.auth import current_user

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceResponse])
async def list_devices(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(select(Device).where(Device.user_id == user.id))
    return rows.all()


@router.get("/usage")
async def device_usage(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Returns how many devices the user has used out of their plan limit."""
    from sqlalchemy import func as sqlfunc
    from app.models.subscription import Subscription
    from app.services.billing import MAX_DEVICES_GLOBAL, device_limit_for

    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    plan = sub.plan if sub else "free"
    status = sub.status if sub else "active"
    limit = device_limit_for(plan, status)
    count = await db.scalar(select(sqlfunc.count(Device.id)).where(Device.user_id == user.id))
    return {
        "used": count or 0,
        "limit": limit,
        "global_max": MAX_DEVICES_GLOBAL,
        "remaining": max(0, limit - (count or 0)),
        "plan": plan,
        "can_add": (count or 0) < limit,
    }


@router.post("", response_model=DeviceResponse, status_code=201)
async def register_device(body: DeviceCreate, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    # Enforce per-account device cap based on subscription plan
    from sqlalchemy import func as sqlfunc
    from app.models.subscription import Subscription
    from app.services.billing import MAX_DEVICES_GLOBAL, device_limit_for

    sub = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    plan = sub.plan if sub else "free"
    status = sub.status if sub else "active"
    limit = device_limit_for(plan, status)

    count = await db.scalar(
        select(sqlfunc.count(Device.id)).where(Device.user_id == user.id)
    )
    if count >= limit:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "device_limit_reached",
                "message": (
                    f"You've reached the {limit}-device limit on the {plan} plan. "
                    f"Maximum 4 laptops per SPYME account."
                ),
                "current_count": count,
                "limit": limit,
                "global_max": MAX_DEVICES_GLOBAL,
                "upgrade_path": "monthly" if plan == "free" else None,
            },
        )

    device = Device(user_id=user.id, name=body.name, platform=body.platform)
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    device = await _owned(device_id, user.id, db)
    return device


@router.patch("/{device_id}", response_model=DeviceResponse)
async def patch_device(device_id: uuid.UUID, body: DevicePatch, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    device = await _owned(device_id, user.id, db)
    if body.name is not None:
        device.name = body.name
    if body.is_armed is not None:
        device.is_armed = body.is_armed
    if body.battery_pct is not None:
        device.battery_pct = body.battery_pct
    if body.storage_free_mb is not None:
        device.storage_free_mb = body.storage_free_mb
    if body.last_seen is not None:
        device.last_seen = body.last_seen
    await db.commit()
    await db.refresh(device)
    return device


@router.delete("/{device_id}", status_code=204)
async def delete_device(device_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    device = await _owned(device_id, user.id, db)
    await db.delete(device)
    await db.commit()


@router.post("/{device_id}/pair", response_model=PairingTokenResponse)
async def generate_pairing_token(device_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    device = await _owned(device_id, user.id, db)
    raw_token = secrets.token_urlsafe(32)
    device.pairing_token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    device.pairing_token_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    await db.commit()
    return PairingTokenResponse(token=raw_token, expires_in_seconds=600)


async def _owned(device_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Device:
    device = await db.scalar(select(Device).where(Device.id == device_id, Device.user_id == user_id))
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
