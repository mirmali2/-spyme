# Deploy SPYME to Vercel (free, ~3 min)

The repo is already configured. You just need to connect it.

## One-time setup

1. Go to **https://vercel.com/new**
2. Sign in with your GitHub (`mirmali2`)
3. Click **Import Project** → find `mirmali2/-spyme` → click **Import**
4. Vercel auto-detects the `vercel.json` config. Just click **Deploy**.
5. Wait ~30 seconds.

You'll get a free URL like:
- `https://spyme.vercel.app` (if you set the project name to `spyme`)
- or `https://-spyme-mirmali2.vercel.app` (default)

## What gets deployed

| URL | Serves |
|-----|--------|
| `/` | Landing page (`website/index.html`) |
| `/preview` | Mobile app preview (28 screens) |
| `/privacy` | Privacy policy |
| `/terms` | Terms of service |
| `/story` | Founder story |

The `vercel.json` is configured to:
- Skip backend/desktop/mobile folders (only ship the static site)
- Add security headers (CSRF, frame deny, referrer policy)
- Block camera/mic permissions on the marketing site
- Redirect `/privacy` → `/legal/PRIVACY.md`, etc.

## Auto-deploy on every push

Once connected:
- Every `git push origin main` → Vercel auto-deploys in 30 sec
- Every PR → preview deployment with a unique URL
- Zero config — just push code

## Custom domain (later, $20/year)

When ready:
1. Buy `spyme.app` on Namecheap or Cloudflare
2. Vercel project → Settings → Domains → Add `spyme.app`
3. Vercel gives you DNS records to add at your registrar
4. Auto SSL via Let's Encrypt (free)

## Cost

**Hobby tier (free, forever):**
- 100 GB bandwidth/month
- Unlimited static sites
- Unlimited git deploys
- Auto SSL

**You don't pay until you have ~50,000 monthly visitors.** Plenty of runway.

---

## Troubleshooting

**"Project name not available"** — Vercel reserves common names. Just accept the auto-suggested one (e.g. `spyme-mirmali2`); you can change it later via custom domain.

**"404 at root"** — Make sure `vercel.json` rewrites `/` → `/website/index.html`. Already configured.

**Preview shows raw markdown** — Privacy/Terms pages render as plain text. To render them styled, install a markdown converter. (Skip for now; raw markdown is fine for legal docs.)
