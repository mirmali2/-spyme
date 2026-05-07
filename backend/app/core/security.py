from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire, "type": "access"}, settings.JWT_SECRET, settings.JWT_ALGORITHM)


_REVOKED: set[str] = set()  # in-memory revocation; swap to Redis for multi-worker


def create_refresh_token(user_id: UUID) -> str:
    import uuid as _uuid
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": "refresh", "jti": str(_uuid.uuid4())},
        settings.JWT_SECRET, settings.JWT_ALGORITHM,
    )


def revoke_refresh(jti: str) -> None:
    _REVOKED.add(jti)


def is_revoked(jti: str) -> bool:
    return jti in _REVOKED


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return {}
