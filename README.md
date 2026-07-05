# podcast.mingli.world

Daily learning podcast for software engineers preparing for English-language interviews. 5-minute episodes covering English patterns, interview frameworks, and speaking practice.

**Live:** `https://podcast.mingli.world` (via Cloudflare Pages)  
**RSS:** `https://podcast.mingli.world/rss.xml`

## Architecture

| Layer | Technology | Details |
|-------|-----------|---------|
| Hosting | Cloudflare Pages | `podcast-landing` project |
| Storage | Cloudflare R2 | `podcast-mingli-world` bucket |
| Functions | Pages Functions (4) | manifest, RSS, episodes, feedback API |
| Pipeline | GitHub Actions | Daily cron: arrange → curate → generate → publish |
| TTS | edge-tts (free) | Microsoft Edge TTS API, no key required |
| CLI tools | Wrangler | R2 operations via `--remote` flag |

No backend server. No database. JSON files on R2 are the database.

## Project Structure

```
├── site/                     # Landing page (mobile-first, 4 tabs)
│   └── index.html
├── functions/                # Cloudflare Pages Functions (R2 binding)
│   ├── api/feedback.js       # POST — write 👍/👎 to R2
│   ├── manifest.json.js      # GET — serve manifest from R2
│   ├── rss.xml.js            # GET — serve RSS from R2
│   └── episodes/[file].js    # GET — serve MP3 from R2
├── scripts/                  # Pipeline (runs in GitHub Actions)
│   ├── arrange.py            # 4 AM — collect feedback, compute ratios, plan next episode
│   ├── curate.py             # 5 AM — fetch RSS feeds, pick relevant article
│   ├── generate.py           # 5 AM — build script, run edge-tts → MP3
│   ├── publish.py            # 5 AM — upload MP3, update manifest, regenerate RSS
│   ├── r2_utils.py           # Wrangler CLI wrapper for R2 operations
│   └── content_bank.json     # 23 patterns, 10 tips, 20 prompts
├── .github/workflows/daily.yml  # Cron: 4 AM arrange, 5 AM publish
├── wrangler.toml             # Cloudflare Pages + R2 binding config
└── manifest.json             # Episode index (source of truth for all episodes)
```

## Landing Page

Mobile-first design with 4 tabs:

| Tab | Content |
|-----|---------|
| Today | Latest episode, audio player, engineering examples with copy button, source attribution, feedback |
| Patterns | 10 phrases organized by category — tap to expand for real-world examples |
| Frameworks | 7 interview frameworks with step-by-step breakdowns |
| History | All past episodes with vote status |

All patterns and tips are embedded in the HTML for offline browsing. Only the episode list fetches from manifest.json at runtime.

## Pipeline

```
4:00 AM AEST  arrange.py    Read feedback → compute ratios → write plan.json to R2
5:00 AM AEST  curate.py     Fetch RSS feeds → pick article → write today.json
5:01 AM AEST  generate.py   Read plan.json → build script → edge-tts → episode.mp3
5:07 AM AEST  publish.py    Upload MP3 to R2 → update manifest.json → regenerate rss.xml
6:00 AM AEST  Episode published, landing page updated
```

## Setup

### Secrets (GitHub Actions)

- `CLOUDFLARE_API_TOKEN` — Cloudflare API token with Pages + R2 permissions
- `BASE_URL` — `https://podcast-landing-868.pages.dev` (or custom domain)

### Manual Steps

1. **Custom domain:** Add `podcast.mingli.world` in Cloudflare Pages → Settings → Custom domains
2. **Artwork:** Upload 1400×1400 JPEG to R2 as `artwork.jpg`
3. **Directories:** Submit RSS to Apple Podcasts Connect and Spotify for Podcasters

### Local Development

```bash
npm install
pip install -r scripts/requirements.txt

# Deploy
npx wrangler pages deploy site --project-name podcast-landing --branch main

# Test pipeline
python3 scripts/arrange.py     # Needs CLOUDFLARE_API_TOKEN
python3 scripts/generate.py    # Needs CLOUDFLARE_API_TOKEN + edge-tts
python3 scripts/publish.py     # Needs CLOUDFLARE_API_TOKEN
```

## Cost

$0/month. All free tiers:

- Cloudflare Pages (500 builds/month)
- Cloudflare R2 (10 GB storage, no egress)
- GitHub Actions (2000 min/month)
- edge-tts (free, no API key)
