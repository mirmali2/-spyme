from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.utils.auth import current_user

router = APIRouter(prefix="/notify", tags=["notify"])


class TokenRegister(BaseModel):
    fcm_token: str | None = None
    apns_token: str | None = None


class PhoneRegister(BaseModel):
    phone_number: str | None = None
    emergency_contact: str | None = None


@router.post("/register-token")
async def register_token(body: TokenRegister, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    if body.fcm_token:
        user.fcm_token = body.fcm_token
    if body.apns_token:
        user.apns_token = body.apns_token
    await db.commit()
    return {"ok": True}


@router.post("/register-phone")
async def register_phone(body: PhoneRegister, user=Depends(current_user), db: AsyncSession = Depends(get_db)):
    """Register phone number for SMS fire alerts + optional emergency backup contact."""
    if body.phone_number is not None:
        user.phone_number = body.phone_number
    if body.emergency_contact is not None:
        user.emergency_contact = body.emergency_contact
    await db.commit()
    return {"ok": True, "phone": user.phone_number, "emergency": user.emergency_contact}
