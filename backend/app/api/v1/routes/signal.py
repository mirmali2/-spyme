import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.models.device import Device
from app.services.signaling import connect, relay

router = APIRouter(tags=["webrtc"])


async def _authorize_ws(ws: WebSocket, device_id: str) -> bool:
    """
    Validate that the JWT in the query string belongs to a user who OWNS this device.
    Closes the socket if not authorized. Prevents random people from joining
    other users' WebRTC rooms.
    """
    token = ws.query_params.get("token", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return False
    try:
        user_id = uuid.UUID(payload["sub"])
        dev_uuid = uuid.UUID(device_id)
    except Exception:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return False

    async with AsyncSessionLocal() as db:
        device = await db.scalar(select(Device).where(Device.id == dev_uuid))
        if not device or device.user_id != user_id:
            await ws.close(code=status.WS_1008_POLICY_VIOLATION)
            return False
    return True


@router.websocket("/ws/signal/{device_id}")
async def camera_ws(device_id: str, ws: WebSocket):
    if not await _authorize_ws(ws, device_id):
        return
    await connect(device_id, "camera", ws)
    try:
        await relay(device_id, "camera", ws)
    except WebSocketDisconnect:
        pass


@router.websocket("/ws/viewer/{device_id}")
async def viewer_ws(device_id: str, ws: WebSocket):
    if not await _authorize_ws(ws, device_id):
        return
    await connect(device_id, "viewer", ws)
    try:
        await relay(device_id, "viewer", ws)
    except WebSocketDisconnect:
        pass
