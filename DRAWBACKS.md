# SPYME — Honest Drawbacks Audit

Ranked by **probability × severity**. Read this BEFORE you spend $124 on store fees.

---

## 🔴 CATEGORY 1 — Could kill the business

### 1. Apple/Google may reject the app as "stalkerware"

**The problem:** Both stores have explicit policies banning apps that record people without consent. Your value proposition — "watch your roommate's room while they're not looking" — is exactly what Apple Guideline 4.5.4 and Google Play's Stalkerware Policy ban.

- **Manything**, an app with the *exact same idea*, was acquired and shut down by Sony in 2018 partly because of these policies tightening.
- Apple has rejected dozens of similar apps. Even ones with consent banners.
- Google Play Protect actively scans devices and removes stalkerware.

**What to do:**
- Reposition copy from "watch roommates" to "monitor my own space when I'm away"
- Make the on-device "MONITORING ACTIVE" indicator unhideable (already done — keep it!)
- Add a forced consent flow on first arming: "All adults in this space have been informed"
- Consider B2B-only pivot to Airbnb hosts where consent is clearer

---

### 2. Webcams are physically bad cameras

**The problem:** Your hardware advantage ("laptop is already a camera") is also your ceiling.

- **No IR/night vision** — useless in a dark room. Most break-ins, theft attempts, and gas leaks happen at night.
- **Lid must be open** — most people close their laptops. Closed = no camera = no monitoring.
- **Privacy shutter** — Lenovo, HP, Dell ship laptops with a physical webcam cover. Users will think it's a feature.
- **Fixed angle ~70°** — vs 120°+ on a $30 Wyze cam.
- **Battery 4-8 hours** — not 24/7. Plugged-in = fan noise + heat + electricity bill.
- **Stolen laptops disappear** — bolted CCTVs don't.

**What to do:**
- Tell the truth in marketing: "daytime + plugged-in monitoring" not "24/7 surveillance"
- Add an "old laptop sentinel mode" — cheap thing for laptops users were going to throw away
- Partner with USB IR cameras ($25 add-on) for night vision

---

### 3. Fire detection has massive false-positive surface

**The problem:** HSV color + flicker is fooled by:

- **Sunset light** through a window (orange/red, flickering as clouds pass)
- **Candles, fireplaces, gas stove**
- **TV scenes with fire** (movies, news, video games)
- **Christmas lights, lava lamps, neon signs**
- **A glass of orange juice in afternoon sun**
- **Disco/RGB gaming lights**

If you fire a SMS-with-siren at 3 AM because the user's TV showed a Marvel explosion, **you'll lose that user forever** AND probably get their angry tweet in your face.

**What to do:**
- Add a 30-second confirmation window before firing the SMS
- Train an ACTUAL fire-classifier model on FireNet dataset (free, 1k images, runs in 1 hour on Colab)
- Default fire alerts to PUSH ONLY for first 14 days; only enable SMS+siren after user explicitly opts in
- Show the user the fire detection clip BEFORE firing the alert: "This looks like fire — confirm or dismiss in 10s"

---

### 4. Theft detection is much weaker than the marketing implies

**The problem:** "Object disappeared while a person was nearby" sounds great but:

- It only works on objects YOLO recognizes (80 classes). It won't notice your wedding ring, your watch, your mail, jewelry, cash.
- The object must be CONFIRMED for 30 frames in the baseline. So a freshly-arrived item being stolen = no alert.
- Anything that gets occluded (someone walks in front, a curtain blows) → false "missing"
- Person ID swaps when people cross paths → "Person #2 took your laptop" might name the wrong person
- Moving the object yourself triggers the alert (you pick up your own phone → "theft event" fires to you)

**What to do:**
- Rebrand "theft detection" → "unusual activity" — lower expectation
- Show context clip with the alert ("here's what we saw"); user confirms or dismisses
- Use detected person + confidence as supporting evidence, never primary cause

---

### 5. App Store rev share + "no card to start" trial conflict

**The problem:** Apple takes 30% (15% small business). Google takes 15-30%. Stripe takes 2.9%+$0.30.

