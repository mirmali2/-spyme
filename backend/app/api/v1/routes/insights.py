"""Aggregate analytics for the Insights screen."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.models.event import Event
from app.utils.auth import current_user

router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/summary")
async def summary(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    fourteen_days_ago = datetime.now(timezone.utc) - timedelta(days=14)

    # event counts (last 7 vs prev 7) for trend
    devs = (await db.scalars(select(Device.id).where(Device.user_id == user.id))).all()
    if not devs:
        return {"events_7d": 0, "events_prev_7d": 0, "delta_pct": 0, "devices": 0, "armed": 0}

    cur = await db.scalar(select(func.count(Event.id)).where(Event.device_id.in_(devs), Event.triggered_at >= seven_days_ago))
    prev = await db.scalar(select(func.count(Event.id)).where(Event.device_id.in_(devs), Event.triggered_at >= fourteen_days_ago, Event.triggered_at < seven_days_ago))
    armed = await db.scalar(select(func.count(Device.id)).where(Device.user_id == user.id, Device.is_armed.is_(True)))

    delta_pct = 0 if prev == 0 else round((cur - prev) / prev * 100)
    return {
        "events_7d": cur or 0,
        "events_prev_7d": prev or 0,
        "delta_pct": delta_pct,
        "devices": len(devs),
        "armed": armed or 0,
    }


@router.get("/heatmap")
async def heatmap(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Returns 7×24 grid of event counts (Mon=0..Sun=6, hour 0..23)."""
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    devs = (await db.scalars(select(Device.id).where(Device.user_id == user.id))).all()
    if not devs:
        return {"grid": [[0] * 24 for _ in range(7)]}

    rows = (await db.execute(
        select(Event.triggered_at).where(Event.device_id.in_(devs), Event.triggered_at >= seven_days_ago)
    )).all()

    grid = [[0] * 24 for _ in range(7)]
    for (ts,) in rows:
        grid[ts.weekday()][ts.hour] += 1
    return {"grid": grid}
