# Shipping SPYME — Honest Cost Breakdown

You said "I don't have money." Here's the truth: **you can ship for $124 total**, and most of even that you can avoid using student programs you already qualify for as an IIT Chicago student.

---

## 💰 The minimum you actually MUST pay

| Item | Cost | Can it be free? |
|------|------|-----------------|
| **Apple Developer Program** | $99/year | ❌ No alternative — Apple charges everyone. |
| **Google Play Console** | $25 once | ❌ No alternative — Google charges everyone. |
| **Domain** spyme.app | $20/year | ✅ Skip — use spyme.vercel.app FREE |
| **Backend hosting** | $0–5/mo | ✅ Render free tier OR Railway $5 |
| **Database** | $0 | ✅ Supabase free 500MB OR Neon free 3GB |
| **Object storage** | $0 | ✅ NOT NEEDED — we don't store videos! |
| **Push (FCM)** | $0 | ✅ Free forever |
| **TURN server** | $0–5/mo | ✅ Skip initially — most networks work without TURN |
| **SMS (Twilio)** | $15 trial credit | ✅ ~2,000 fire alerts free with trial |
| **Code signing macOS** | included in Apple Dev | (already in $99) |
| **Code signing Windows** | $200/yr EV cert | ✅ Skip — users see one warning click "Run anyway" |

### **Minimum to ship: $124** (Apple $99 + Google $25)

Everything else can be free using student credits.

---

## 🎓 Free credits you qualify for (IIT Chicago student)

Apply for these THIS WEEK — most take 1-3 days for approval:

| Program | What you get | Worth |
|---------|--------------|-------|
| **GitHub Student Pack** (github.com/education) | DigitalOcean $200 + Namecheap free .me domain + JetBrains tools + Heroku credits | $1,000+ |
| **Google for Startups Cloud Program** | $2,000–$200,000 GCP credit, free WorkSpace | $2,000+ |
| **AWS Activate (Founders)** | $1,000 AWS credit | $1,000 |
| **Microsoft for Startups Founders Hub** | $150,000 Azure credits + $5k OpenAI/GitHub Copilot | $150k+ |
| **Apple Developer Discount for Education** | Sometimes 50% off ($49/yr) — apply via your university | $49/yr saved |
| **Notion for Students** | Free pro forever | $96/yr |
| **MongoDB for Startups** | $500 credit | $500 |
| **Supabase Education** | Free pro tier | $300/yr |
| **Cloudflare Pro for Students** | Free Pro plan | $240/yr |

**TOTAL FREE CREDITS AVAILABLE TO YOU: $5,000+ in your first month**

---

## 🚀 The 30-day shipping plan (zero money required to start)

### Week 1 — Backend live + free hosting
1. Push backend to GitHub
2. Sign up Render.com (free), connect repo → auto-deploy
3. Sign up Supabase (free), get Postgres connection string
4. Set env var `DATABASE_URL` on Render
5. Your backend is live at `https://spyme-api.onrender.com`

### Week 2 — Beta laptop installer (no signing needed)
1. `cd desktop && npm run build:win` → produces `SPYME-Setup.exe`
2. `cd desktop && npm run build:mac` → produces `SPYME.dmg`
3. Upload both to GitHub Releases (free)
4. Update website download links to point at GitHub Releases URLs
5. Push website to Vercel (free) → live at `spyme.vercel.app`

### Week 3 — TestFlight + Internal Testing (NO STORE FEES YET)
1. Pay $99 Apple Developer fee, $25 Google Play fee
2. `cd mobile && npx eas build --platform ios` → produces .ipa
3. Upload to TestFlight → invite 100 IIT Chicago testers FREE
4. `cd mobile && npx eas build --platform android` → produces .aab
5. Upload to Google Play Internal Testing → invite 100 testers FREE

### Week 4 — Iterate based on beta feedback
- Fix bugs
- Make 3 TikTok videos: "60 second laptop CCTV"
- Reddit: r/uchicago, r/IITKgp, r/college, r/Frugal

### Month 2 — Public launch
- Submit to App Store (review: 1-3 days)
- Submit to Play Store (review: hours-3 days)
- Both go live simultaneously

---

## 🔑 What I need FROM YOU before any money is spent

### Right now (free, ~30 min total):

