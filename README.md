# SPYME

Personal AI security system. Laptop = smart camera. Phone = remote control.

## Structure

```
SPYME/
├── backend/     FastAPI — auth, devices, events, clips, push, WebRTC signaling
├── desktop/    Electron — webcam, AI detection (YOLOv8), recording, streaming, Cover Mode
├── mobile/     React Native (Expo) — live view, alerts, dashboard, pairing
├── infra/      Docker Compose, Nginx, Coturn TURN server
└── ARCHITECTURE.md
```

## Run (Windows)

Open three terminals:

```cmd
run-backend.bat       :: starts FastAPI on :8000 (SQLite, no setup)
run-desktop.bat       :: launches Electron camera app
run-mobile.bat        :: starts Expo dev server, scan QR with Expo Go
```

The backend auto-creates `spyme_dev.db` on first launch.

## Phase Status

- [x] **Phase 1** — Webcam capture (ffmpeg) + WebRTC stream to mobile (`wrtc` ↔ `react-native-webrtc`)
- [x] **Phase 2** — Motion detection + YOLOv8-nano person detection + ring-buffer clip recording
- [x] **Phase 3** — Auth (JWT + refresh), device registry, events API, S3/R2 pre-signed clip uploads
- [x] **Phase 4** — Multi-device dashboard, pairing tokens, heartbeat (battery/storage/online)
- [x] **Phase 5** — Cover Mode (full-screen wallpaper with monitoring indicator), tray, polish
- [x] **Phase 6** — Push notifications (FCM/APNs token registration)
- [x] **Phase 7** — Alembic migrations, Docker Compose, Nginx, Coturn TURN

## Production Deploy

```bash
cd infra/docker && docker compose up -d
# Then point Nginx (infra/nginx/spyme.conf) at api.spyme.app with Let's Encrypt
```

Mobile builds:
```bash
cd mobile && npx eas build --platform ios     # or android
```

Desktop builds:
```bash
cd desktop && npm run build:win    # NSIS installer
cd desktop && npm run build:mac    # DMG
```

## Privacy & Safety

- Camera access requires OS permission (system prompt on first run)
- Cover Mode shows persistent "SPYME monitoring" indicator — never hidden
- No audio capture by default
- All clips encrypted in transit (TLS) + at rest (S3 SSE)
- JWT access tokens expire in 30 min, refresh tokens 30 days
- WebRTC streams are P2P — server only relays signaling, never media
