import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.models.extras import Zone
from app.utils.auth import current_user

router = APIRouter(prefix="/zones", tags=["zones"])


class ZoneCreate(BaseModel):
    device_id: uuid.UUID
    name: str
    kind: str = "alert"           # alert | ignore
    polygon: list[list[float]]    # [[x,y], ...] normalized 0-1
    priority: int = 1


class ZoneOut(BaseModel):
    id: uuid.UUID
    device_id: uuid.UUID
    name: str
    kind: str
    polygon: list
    priority: int

    model_config = {"from_attributes": True}


async def _owns_device(device_id: uuid.UUID, user_id: uuid.UUID, db: AsyncSession) -> Device:
    d = await db.scalar(select(Device).where(Device.id == device_id, Device.user_id == user_id))
    if not d:
        raise HTTPException(404, "Device not found")
    return d


@router.get("", response_model=list[ZoneOut])
async def list_zones(device_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    await _owns_device(device_id, user.id, db)
    return (await db.scalars(select(Zone).where(Zone.device_id == device_id))).all()


@router.post("", response_model=ZoneOut, status_code=201)
async def create_zone(body: ZoneCreate, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    await _owns_device(body.device_id, user.id, db)
    zone = Zone(**body.model_dump())
    db.add(zone)
    await db.commit()
    await db.refresh(zone)
    return zone


@router.delete("/{zone_id}", status_code=204)
async def delete_zone(zone_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    zone = await db.get(Zone, zone_id)
    if not zone:
        raise HTTPException(404, "Zone not found")
    await _owns_device(zone.device_id, user.id, db)
    await db.delete(zone)
    await db.commit()
