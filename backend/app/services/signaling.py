"""
WebRTC signaling via WebSocket.
Laptop connects as 'camera', mobile connects as 'viewer'.
Server relays SDP offer/answer and ICE candidates between peers.
No media passes through server — pure signaling only.
"""
import json
from collections import defaultdict

from fastapi import WebSocket

# rooms[device_id] = {"camera": ws | None, "viewer": ws | None}
rooms: dict[str, dict[str, WebSocket | None]] = defaultdict(lambda: {"camera": None, "viewer": None})


async def connect(device_id: str, role: str, ws: WebSocket):
    await ws.accept()
    rooms[device_id][role] = ws
    peer_role = "viewer" if role == "camera" else "camera"
    peer = rooms[device_id][peer_role]
    if peer:
        await peer.send_text(json.dumps({"type": "peer-connected", "role": role}))


async def relay(device_id: str, role: str, ws: WebSocket):
    peer_role = "viewer" if role == "camera" else "camera"
    try:
        while True:
            data = await ws.receive_text()
            peer = rooms[device_id][peer_role]
            if peer:
                await peer.send_text(data)
    except Exception:
        pass
    finally:
        rooms[device_id][role] = None
        peer = rooms[device_id][peer_role]
        if peer:
            await peer.send_text(json.dumps({"type": "peer-disconnected", "role": role}))
