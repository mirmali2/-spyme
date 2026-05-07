import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)  # null when Google-only
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    picture_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Push & SMS
    fcm_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    apns_token: Mapped[str | None] = mapped_column(String(512), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # Google OAuth
    google_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True, index=True)
    google_refresh_token: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Storage preference: "spyme_cloud" (our S3) | "google_drive" (user's drive) | "local_only"
    storage_provider: Mapped[str] = mapped_column(String(32), default="spyme_cloud", nullable=False)

    # Safety controls
    fire_sms_enabled: Mapped[bool] = mapped_column(default=False)         # off for first 14 days, user must opt-in
    fire_sms_opted_in_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    quiet_hours_start: Mapped[int] = mapped_column(default=1)             # 1 AM
    quiet_hours_end: Mapped[int] = mapped_column(default=6)               # 6 AM
    bedroom_mode: Mapped[bool] = mapped_column(default=False)             # auto-disarm 11pm-7am
    consent_given: Mapped[bool] = mapped_column(default=False)            # "all adults informed"
