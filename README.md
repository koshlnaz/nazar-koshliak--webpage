# nazar-koshliak.com

Personal website for **Nazar Koshliak** — Real estate portfolio manager based in Dubai.

Live: https://nazar-koshliak.com

## Stack

- Plain HTML/CSS/JavaScript (no build step)
- GSAP + ScrollTrigger for cinematic scroll animations
- Hosted on Cloudflare Pages (auto-deploys from `main`)

## Structure

```
.
├── index.html         # Home — cinematic, video hero, scrolling scenes
├── about.html         # About
├── services.html      # Services
├── experience.html    # Experience & awards
├── contact.html       # Contact
├── assets/
│   ├── site.css       # Shared base + mobile nav + Burj indicator
│   ├── cinematic.css  # Home-page cinematic scene styles
│   ├── site.js        # Shared JS (nav toggle, reveal, inner-page Burj)
│   ├── cinematic.js   # Home-page GSAP animations + Burj
│   └── ...            # Photos, logos, hero video
└── wrangler.jsonc     # Cloudflare Pages config
```

## Deploy

Push to `main` → Cloudflare Pages auto-deploys in ~30 seconds.

```bash
git add .
git commit -m "describe change"
git push origin main
```

## Editing

- Text content → edit the relevant `.html` file
- Shared styles → `assets/site.css`
- Home cinematic styles → `assets/cinematic.css`
- Scroll animations → `assets/cinematic.js`