| You charge | Apple keeps | You keep | After Stripe (web) |
|-----------|------------|----------|--------------------|
| $5/mo monthly | $1.50 | $3.50 | $4.55 |
| $50/yr yearly | $15 | $35 | $48.20 |

To start a trial with no card on iOS, you have to use Apple's StoreKit subscription, which means you can't use Stripe at all on iOS. You give up 30% **and** the user can refund any time with no friction.

**What to do:**
- Mobile = Apple/Google billing (must)
- Web/desktop signup = Stripe (better margin, can verify card before trial)
- Push power users to web signup with a discount: "Sign up on web, save 20%" — direct $5 → you keep $4.55 vs $3.50

---

## 🟠 CATEGORY 2 — Will hurt growth severely

### 6. Solo founder + no traction = YC + investor hard NO

You said you're a solo CS Master's student. YC funds <2% of solo founders. Investors want a co-founder.

**Fix:** Find a non-CS co-founder at IIT Chicago this semester — design, sales, ops. Even a 10% equity partner improves your odds 5×.

---

### 7. Critical Alert entitlement is rarely granted by Apple

Your fire alarm (the killer feature) needs Apple's `com.apple.developer.usernotifications.critical-alerts` entitlement. Apple grants it sparingly — usually only to medical/safety apps with regulatory backing.

**Fix:** Apply for it on Day 1 (it takes 4-8 weeks). Have a fallback path: high-priority push without bypass-mute, plus SMS, plus phone call ringtone.

---

### 8. The 60-second install is a lie

Real flow:
1. Mobile app install — 60s ✓
2. Sign up + verify email — 60s
3. Install desktop app — 90s (download + extract + permission popups)
4. macOS notarization warning — 30s (user clicks "Open Anyway")
5. Camera permission popup — 20s
6. WebRTC pairing on flaky dorm Wi-Fi — **2-15 min**, sometimes fails entirely
7. Position laptop, frame the room — 60s

= **5-20 minutes realistic**. People give up.

**Fix:** Bluetooth pairing fallback. Local-network discovery via mDNS. NEVER block install on WebRTC working — start with cached/relayed video and upgrade to P2P later.

---

### 9. Cold-start problem on Render free tier

Free hosting sleeps after 15 min idle. Your first user of the morning waits 10-30 seconds for the server to wake up. Push notifications might miss the window.

**Fix:** $7/month Render Starter plan (or use Fly.io which doesn't sleep). Or self-host on a $4 Hetzner VPS.

---

### 10. WebRTC fails on 20-30% of networks

College dorm Wi-Fi, hotel Wi-Fi, corporate networks, double-NAT routers — all block UDP for WebRTC. Without a TURN server, your live stream breaks for those users.

Coturn TURN servers cost $5-30/month + bandwidth ($0.10/GB). At 1k users with 5 min of streaming/day, your TURN bill is $50-200/month.

**Fix:** Use Cloudflare's TURN service — generous free tier. Or accept that some users will see "live stream unavailable" and need to be educated.

---

### 11. Free tier is too generous → no one upgrades

1 camera + 24h history is plenty for the lonely roommate use case. People will stay free forever.

Industry conversion benchmarks for freemium consumer apps: **2-5% to paid**. You projected 23%. That's optimistic by a factor of 5-10×.

**Fix:**
- Free tier: 1 camera, **6 hours** history, motion only (no person/theft AI)
- Make the AI features the upgrade incentive

---

## 🟡 CATEGORY 3 — Quality/UX problems

### 12. False alarm fatigue

A security app that fires too many alerts trains users to ignore them. After the 5th false person-detection alert at 3 AM, they mute notifications. Now your fire alarm doesn't fire either.

**Fix:**
- Per-user adaptive thresholds — learn what's "normal" in their feed
- Quiet hours by default (1 AM - 6 AM, push silently)
- Alert deduplication — don't fire 10 person alerts in 10 minutes

### 13. ID swap on multi-person tracking

When two people cross paths in frame, ByteTrack frequently swaps their IDs. So "Person #2 took your laptop" might actually be Person #3 — wrong evidence in court / wrong roommate accused.

**Fix:** Show a clip in the alert. Don't accuse anyone — "unknown person" until user labels.

### 14. Camera permission revokes when Mac locks

On macOS, when the user locks their Mac, camera permission for background apps gets revoked on next unlock. Until they manually re-allow it, monitoring is dead.

**Fix:** Use a system-level launch agent + camera helper that auto re-requests; or persist via a menu bar daemon.

### 15. Closed lid = dead camera

Most people close their laptops when leaving home — the universal "I'm done with this" gesture. SPYME stops working. They don't realize.

**Fix:** Big banner on disarm: "REMINDER: leave the lid OPEN for monitoring to work". Include a stand recommendation in onboarding.

### 16. Closed-lid-with-external-monitor on macOS = camera off

Closing the lid while keeping the Mac awake (external monitor mode) physically blocks the camera.

**Fix:** Detect lid state. Show banner.

### 17. Audio not recorded — but laptops have mics

Even though you don't record audio, the moment a security researcher reverse-engineers SPYME and shows the binary has microphone code paths (just not used), there will be a Twitter/Reddit storm.

**Fix:** Hard-disable microphone access at the OS permission level. Never even ask for mic permission. Document this on a security page.

### 18. Network egress costs at scale

Each user uploading a 30MB clip per event × 1k events/day × 1k users = 30GB/day = $9/day on AWS, $3/day on R2. With your $5/month price, that's 60% of revenue gone — IF you store clips. (Good thing you don't!)

