# App Store + Play Store Listing Copy

Use these word-for-word — they're tuned to fit Apple/Google character limits AND avoid stalkerware-policy red-flag terms.

---

## App name (Apple ≤30 chars, Google ≤30 chars)

```
SPYME — Laptop Security Cam
```

## Subtitle (Apple ≤30 chars)

```
Your laptop, your camera
```

## Promotional text (Apple ≤170 chars)

```
Turn the laptops you already own into AI security cameras you control from your phone. Multi-person tracking, fire detection, theft alerts. Privacy-first.
```

## Short description (Google ≤80 chars)

```
Turn your laptop into a private AI security camera you control from your phone.
```

## Full description (Apple ≤4000, Google ≤4000)

```
SPYME turns the laptops you already own into AI security cameras you control from your phone. Bedroom, kitchen, dorm, office — link up to 4 laptops to one account, watch them all live, and get instant alerts when something matters.

WHY SPYME

Most security cameras cost $30-150 plus a monthly cloud fee per camera. The MacBook on your desk is a 1080p camera you've already paid for. SPYME just wakes it up.

WHAT YOU GET

• Live HD video from any of your laptops, sub-second latency, P2P
• AI multi-person tracking — knows when 2+ people are in frame
• Theft detection — alerts when a confirmed object disappears while a person was nearby
• Fire detection — vibrating siren + SMS to your emergency contact
• Push notifications on every alert (instant, never delayed)
• Apple Watch app for quick glances
• "Cover Mode" — laptop shows a normal wallpaper while monitoring continues, with a visible indicator that's never hidden
• Up to 4 laptops per account

PRIVACY-FIRST BY DESIGN

We do not store your videos. Ever.

• Live streams are P2P — laptop talks straight to your phone, our servers never see your video
• Recorded clips stay on your laptop, your phone, or your own Google Drive (your choice at signup)
• No audio recording, ever
• Face recognition is local-only — biometric data never leaves your laptop
• Persistent visible "MONITORING" indicator means nothing is hidden from anyone in the room
• Audio is permanently disabled at the OS level
• Open privacy policy + GDPR / CCPA / DPDPA compliant

PRICING

• 2-day free trial — no card required
• Free tier after trial: 1 camera, 24-hour history, motion + person detection
• Pro Monthly: $9.99 — up to 4 cameras, 30-day history, theft AI, fire alerts
• Pro Yearly: $99.99 — same as monthly, save $20

ACCEPTABLE USE

SPYME is for monitoring your own space — your bedroom, your dorm room, your home office, your rented apartment. By using SPYME you agree that all adults in the monitored space have been informed. Do not use SPYME to surveil people without their consent.

Built by Mustafa Khan, IIT Chicago. Questions? hello@spyme.app
```

---

## Keywords (Apple ≤100 chars, comma separated, NO spaces after commas)

```
security,camera,monitor,laptop,webcam,ai,detection,fire,theft,alarm,home,room,dorm,renter,student
```

---

## App Store category

- **Primary:** Lifestyle
- **Secondary:** Utilities

NOT "Health & Fitness" (medical claims). NOT "Productivity". NOT "Reference".

## Play Store category

- **Primary:** Tools

---

## Age rating

- **Apple:** 17+ (mentions of monitoring — Apple flags anything under 17+ for surveillance terminology)
- **Google:** 13+

---

## Apple Privacy Nutrition Label (filled at submission)

| Category | Used? | Linked to user? | For tracking? |
|----------|-------|-----------------|---------------|
| Camera | ✅ Required | No | No |
| Microphone | ❌ Not used | — | — |
| Email | ✅ Account creation | Yes | No |
| Phone Number | ✅ Optional, fire SMS only | Yes | No |
| Crash data | ✅ App functionality | No | No |
| Performance data | ✅ App functionality | No | No |
| Other usage data | ❌ Not collected | — | — |
| Location | ❌ Not collected | — | — |
| Contacts | ❌ Not collected | — | — |
| Photos/Videos | ❌ Not stored on our servers | — | — |

Tracking: **NO** (we don't track users)

---

## Google Play Data safety form (filled at submission)

**Data collected and shared:** Email (account), Phone (optional), Camera frames (processed locally on user's laptop, never sent to us)

**Data shared with third parties:** No

**Encryption in transit:** Yes (TLS)

**Users can request deletion:** Yes (in-app settings)

---

## Required URLs (you'll paste these into App Store Connect / Play Console)

| Field | URL |
|-------|-----|
| Privacy policy | `https://spyme.vercel.app/privacy` |
| Terms of service | `https://spyme.vercel.app/terms` |
| Support | `mailto:hello@spyme.app` |
| Marketing | `https://spyme.vercel.app/` |

---

## Reviewer notes (Apple App Review only)

```
Hi App Review,

SPYME turns the user's own laptop into an AI security camera they control from their phone.

CONSENT FLOW: At first arming, the user must explicitly confirm "all adults in this monitored space have been informed." This is not skippable. The laptop also shows a persistent visible "MONITORING ACTIVE" indicator — never hidden — so anyone in the room knows the camera is on.

DATA HANDLING: We do not store user videos on our servers. All clips stay on the user's laptop, on their phone, or in their own Google Drive. Live streams are P2P over WebRTC — our servers only relay signaling, never media bytes.

TEST ACCOUNT:
  email: reviewer@spyme.app
  password: ReviewSPYME2026!

This account is pre-paired with a test laptop you can stream from.

Please contact mustafa@spyme.app if any clarification is needed.

Thanks,
Mustafa Khan
```

---

## What to upload, in order

1. **App icon** — 1024×1024 PNG, no transparency, no rounded corners (Apple rounds for you)
2. **Screenshots** — generated by `store-assets/capture.js` (5 PNGs at 1290×2796)
3. **App Preview video** — optional but boosts conversion 25%. Capture a 30s screen recording of the iOS app showing: open → see live → arm → get alert. Trim to 15-30 seconds at 1080×1920 or 1290×2796.
4. **Listing copy** — paste from above
5. **In-App Purchase products** — set up Pro Monthly ($9.99) and Pro Yearly ($99.99) in App Store Connect / Play Console BEFORE submitting

---

## Submission day checklist

- [ ] All 5 screenshots uploaded (1290×2796)
- [ ] App icon uploaded (1024×1024)
- [ ] Listing copy pasted
- [ ] Privacy URL set to spyme.vercel.app/privacy
- [ ] In-App Purchases configured ($9.99 monthly, $99.99 yearly)
- [ ] Test account credentials in reviewer notes
- [ ] Apple Privacy Nutrition Label filled
- [ ] Submit to TestFlight first (1-3 day review)
- [ ] After 7 days of TestFlight stability → submit for App Store review (1-3 days)
- [ ] Same for Google Play Internal Testing (24-48h) → Production
```
