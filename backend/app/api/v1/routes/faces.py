import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.extras import Face
from app.utils.auth import current_user

router = APIRouter(prefix="/faces", tags=["faces"])


class FaceIn(BaseModel):
    name: str
    label: str = "trusted"     # trusted | family | unknown
    embedding: list[float] = []
    avatar_key: str | None = None


class FaceOut(BaseModel):
    id: uuid.UUID
    name: str
    label: str
    sightings_count: int
    avatar_key: str | None
    model_config = {"from_attributes": True}


@router.get("", response_model=list[FaceOut])
async def list_faces(user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Face).where(Face.user_id == user.id))).all()


@router.post("", response_model=FaceOut, status_code=201)
async def add_face(body: FaceIn, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    face = Face(user_id=user.id, **body.model_dump())
    db.add(face)
    await db.commit()
    await db.refresh(face)
    return face


@router.delete("/{face_id}", status_code=204)
async def delete_face(face_id: uuid.UUID, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    face = await db.get(Face, face_id)
    if not face or face.user_id != user.id:
        raise HTTPException(404, "Face not found")
    await db.delete(face)
    await db.commit()