But wait — your "send clips P2P over WebRTC data channel" still uses laptop upload bandwidth. ISPs in some countries charge for upload. Some users will hit data caps. Some hotels charge per GB.

**Fix:** Make P2P clip transfer opt-in. Default to local-only. User can toggle "send to phone too" per camera.

---

## 🟣 CATEGORY 4 — Scaling/Architecture

### 19. SQLite won't survive past 100 concurrent users

Single-writer, file-based, no replication. Your dev DB is fine; production needs Postgres on day 1.

**Fix:** Migrate to Supabase free tier (500MB Postgres). 2-hour switch.

### 20. WebSocket signaling has no auth

Right now any device_id can join any room — `/ws/signal/{device_id}`. A bad actor could probe device IDs and intercept stream offers.

**Fix:** Validate JWT on WebSocket upgrade; reject if user doesn't own the device_id.

### 21. No rate limiting on auth endpoints

`/api/v1/auth/login` will get brute-forced.

**Fix:** Add `slowapi` middleware → 5 attempts per 15 min per IP.

### 22. JWT refresh tokens never rotate

Stolen refresh token = forever access.

**Fix:** Rotate refresh on every use. Mark old as revoked.

### 23. Stripe webhook idempotency missing

If Stripe retries a webhook (they do), you might double-credit a subscription.

**Fix:** Store `stripe_event_id` on subscription updates; ignore duplicates.

### 24. No backups configured

If your DB corrupts, you've lost every user.

**Fix:** Daily Postgres dump → S3. Free with `pg_dump` + cron.

### 25. No observability

When something breaks at 3 AM, you'll find out from an angry tweet.

**Fix:** Sentry free tier for errors + UptimeRobot free tier for /health pings.

---

## 🟢 CATEGORY 5 — Business/Legal landmines

### 26. State surveillance laws

- **California, Florida, Illinois, Maryland, Massachusetts, Montana, New Hampshire, Pennsylvania, Washington** — two-party consent for audio. Even though you don't record audio, fire-detection ML models running on a microphone-bearing device is enough for some prosecutors.
- **GDPR** in EU — recording anyone in your apartment without their knowledge could expose you (the user) AND you (SPYME the company) to fines.
- **India DPDPA** (just enforced 2025) — biometric data (face recognition) requires explicit consent.

**Fix:** Geo-fence features. Disable theft + multi-person AI in 2-party-consent states by default. Show a state-specific consent banner at first arm.

### 27. Sex tape liability

Bedroom monitoring + couple having sex + clip stored on user's Google Drive + ex-partner gets phone access = revenge porn distribution. Your platform was the enabler.

