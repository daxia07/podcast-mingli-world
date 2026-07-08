# podcast.mingli.world

Daily learning podcast for software engineers preparing for English-language interviews. ~28-minute episodes covering English patterns, interview frameworks, and speaking practice — generated daily from real-world engineering content.

**Live:** `https://podcast.mingli.world` (via Cloudflare Pages)  
**RSS:** `https://podcast.mingli.world/rss.xml`  
**Episodes:** 10 published (daily pipeline active)

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
├── site/                     # Landing page (mobile-first, 3 tabs)
│   └── index.html
├── functions/                # Cloudflare Pages Functions (R2 binding)
│   ├── api/feedback.js       # POST — write 👍/👎 to R2
│   ├── manifest.json.js      # GET — serve manifest from R2
│   ├── rss.xml.js            # GET — serve RSS from R2
│   └── episodes/[file].js    # GET — serve MP3 from R2
├── scripts/                  # Pipeline (runs in GitHub Actions)
│   ├── arrange.py            # 4 AM — collect feedback, compute ratios, plan next episode
│   ├── curate.py             # 5 AM — fetch RSS feeds, pick relevant article
│   ├── generate.py           # 5 AM — build 3200-word script, run edge-tts → MP3
│   ├── publish.py            # 5 AM — upload MP3, update manifest, regenerate RSS
│   ├── r2_utils.py           # Wrangler CLI wrapper for R2 operations
│   └── content_bank.json     # 23 patterns, 10 tips, 20 prompts
├── .github/workflows/daily.yml  # Cron: 4 AM arrange, 5 AM publish (AEST)
├── wrangler.toml             # Cloudflare Pages + R2 binding config
└── manifest.json             # Episode index (source of truth for all episodes)
```

## Landing Page

Mobile-first design with 3 tabs:

| Tab | Content |
|-----|---------|
| Today | Latest episode ~28 min, audio player, content breakdown, feedback buttons |
| Patterns | 11 patterns by category (opinion, self-description, transitional, etc.) with real engineering examples — server-rendered, no JS dependency |
| History | Past episodes list, 7 interview frameworks, practice prompts |

All patterns and frameworks are server-rendered HTML for instant loading. Episode data and audio files load from R2 via Pages Functions.

## Episode Format (~28 min)

Each daily episode covers:

| Section | Duration |
|---------|----------|
| Intro + article discussion | ~5 min |
| 6 English patterns with examples | ~15 min |
| Deep dive (category-specific scenario) | ~5 min |
| 3 interview frameworks | ~9 min |
| Common mistakes | ~3 min |
| Cultural context | ~2 min |
| Practice prompts | ~3 min |
| Quick wins + listener Q&A | ~4 min |
| Outro | ~1 min |

## Pipeline

```
4:00 AM AEST  arrange.py    Read feedback → compute ratios → write plan.json to R2
5:00 AM AEST  curate.py     Fetch RSS feeds → pick article → write today.json
5:01 AM AEST  generate.py   Read plan.json → build 3200-word script → edge-tts (-15% rate) → episode.mp3
5:07 AM AEST  publish.py    Upload MP3 to R2 → update manifest.json → regenerate rss.xml
6:00 AM AEST  Episode published, landing page updated
```

## Feedback Loop

Listeners tap 👍 or 👎 on each episode. Feedback is stored in R2 as `feedback/{date}_ep{id}.json`. The arrange step reads 7 days of feedback per episode and computes good/bad ratios:

- **≥80% good** → pattern promoted, appears more frequently
- **40–80%** → pattern kept at normal rotation
- **<40%** → pattern dropped from rotation

Feedback persists in localStorage so users see their vote state across visits.

## Setup

### Secrets (GitHub Actions)

- `CLOUDFLARE_API_TOKEN` — Cloudflare API token with Pages + R2 permissions
- `BASE_URL` — `https://podcast.mingli.world` (or custom domain)

### Manual Steps

