# SPYME — System Architecture

## Stack

| Layer | Technology |
|-------|-----------|
| Desktop Agent | Electron + Node.js |
| Mobile App | React Native (Expo) |
| Backend API | FastAPI (Python) |
| Database | PostgreSQL |
| Cache / Realtime | Redis |
| Clip Storage | S3 / Cloudflare R2 |
| Streaming | WebRTC (P2P via signaling server) |
| STUN | Cloudflare / Google |
| TURN | Coturn (self-hosted) |
| Notifications | Firebase FCM + APNs |
| AI Engine | YOLOv8-nano + OpenCV |

---

## System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  Laptop Agent (Electron)          Mobile App (React Native)     │
│                                                                 │
│  Webcam → AI Engine               Live Feed (WebRTC)           │
│  Motion / Person Detection        Alerts / Arm / Disarm        │
│  Cover Mode (wallpaper UI)        Clip Replay                  │
│  Local encrypted storage          Multi-device dashboard       │
│         │                                    │                  │
│         └──────────┬──────────────────────────┘                │
│                    ▼                                            │
│            SPYME Backend (FastAPI)                              │
│                                                                 │
│  /auth  /devices  /events  /clips  /ws/signal                  │
│         │              │               │                        │
│    PostgreSQL        Redis          S3/R2                       │
│  (users,devices,   (sessions,    (video clips,                  │
│   events,clips)    ws state)      thumbnails)                   │
│                                                                 │
│  WebRTC Flow:                                                   │
│  Laptop ──offer──► Signaling Server ──offer──► Mobile          │
│  Laptop ◄──answer── Signaling Server ◄──answer── Mobile        │
│  Laptop ◄──────────── P2P Stream ──────────────► Mobile        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### users
| column | type | notes |
|--------|------|-------|
| id | UUID PK | |
| email | TEXT UNIQUE | |
| password_hash | TEXT | bcrypt |
| created_at | TIMESTAMPTZ | |
| last_login | TIMESTAMPTZ | |

### devices
| column | type | notes |
|--------|------|-------|
| id | UUID PK | |
| user_id | UUID FK→users | |
| name | TEXT | e.g. "Bedroom Laptop" |
| platform | TEXT | windows / macos |
| pairing_token | TEXT | short-lived, hashed |
| is_armed | BOOLEAN | |
| last_seen | TIMESTAMPTZ | |
| battery_pct | INT | |
| storage_free_mb | BIGINT | |
| created_at | TIMESTAMPTZ | |

### events
| column | type | notes |
|--------|------|-------|
| id | UUID PK | |
| device_id | UUID FK→devices | |
| type | TEXT | motion / person |
| confidence | FLOAT | 0.0–1.0 |
| triggered_at | TIMESTAMPTZ | |
| clip_id | UUID FK→clips nullable | |

### clips
| column | type | notes |
|--------|------|-------|
| id | UUID PK | |
| device_id | UUID FK→devices | |
| event_id | UUID FK→events nullable | |
| storage_key | TEXT | S3 object key |
| thumbnail_key | TEXT | |
| duration_sec | INT | |
| size_bytes | BIGINT | |
| created_at | TIMESTAMPTZ | |

### device_status_logs
| column | type | notes |
|--------|------|-------|
| id | UUID PK | |
| device_id | UUID FK→devices | |
| battery_pct | INT | |
| storage_free_mb | BIGINT | |
| is_online | BOOLEAN | |
| recorded_at | TIMESTAMPTZ | |

---

## API Endpoints

### Auth
```
POST /api/v1/auth/register
POST /api/v1/auth/login           → {access_token, refresh_token}
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### Devices
```
GET    /api/v1/devices            → list user's devices
POST   /api/v1/devices            → register new device
GET    /api/v1/devices/{id}       → device detail + status
PATCH  /api/v1/devices/{id}       → update name / arm state
DELETE /api/v1/devices/{id}
POST   /api/v1/devices/{id}/pair  → generate pairing QR token
```

### Events
```
GET  /api/v1/events               → list (filter: device, type, date)
GET  /api/v1/events/{id}
POST /api/v1/events               → laptop posts new event
```

### Clips
```
GET  /api/v1/clips                → list
GET  /api/v1/clips/{id}
GET  /api/v1/clips/{id}/url       → pre-signed S3 URL
POST /api/v1/clips/upload-url     → get pre-signed upload URL
DELETE /api/v1/clips/{id}
```

### WebRTC Signaling (WebSocket)
```
WS /ws/signal/{device_id}        → laptop connects
WS /ws/viewer/{device_id}        → mobile connects
```

### Notifications
```
POST /api/v1/notify/register-token   → save FCM/APNs token
```

---

## WebRTC Connection Flow

```
1. Laptop connects → WS /ws/signal/{device_id}  (authenticated)
2. Mobile connects → WS /ws/viewer/{device_id}  (authenticated)
3. Server pairs them in room

4. Mobile sends  → {type: "request-offer"}
5. Laptop creates RTCPeerConnection
6. Laptop gathers ICE candidates (STUN)
7. Laptop sends  → {type: "offer", sdp: ...}
8. Mobile sends  → {type: "answer", sdp: ...}
9. ICE candidates exchanged via signaling
10. P2P stream established — server no longer in media path

TURN fallback: if P2P fails (strict NAT), relay via Coturn
```

---

## AI Detection Pipeline

```
Webcam frame (30fps)
       │
       ▼
Frame Buffer (ring, 5 frames)
       │
       ▼
Motion Detector (frame diff + threshold)
  → NO motion → discard, continue
  → Motion detected ↓
       │
       ▼
YOLOv8-nano inference (every 3rd frame while motion active)
  → confidence < 0.6 → log motion-only event
  → person detected  → trigger clip recording
       │
       ▼
Clip Recorder: 5s pre-buffer + recording until clear
       │
       ▼
Event written to local DB (SQLite)
       │
       ▼
Upload clip → S3 pre-signed URL
       │
       ▼
POST /api/v1/events → backend
       │
       ▼
Backend → FCM/APNs → Mobile push notification
```

---

## Development Phases

| Phase | Scope | Target |
|-------|-------|--------|
| 1 | Laptop webcam capture + WebRTC stream to mobile | Week 1-2 |
| 2 | Motion + person detection + clip recording | Week 3-4 |
| 3 | Backend auth + device registry + events API | Week 3-4 |
| 4 | Push notifications + mobile alerts + playback | Week 5-6 |
| 5 | Multi-device dashboard + Cover Mode UI | Week 7-8 |
| 6 | AI tuning + offline sync + cloud/local hybrid | Week 9-10 |
| 7 | Polish + security audit + beta | Week 11-12 |

---

## Deployment

```
Backend:     Docker → Railway / Render / AWS ECS
PostgreSQL:  Supabase or RDS
Redis:       Upstash or ElastiCache
S3/Storage:  Cloudflare R2 (cheaper egress)
TURN server: Coturn on small VPS (Hetzner CX21)
Mobile:      Expo EAS Build → App Store / Play Store
Desktop:     Electron Builder → NSIS (Windows) + DMG (macOS)
CI/CD:       GitHub Actions (build + test + deploy)
```
