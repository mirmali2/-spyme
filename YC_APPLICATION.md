# YC Application Draft — SPYME (Winter 2026)

> Use these answers as starting points. Actual YC application has
> 50-word and 100-word limits per question — I've kept these under
> the limits.

---

### Company name
**SPYME**

### Describe what your company does in 50 characters or less
Turn any laptop into a privacy-safe AI security camera.

### What is your company going to make? (≤700 chars)
SPYME turns the laptops people already own into AI security
cameras. One account links unlimited laptops in unlimited rooms;
your phone is the remote control and live viewer. The AI runs
locally on each laptop — multi-person tracking, theft detection
("someone took your keys"), and fire/smoke alerts that bypass
mute and vibrate your phone with a siren.

Privacy is the wedge: clips can be stored in our cloud, in your
*own* Google Drive, or local-only. Live streams are P2P WebRTC
and never touch our servers.

A free Wyze cam costs $30 + a monthly fee. The MacBook Pro on
your desk is already paid for, and it's a better camera.

### Where do you live now, and where would the company be based?
Chicago, IL → moving to YC if accepted.

### Have you ever applied for or participated in YC?
No.

---

### How far along are you?
Working product across all 3 layers (laptop agent, mobile app,
backend). 17 mobile screens designed. AI engine validated end-to-end
on real images: 7 FPS multi-person + pose + theft + fire on a
mid-range CPU laptop. Backend deployed locally with FastAPI +
Postgres + Redis + WebRTC signaling. Need to: run beta, get users.

### How long have you been working on this?
6 weeks of nights/weekends. Going full-time June 2026 after I
graduate.

### How much money have you raised?
$0. Bootstrapped on student stipend.

### Are people using your product?
Not yet — entering closed beta with ~50 IIT Chicago students this
month.

### Do you have revenue?
Not yet.

---

### Why did you pick this idea? Do you have domain expertise?

I'm a CS Master's student at IIT Chicago graduating May 2026.
I've lived the problem for years — roommates wandering through my
room while I'm in class, things going missing, and last year a
gas leak in my apartment that nobody was home to catch. A real
camera system was $300+ and a monthly fee per camera I couldn't
afford on a student budget.

The insight that wouldn't leave me: the laptop on my desk is a
1080p webcam, an Intel chip, a hard drive, Wi-Fi, and a battery.
**It is already a CCTV camera pretending to be a notebook.**
Every household has 2-3 of these sitting idle when nobody's
using them. We don't need to ship hardware. We need to wake
up the hardware that's already there.

I built it because nobody else did.

### Why now? What's changed?

- **YOLOv8** runs at 7+ FPS on a CPU laptop. In 2020 you needed
  a GPU. In 2026 the inference is essentially free.
- **WebRTC P2P** is finally stable on iOS/Android — laptops can
  stream to phones with no media server.
- **Renters now outnumber homeowners** in major US metros.
  Renters can't drill holes for Ring. They need software.
- **Trust collapse** — Amazon's police-data sharing scandal made
  privacy an actual buying criterion among Gen Z. Incumbents
  *cannot* offer "your video stays in your Drive" because their
  business model requires holding it.

### What's the moat?

1. **The hardware is already deployed.** Ring needs you to buy
   a $99 camera. We need 60 seconds of install time. Lowest
   activation cost in the category.
2. **Multi-laptop network effect inside a household.** One
   account + N laptops = network-effect-of-one. The more nodes
   a family activates, the harder it is to switch.
3. **Privacy positioning Ring/Nest structurally cannot copy.**
   Their P&L requires storing your data.
4. **Distribution wedge into computer vision.** Once SPYME is
   on millions of laptops, every CV product (focus tracking,
   accessibility, gesture control) ships through us.

### Who are your competitors? Who *might* become competitors?

- **Ring / Nest / Arlo** — sell hardware + cloud subscription.
  Won't cannibalize $4B hardware revenue to sell a software-only
  product. Strategic blind spot.
- **Wyze / Eufy** — race-to-bottom on hardware price. Same
  business model.
- **Frigate** (open source) — closest competitor in spirit but
  requires a dedicated server, network knowledge, and a
  Raspberry Pi. We are 60 seconds; they are a weekend project.
- **Manything (acquired & shut down 2018)** — proves the laptop
  approach has demand. They had 3M downloads before acquisition.

### How will you make money?

Freemium SaaS:

- **Free** — 1 laptop, 24h history.
- **Plus $4.99/mo** — Unlimited laptops, 30-day history, fire
  alerts, theft AI.
- **Family $9.99/mo** — Above + 5 users, Watch app, "Store in
  my Drive" mode, emergency SMS.

Target: 5% free→paid conversion. 100k free users → $250k MRR.

### What's the worst that can happen to your company in the next year?

Apple or Microsoft ships native "use your laptop as a security
camera" feature. Mitigation: we move faster than OS vendors,
build cross-platform multi-device experience they won't match,
and our privacy positioning beats their default cloud play.

Realistic worst case: paid conversion is below 2%, we need a
B2B pivot to Airbnb hosts or small retail (theft detection
on existing cameras).

---

### What is the next step / what would you do with YC funding?

- Hit 10,000 active beta users before W26 batch starts (organic +
  Reddit + TikTok virality of "60-second laptop CCTV" demo).
- Hire one engineer to ship native installers + Apple Watch app.
- Get to $50k MRR by end of batch.
- Use Demo Day to raise a pre-seed round to expand into B2B
  Airbnb / property-management vertical.
