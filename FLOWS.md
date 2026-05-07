# SPYME — User & Operator Flows

How every screen connects, what triggers what, what to do when things break.

---

## A. Happy-path user journey (4 screens)

```
🌐 Website
   ↓ "Get the app"
📱 Login/Sign-up  (#1)
   ↓ Continue with Google
✨ Onboarding pairing  (#18)
   ↓ Enter 7K2-94X code
✅ Armed Success  (#22)
   ↓
📊 Dashboard  (#2)  ← home from now on
```

## B. The 7 critical user-state screens (when something happens)

| # | Screen | Triggered when | Auto-recovery? |
|---|--------|----------------|----------------|
| 19 | Empty state | First launch, no laptop linked yet | n/a — user action required |
| 20 | Offline mode | Phone loses internet | yes — auto-retry every 30s |
| 21 | Permission ask | Critical Alerts not yet granted | yes — re-prompt after 1 dismiss |
| 22 | Armed success | User just armed all devices | n/a — celebratory state |
| 23 | Payment failed | Stripe webhook returns failed | yes — 3-day grace + auto-retry |
| 24 | Support chat | User taps "Get help" anywhere | n/a — founder reply within 1h |
| 25 | Error & recovery | Laptop disconnected for >2 min | yes — every 30s reconnect attempt |

## C. The fire/theft emergency flow (highest stakes)

```
Laptop AI detects fire
       ↓ <1 sec
📡 POST /events {type:fire}
       ↓
[Backend fans out simultaneously]
   ├──→ FCM/APNs critical push  → 📱 Phone vibrates + siren
   ├──→ Twilio SMS               → 📱 Text to user phone
   ├──→ Twilio SMS               → 📱 Text to emergency contact
   └──→ Apple Watch tap          → ⌚ Wrist haptic
       ↓
📱 FireAlertScreen full-screen takeover (#13)
       ├──→ "View live" → LiveView (#3)
       ├──→ "Call 911"  → native dialer
       └──→ "Dismiss false alarm" → silenced for 5 min
       ↓
[User confirms outcome]
   ├──→ "Real fire"   → admin marks confirmed, ML training data
   └──→ "False alarm" → admin reviews, tunes detector for that user
```

## D. Edge cases I handled (subset of the 10,000+ you asked for)

### User edge cases
- ✅ User has no internet → offline mode shows cached data, fire SMS still works
- ✅ User's card declined → 3-day grace, all features stay on, auto-retry
- ✅ User on plane (airplane mode) → fire alerts queue locally, fire when reconnect
- ✅ User has 0 laptops yet → friendly empty state with demo
- ✅ User denied camera permission on laptop → in-app deeplink to System Settings
- ✅ User's laptop went to sleep → auto wake-up packet, error screen with causes
- ✅ User receives fake notification (spoofed) → all push payloads signed with backend HMAC
- ✅ User on iOS without Critical Alerts entitlement → falls back to high-priority push
- ✅ Two users sign up on same email → second signup shows "Already have an account?"
- ✅ User wants to leave SPYME → in-app delete account, wipes all data in 24h
- ✅ User on cheap Android (no FCM) → polling fallback via WebSocket
- ✅ User abroad with different SIM → SMS still routes via Twilio E.164
- ✅ Roommate steals my phone → 2FA via email + remote logout via dashboard
- ✅ User's laptop is stolen → admin "kill switch" wipes credentials remotely
- ✅ Laptop charges/runs hot → adaptive AI: drops to motion-only when over 60°C
- ✅ User wants pets ignored → "Smart filter: ignore animals" toggle uses YOLO class filter
- ✅ User opens 10 viewer tabs → backend rate-limits per-device WebRTC rooms
- ✅ User stops paying mid-fire → emergency stays on through fire (life > revenue)
- ✅ User's WiFi changed → laptop re-pairs automatically via cached refresh token
- ✅ Subscription renewed but user already cancelled → Stripe webhook idempotency check

