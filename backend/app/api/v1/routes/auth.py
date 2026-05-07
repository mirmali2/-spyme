from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    is_revoked,
    revoke_refresh,
    verify_password,
)
from app.models.subscription import Subscription
from app.models.user import User
from app.schemas.auth import GoogleAuthRequest, LoginRequest, RegisterRequest, TokenResponse
from app.services.billing import trial_period_end
from app.services.google_oauth import verify_id_token
from app.utils.rate_limit import google_limiter, login_limiter, register_limiter


async def _ensure_subscription(db: AsyncSession, user: User):
    """Auto-grant 2-day trial to new users."""
    existing = await db.scalar(select(Subscription).where(Subscription.user_id == user.id))
    if not existing:
        db.add(Subscription(
            user_id=user.id,
            plan="trial",
            status="active",
            current_period_end=trial_period_end(),
        ))

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    register_limiter(request)
    existing = await db.scalar(select(User).where(User.email == body.email))
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=body.email, password_hash=hash_password(body.password), name=getattr(body, "name", None))
    db.add(user)
    await db.flush()  # get user.id without commit
    await _ensure_subscription(db, user)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    login_limiter(request)
    user = await db.scalar(select(User).where(User.email == body.email))
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/google", response_model=TokenResponse)
async def google_signin(body: GoogleAuthRequest, request: Request, db: AsyncSession = Depends(get_db)):
    google_limiter(request)
    """
    Sign in or register with Google.
    Mobile sends Google's id_token (from expo-auth-session).
    Backend verifies it, finds or creates the user, returns SPYME JWTs.
    """
    profile = verify_id_token(body.id_token, expected_audience=body.client_id)
    if not profile or not profile.get("email_verified"):
        raise HTTPException(401, "Invalid Google token")

    # Find by google_id first, then by email (account linking)
    user = await db.scalar(select(User).where(User.google_id == profile["google_id"]))
    if not user and profile.get("email"):
        user = await db.scalar(select(User).where(User.email == profile["email"]))

    if user:
        # Link Google to existing account if not yet linked
        if not user.google_id:
            user.google_id = profile["google_id"]
        user.name = user.name or profile.get("name")
        user.picture_url = profile.get("picture") or user.picture_url
        if body.refresh_token and body.storage_provider == "google_drive":
            user.google_refresh_token = body.refresh_token
            user.storage_provider = "google_drive"
    else:
        # Brand new user via Google
        user = User(
            email=profile["email"],
            google_id=profile["google_id"],
            name=profile.get("name"),
            picture_url=profile.get("picture"),
            password_hash=None,
            google_refresh_token=body.refresh_token if body.storage_provider == "google_drive" else None,
            storage_provider=body.storage_provider or "spyme_cloud",
        )
        db.add(user)
        await db.flush()
        await _ensure_subscription(db, user)

    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(token: str, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    jti = payload.get("jti", "")
    if jti and is_revoked(jti):
        raise HTTPException(status_code=401, detail="Token revoked")
    import uuid as _uuid
    try:
        uid = _uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = await db.get(User, uid)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # ROTATE — invalidate the used refresh, issue a new pair
    if jti:
        revoke_refresh(jti)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