1. **Apple ID** — sign in at https://developer.apple.com (you already have one for your Mac/iPhone)
2. **Google account** — already have it
3. **GitHub account** — sign up at github.com if you don't have one
4. **Bundle IDs** — pick:
   - iOS: `com.spyme.app` (already in `mobile/app.json`)
   - Android: `com.spyme.app` (already in `mobile/app.json`)
   - macOS: `com.spyme.desktop` (already in `desktop/package.json`)
5. **Domain decision** — `spyme.vercel.app` (free) OR buy spyme.app for $20/yr later

### When you're ready to pay $124 (week 3):

6. **Apple Developer enrollment** — https://developer.apple.com/programs/enroll/
   - Need: government ID, $99
7. **Google Play Console** — https://play.google.com/console/signup
   - Need: $25, ID verification

### Optional (can skip until you have revenue):

8. **Twilio account** — $0 to sign up, $15 trial credit. Get phone number for fire-SMS.
9. **Stripe** — $0 to sign up. Need: bank account for payouts.
10. **Firebase project** — free. For push notifications.

---

## 🚫 What you DON'T need

- Cloud GPU ($0)
- Video storage ($0 — we don't store any!)
- Code signing certificates ($0 to skip)
- Custom domain (use Vercel subdomain)
- TURN server (most networks don't need one)
- Marketing budget (TikTok virality is free)
- Lawyer for privacy policy (template provided in `legal/PRIVACY.md` — review later if you raise money)
- Analytics tool (use PostHog free tier when ready)

---

## 📋 App Store submission checklist

### Apple App Store

- [ ] Apple Developer enrolled ($99)
- [ ] Bundle ID `com.spyme.app` registered
- [ ] App icon: 1024×1024 PNG (no transparency)
- [ ] Screenshots: 6.7" iPhone (1290×2796) — at least 3, max 10
- [ ] App description (under 4,000 chars)
- [ ] Keywords (under 100 chars total)
- [ ] Privacy policy URL → `https://spyme.vercel.app/legal/PRIVACY.md`
- [ ] Support URL → `mailto:hello@spyme.app`
- [ ] Privacy nutrition label (camera permission, no data sold)
- [ ] App Review Information (test login + notes for reviewer)
- [ ] In-App Purchase products configured ($5/mo, $50/yr) — uses Apple's billing not Stripe
- [ ] Build uploaded via Xcode or `eas submit -p ios`

### Google Play Store

- [ ] Google Play Console paid ($25)
- [ ] App bundle (.aab) signed and uploaded
- [ ] Feature graphic: 1024×500 PNG
- [ ] Screenshots: at least 2, up to 8 per type
- [ ] Short description (80 chars), full description (4,000 chars)
- [ ] Content rating questionnaire (1 min)
- [ ] Privacy policy URL
- [ ] Data safety form (camera, no data sold, no tracking)
- [ ] Subscription products configured (uses Google billing)
- [ ] Internal testing track first → production after 7 days

---

## 🍿 The honest opinion

**Don't pay the $124 yet.** Here's the smarter sequence:

1. **This week:** Apply for GitHub Student Pack + Google for Startups + AWS Activate. You get $5,000+ in free cloud credits in 3 days. Cost: $0.

2. **Next 2 weeks:** Get 50 IIT Chicago students using SPYME via TestFlight beta (still no money — TestFlight uses your Apple ID free for 100 testers, no Apple Developer Program needed if you're just sideloading, but TestFlight requires the $99 enrollment).

   **Actually for 100% free beta testing:** ship the laptop app via GitHub Releases (no Apple/Google fees), and have beta testers use the **mobile web app** I'll add (PWA — installs to home screen, works fine for live view + dashboard).

3. **Once you have 100 active beta users:** then pay the $124 for App Store + Play Store. Now you have proof people want it.

4. **Once you have 50 paying users ($250+ MRR):** then think about YC.

The $124 is a *lot* less scary when 50 people are paying you $5/month — that's $250 in your pocket monthly, recurring.

---

## What I'll build next if you want

Tell me which to do next:

- [ ] PWA mode (free mobile beta — no app store needed)
- [ ] Auto-build script for laptop installers (one command → .exe + .dmg)
- [ ] App Store screenshots generator (uses preview screens)
- [ ] One-click deploy to Render
- [ ] Beta signup page