### Operator/admin edge cases
- ✅ Stripe goes down → fallback grace period + email queue
- ✅ Twilio runs out of credits → fall back to push + email
- ✅ Backend crashes → Render auto-redeploy, push notifications queue in FCM
- ✅ Database fills up → auto-purge events older than user's plan limit
- ✅ Brute-force login attempts → rate-limit + Cloudflare challenge
- ✅ Reviewer wants iOS test account → seeded admin@apple.com / Pass1234! works
- ✅ Bad actor mass-signups → email verification + reCAPTCHA on register
- ✅ DMCA / law enforcement request → in-app legal contact, escrowed metadata only
- ✅ Founder is asleep → admin dashboard mobile-friendly + on-call email queue

---

## E. The 5 paths to support (always reachable)

```
Anywhere in app
       ↓
"?" icon (top-right of every screen)
       ↓
┌──────────────────────────────────────────┐
│  Choose how to reach Mustafa:            │
│                                          │
│  ⚡ Auto-fix this for me  → AI playbook  │
│  💬 Chat with founder    → 1h SLA       │
│  📧 Email                → 24h SLA       │
│  📞 Schedule call        → only Pro+    │
│  🗣 Voice memo           → 4h SLA       │
└──────────────────────────────────────────┘
```

## F. The admin (you) dashboard organization

```
/admin/
   ├─ Overview      — KPI strip + live activity feed
   ├─ Users         — every signup, search, filter, refund
   ├─ Devices       — every laptop online status
   ├─ Live Alerts   — every fire/theft event in real-time
   ├─ Revenue       — MRR chart, Stripe state, dunning
   ├─ System Health — API/DB/Redis/FCM/Twilio/Stripe
   ├─ Support       — open tickets, founder inbox
   ├─ Analytics     — funnel: install → arm → pro
   ├─ Push Console  — manual broadcast to all/segment
   ├─ API Keys      — Twilio/Stripe/Firebase rotation
   ├─ Logs          — last 30 days, searchable
   └─ Configuration — feature flags, AB tests
```

You should spend ≤ 30 min/day in `/admin/`. Everything is automated. Notifications hit your phone for events that need you (failed payment cluster, fire alarm, support ticket).

---

## G. The "smooth UX" checklist (every screen passes these)

1. **Loading state** — skeleton, never blank
2. **Empty state** — encouraging copy, not "no data"
3. **Error state** — explains cause + offers recovery
4. **Success state** — celebratory micro-animation
5. **Permission state** — primes WHY before native prompt
6. **Offline state** — graceful degradation, never broken
7. **Pricing/payment state** — no shock, transparent
8. **Reachable support** — "?" icon top-right always

---

## H. State machine: subscription lifecycle

```
[Sign up]
    ↓
trial · 2 days
    ├──→ Upgrade → monthly|yearly · active
    │       ├──→ Card OK every cycle → stays active
    │       ├──→ Card declined → grace · 3 days
    │       │       ├──→ Card fixed → active
    │       │       └──→ Grace expires → free tier
    │       └──→ User cancels → active until period_end → free tier
    └──→ Trial ends without upgrade → free tier

free tier (forever)
    ├──→ Re-upgrade anytime → monthly|yearly · active
    └──→ Delete account → wiped in 24h
```

## I. State machine: device lifecycle

```
[New laptop]
    ↓
unpaired
    ↓ User enters pairing code
paired · disarmed
    ├──→ User arms → armed
    ├──→ Long offline → presumed_dead
    └──→ User removes → unpaired

armed
    ├──→ Detection event → triggered (records clip)
    ├──→ User disarms → paired · disarmed
    ├──→ Loses connection → armed_offline (events queue locally)
    └──→ Battery <5% → low_power_mode (motion-only AI)

triggered (recording)
    ├──→ Clip uploaded → posts metadata to backend
    └──→ Recording done → back to armed
```
