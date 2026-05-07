"""Extra models for premium features: zones, schedules, faces, snapshots."""
import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Zone(Base):
    """Detection zone — polygon region drawn on camera feed."""
    __tablename__ = "zones"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), default="alert")  # alert | ignore
    polygon: Mapped[list] = mapped_column(JSON, default=list)       # [[x,y], ...] normalized 0-1
    priority: Mapped[int] = mapped_column(Integer, default=0)       # 0=low, 1=normal, 2=high
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Schedule(Base):
    """Time-based or geofence-based auto arm/disarm."""
    __tablename__ = "schedules"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    kind: Mapped[str] = mapped_column(String(16), default="time")   # time | geofence
    start_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)  # minutes since midnight
    end_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)
    days_of_week: Mapped[int] = mapped_column(Integer, default=0b1111111)     # bitmask Mon-Sun
    geofence_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    geofence_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    geofence_radius_m: Mapped[int | None] = mapped_column(Integer, nullable=True)
    arm_action: Mapped[str] = mapped_column(String(8), default="arm")         # arm | disarm
    device_ids: Mapped[list] = mapped_column(JSON, default=list)              # [] = all
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Face(Base):
    """Known person face library."""
    __tablename__ = "faces"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(32), default="trusted")  # trusted | family | unknown
    embedding: Mapped[list] = mapped_column(JSON, default=list)        # 128-d face embedding
    avatar_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    sightings_count: Mapped[int] = mapped_column(Integer, default=0)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Snapshot(Base):
    """One-tap snapshots from live view."""
    __tablename__ = "snapshots"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    device_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
