from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes import auth, billing, clips, devices, events, faces, insights, notify, safety, schedules, signal, zones
from app.core.config import settings
from app.core.database import Base, engine
# Import all models so SQLAlchemy registers their metadata
from app.models import user as _user, device as _device, event as _event, clip as _clip, extras as _extras  # noqa
from app.models import subscription as _subscription  # noqa


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title=settings.APP_NAME, version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")
app.include_router(events.router, prefix="/api/v1")
app.include_router(clips.router, prefix="/api/v1")
app.include_router(notify.router, prefix="/api/v1")
app.include_router(zones.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(faces.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(safety.router, prefix="/api/v1")
app.include_router(signal.router)

# Serve static assets
_root = Path(__file__).resolve().parent.parent.parent
for url, folder in [("/preview", "preview"), ("/website", "website"), ("/legal", "legal"), ("/admin", "admin")]:
    p = _root / folder
    if p.exists():
        app.mount(url, StaticFiles(directory=str(p), html=True), name=folder)


@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": "0.1.0", "docs": "/docs", "preview": "/preview"}


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