**Fix:**
- "Bedroom mode" auto-disarms 11 PM - 7 AM by default
- Strong warning at first install: "Do not point at a bed where intimacy may occur"
- Privacy mask zones (already a feature in spec — implement before launch)

### 28. Lawsuit from a laptop fire that SPYME failed to detect

User trusts SPYME, has no smoke detector, a real fire happens, SPYME misses it because it was a slow-burning electrical fire (no flame visible in camera). House burns down. They sue.

**Fix:** Liability cap in TOS (already there), aggressive disclaimers, mandate "verify your smoke detectors work" banner monthly.

### 29. Apple/Google account suspension

Your entire mobile distribution lives on Apple's and Google's terms. One bad review trigger from a competitor's bot army → suspended → company dies.

**Fix:** Always have web version available. Don't make App Store presence existential.

### 30. Subscription chargebacks

Users who forget about $5/month → 6 months later → see charge → call bank → chargeback. Apple/Google process these. You eat the cost AND the chargeback fee.

**Fix:** Send "your subscription will renew tomorrow" email 24h before charge. Most apps don't. Reduces chargebacks 40%.

---

## 🟤 CATEGORY 6 — Founder reality

### 31. Customer support at scale

1,000 users × ~1 ticket/month = 1,000 tickets. At 5 min/ticket = 83 hours/month. That's a part-time job. Your job. While building features.

**Fix:** Build aggressive self-service: troubleshooter UI, "I'll fix it for you" auto-actions, AI chatbot trained on FAQs.

### 32. Monthly revenue ≠ monthly profit

Even at $1k MRR (200 paid users), after Apple cut + server + Twilio + Stripe + your time = you might net $400/month. That's not a salary.

**Fix:** Get to $10k MRR before quitting your day job. That's 2,000 paid users — 18 months of focused work.

### 33. Founder burnout

You'll be doing dev + sales + support + marketing + legal — alone. Solo founder burnout rate >70% in year 1.

**Fix:** Find a co-founder, or accept this is a side project not a startup.

---

## ⚪ CATEGORY 7 — What competitors will do

### 34. Apple ships "Sentinel Mode" for old Macs

Apple already has Find My, Stage Manager, Shortcuts. They could ship a free first-party "use my old Mac as a security camera" tomorrow. They'd kill SPYME on iOS overnight.

**Fix:** Cross-platform is your moat — work on Windows + Mac. Apple won't go cross-platform.

### 35. Frigate keeps growing

Frigate (open source, 30k GitHub stars) is the dominant DIY surveillance product. Free, runs on Pi, has a huge Home Assistant community.

**Fix:** Don't compete on power-user features. Compete on simplicity + mobile-first UX. Frigate's UX is awful.

### 36. Wyze adds laptop mode

Wyze has consumer brand awareness + $20 cameras. They could add a free "use your old phone" mode and bundle with their cam.

**Fix:** Move fast. Get to 10k users before incumbents notice.

---

## TL;DR — The five things that ACTUALLY worry me

1. **Apple/Google reject the app as stalkerware** — biggest existential risk
2. **Fire detection false positives at 3 AM** — one viral angry tweet kills your trust
3. **Webcams are bad cameras** — physical limit on user satisfaction
4. **Solo founder + thin margins + 30% Apple cut** — won't pay rent for 18 months
5. **You're a CS student who's never run a business** — true for every founder, but compounds the others

## What I'd do if I were you

1. **Ship it as a side project. Don't quit school plans.** Get 100 users at IIT Chicago in beta.
2. **Pick ONE killer use case** — "AI camera for college students with bad roommates" — drop the fire detection from V1. It's risky and hard.
3. **Find a co-founder THIS SEMESTER.** Sales/design/business background. Even if just 10% equity.
4. **Apply for free credits NOW.** GitHub Student Pack + Microsoft Founders Hub + Google for Startups. $5k+ in free cloud.
5. **Do not pay $124 for app stores until you have 100 active users.**

If after 6 months of beta you have 100 engaged users + 20 paying → keep going.
If after 6 months you have 10 users → kill it, take the lessons, build the next thing.

Be honest with yourself about which of these drawbacks you're solving and which you're hand-waving. The ones you hand-wave are the ones that kill you.