1. **Custom domain:** Add `podcast.mingli.world` in Cloudflare Pages → Settings → Custom domains
2. **DNS:** CNAME `podcast.mingli.world` → `podcast.mingli.world` (via Aliyun CLI)
3. **Artwork:** Upload 1400×1400 JPEG to R2 as `artwork.jpg`
4. **Directories:** Submit RSS to Apple Podcasts Connect and Spotify for Podcasters

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

---

## Next Steps & Future Features

### Phase 1 — Polish (this week)

| Task | Details | Priority |
|------|---------|----------|
| Podcast artwork | Upload 1400×1400 JPEG to R2 as `artwork.jpg` — required for Apple/Spotify submission | 🔴 High |
| Submit to directories | Apple Podcasts Connect + Spotify for Podcasters — RSS is ready | 🔴 High |
| Episode descriptions | Generate richer per-episode descriptions (currently first-line only) | 🟡 Medium |
| Mobile player polish | Sticky audio player that persists across tab switches; playback progress saved in localStorage | 🟡 Medium |
| Offline pattern browsing | Cache patterns in service worker for offline access | 🟢 Low |

### Phase 2 — Content Intelligence (next 2 weeks)

| Task | Details | Priority |
|------|---------|----------|
| Adaptive difficulty | Track per-pattern mastery via SM-2 spaced repetition — harder patterns get more airtime | 🔴 High |
| Multi-source curation | Curate from Hacker News, Reddit r/ExperiencedDevs, Engineering Blogs RSS in addition to current feeds | 🟡 Medium |
| Pattern gap detection | Analyze which pattern categories (opinion, clarification, disagreement, etc.) are under-represented | 🟡 Medium |
| Speaker voice variety | Rotate TTS voices (en-US male/female, en-GB, en-AU) for different sections | 🟢 Low |
| Transcripts | Generate and publish text transcripts alongside each episode for reading practice | 🟡 Medium |

### Phase 3 — Listener Experience (next month)

| Task | Details | Priority |
|------|---------|----------|
| Search | Full-text search across all episode descriptions and pattern names | 🟡 Medium |
| Personalized playlists | User picks their weak areas (e.g., "opinion phrases", "STAR-LA") → curated episode queue | 🟡 Medium |
| Progress tracking | Track which episodes listened to, patterns practiced, streaks — stored in localStorage | 🟢 Low |
| Push notifications | Web push API — "Today's episode is ready" at 6 AM local time | 🟢 Low |
| Speed controls | 0.75× / 1× / 1.25× / 1.5× playback — useful for learners | 🟢 Low |

### Phase 4 — Community & Scale (next quarter)

| Task | Details | Priority |
|------|---------|----------|
| User accounts | Optional Cloudflare Access or Firebase Auth — sync progress + feedback across devices | 🟢 Low |
| Community prompts | Listeners submit practice prompts → voted up by community → featured in episodes | 🟢 Low |
| Topic-specific series | Multi-day deep dives: "System Design Interview Week", "Behavioral Interview Week", etc. | 🟢 Low |
| Analytics dashboard | Listen count, completion rate, top patterns, feedback trends — private dashboard for content tuning | 🟢 Low |

### Technical Debt & Improvements

| Task | Details |
|------|---------|
| Error monitoring | Add health-check endpoint that verifies R2 connectivity + manifest integrity; alert on pipeline failure |
| Episode cleanup | Prune MP3s older than 90 days to stay within R2 10 GB free tier (est. ~3 MB/day = ~270 MB/quarter) |
| Build caching | Cache pip dependencies in GitHub Actions to speed up pipeline runs |
| CI smoke test | Verify generated MP3 is playable and manifest is valid JSON before publishing |
| Multi-language pipeline | Framework for generating same content in other languages (Japanese, Korean) using same content bank |

### North Star

A fully autonomous learning platform: RSS feeds → LLM curation → adaptive TTS generation → listener feedback → content optimization. Zero human intervention. $0/month. One engineer's personal AI tutor that gets smarter every day.
