# SPYME — Founder Story & Vision

## Who I am

**Mustafa Khan** — CS engineer, graduating May 2026 with a Master's in
Computer Science from **Illinois Institute of Technology, Chicago**.

## The lived pain that started this

### 1. Roommates I couldn't trust
For years I lived with roommates who walked in and out of my room while
I was at class, in the library, or out of town. Things moved.
Sometimes things disappeared. Confronting a roommate over a missing
charger destroys a friendship — but doing nothing makes you the fool.
**I needed eyes in my own room without paying $300 for a camera system
on a student budget.**

### 2. The gas leak that almost killed someone
Last year my house had a gas leak. Nobody was home for hours.
A real CCTV with smoke/fire detection would have alerted me instantly.
I didn't have one. **I couldn't afford to put cameras in every room** —
kitchen, bedroom, hallway, garage. Even one decent camera with cloud
recording is $10–$15/month per device, forever.

### 3. The insight that wouldn't leave me alone
Every time I shut my laptop and walked out of my apartment I thought:
*this thing has a 1080p camera, an Intel chip, a microphone, Wi-Fi, a
hard drive, and a battery — it is a CCTV camera that's pretending to
be a notebook.* If I had 3 laptops in 3 rooms (mine, my roommate's old
one, my parents' spare), I'd already have a 3-camera system. **The
hardware is sitting idle in 1.4 billion homes.**

That's where SPYME began — out of frustration that the answer was
right in front of every person who had ever owned a laptop.

## Why this matters more than I first realized

| Reason | Who it helps |
|--------|--------------|
| **Broke students** can't afford Ring/Nest cameras + monthly fees | 20M US college students alone |
| **Renters** can't drill holes in walls for permanent cameras | 44M US renter households |
| **International students** can monitor their stuff during winter break trips home | 1M+ in the US |
| **Aging parents** want to check on each other without learning Ring's UI | every adult child of an immigrant parent |
| **Small Airbnb hosts** can't afford pro security across 5 properties | 4M Airbnb hosts |
| **People who already own 2-3 laptops** — old MacBooks, dead-screen Windows boxes, retired work laptops gathering dust in closets | nearly everyone in tech-forward homes |
| **Travelers** want to verify movers, cleaners, dog-sitters didn't go through their things | anyone who hires household help |
| **Gas/fire safety** for older houses without smart smoke detectors | every renter, every old building |

## Why this is a company, not a feature

1. **The hardware is already deployed and paid for.** No CapEx.
   Ring needs you to buy a $99 camera. SPYME asks you to plug in
   something you already own.
2. **Multi-laptop = household network effect.** One account, many
   nodes. The more laptops a family activates, the more the
   product is worth — and the harder it is to leave.
3. **Privacy that incumbents structurally cannot offer.** Ring's
   business model requires storing your video. SPYME can run
   100% local-only or in *your own* Google Drive. Amazon will
   never offer that.
4. **A wedge into computer vision distribution.** Once SPYME
   is on millions of laptops, it's the easiest distribution
   for any CV product — health monitoring, focus tracking,
   gesture control, accessibility tools.

## The "Why now?"

- **YOLOv8** runs at 7+ FPS on a CPU laptop in 2025. In 2020 you
  needed a $2,000 GPU.
- **WebRTC P2P** is finally stable enough that we don't need
  expensive media servers — laptops talk straight to phones.
- **Apple Silicon + recent Intel** webcams are 1080p+, low light
  has improved 4× since 2018.
- **Renters > homeowners** for the first time in major US metros
  (people can't drill holes for Ring).
- **Gen Z mistrust of Ring** after Amazon's police-data-sharing
  scandals. Privacy is now a buying criterion.

## The market

- **TAM:** 1.4B laptops worldwide × ~200M households with multiple
  laptops × $5/month = $12B/year theoretical ceiling.
- **SAM:** Privacy-conscious renters + students globally.
  ~150M households. **$9B/year.**
- **Wedge market (initial):** US college students with roommates +
  multiple laptops. ~5M households at $5/mo = **$300M ARR
  obtainable within 5 years.**

## Pricing model

- **Free** — 1 laptop, 24h event history, push notifications.
- **Plus ($4.99/mo)** — Unlimited laptops, 30-day cloud history,
  fire alerts + SMS, multi-person/theft AI.
- **Family ($9.99/mo)** — Above + 5 user accounts, Apple Watch,
  emergency contacts, "Store in my Google Drive" mode.

Lower than Ring ($3.99/cam/mo + $99 hardware = ~$10/cam/mo
effective). Higher gross margin (no hardware).

## Distribution strategy

1. **Reddit + TikTok** — "Turn your old MacBook into a security
   camera in 60 seconds" demo videos. Built-in virality.
2. **University Reddit subs** — `r/uchicago`, `r/IITKgp`,
   `r/college`. Roommate horror stories sell themselves.
3. **Airbnb host Facebook groups** — high willingness to pay.
4. **Reseller deals** — laptop refurbishers (Back Market,
   Decluttr) bundle SPYME with sold devices.

## Product roadmap (already shipped — this repo)

- ✅ Webcam → AI engine (YOLOv8 + ByteTrack + pose)
- ✅ Multi-person + action + theft detection (object disappeared
  while person nearby)
- ✅ Fire detection (HSV + flicker, no training needed)
- ✅ Live P2P WebRTC stream from laptop → phone
- ✅ Push notifications (FCM/APNs)
- ✅ Critical fire alerts → SMS via Twilio + full-screen
  vibrating siren
- ✅ Multi-device dashboard (one account, N laptops)
- ✅ Cover Mode (laptop shows wallpaper while monitoring)
- ✅ "Continue with Google" + optional clip storage in user's
  own Drive
- ✅ Backend: FastAPI + Postgres + Redis + S3/R2 +
  Coturn TURN

## What I want to build next

- Native installers (one-click Windows + macOS)
- 100-user closed beta from IIT Chicago campus
- Onboarding video that goes viral on TikTok
- Apply to YC W26 with 1,000+ active beta users

## Why me

I'm not a serial founder. I'm a CS engineer who **lived this
problem in my own apartment for two years** and built the
solution because nobody else was going to. I have shipped
working code across web, mobile, and ML — this repo is proof.
I'm two months from graduation, debt-free thanks to grants,
and I will work on this full-time starting June 2026.

If YC backs me, I commit to:
- 1,000 paying users by end of W26 batch
- $50k MRR in 12 months
- Open-sourcing the AI engine to build community moat
- Hiring my first engineer (also IIT Chicago) within 6 months
