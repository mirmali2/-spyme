import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.extras import Schedule
from app.utils.auth import current_user

router = APIRouter(prefix="/schedules", tags=["schedules"])


class ScheduleIn(BaseModel):
    name: str
    enabled: bool = True
    kind: str = "time"
    start_minute: int | None = None
    end_minute: int | None = None
    days_of_week: int = 0b1111111
    geofence_lat: float | None = None
    geofence_lng: float | None = None
    geofence_radius_m: int | None = None
    arm_action: str = "arm"
    device_ids: list[str] = []


class ScheduleOut(ScheduleIn):
    id: uuid.UUID
    model_config = {"from_attributes": True}


@router.get("", response_model=list[ScheduleOut])
async def list_schedules(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Schedule).where(Schedule.user_id == user.id))).all()


@router.post("", response_model=ScheduleOut, status_code=201)
async def create_schedule(body: ScheduleIn, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    sched = Schedule(user_id=user.id, **body.model_dump())
    db.add(sched)
    await db.commit()
    await db.refresh(sched)
    return sched


@router.patch("/{schedule_id}", response_model=ScheduleOut)
async def patch_schedule(schedule_id: uuid.UUID, body: ScheduleIn, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    sched = await db.get(Schedule, schedule_id)
    if not sched or sched.user_id != user.id:
        raise HTTPException(404, "Schedule not found")
    for k, v in body.model_dump().items():
        setattr(sched, k, v)
    await db.commit()
    await db.refresh(sched)
    return sched


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(schedule_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    sched = await db.get(Schedule, schedule_id)
    if not sched or sched.user_id != user.id:
        raise HTTPException(404, "Schedule not found")
    await db.delete(sched)
    await db.commit()
