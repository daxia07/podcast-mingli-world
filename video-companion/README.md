# Video · Mingli

A mobile-first vertical feed of short, original AI idea summaries. The companion follows the podcast’s vanilla JavaScript / Cloudflare Pages architecture and does not change its runtime, R2 contents or source checkout.

14 reviewed cards cover Jensen Huang, Alexandr Wang, Dario Amodei, Andrej Karpathy, Andrew Ng, Fei-Fei Li and Demis Hassabis. Current 2026 sources are mixed with dated historical context. Cards paraphrase inspected publisher evidence; they do not impersonate speakers, host video or reproduce full transcripts. Source dialogs label the evidence limits and open official videos or publishers. Chapter links are not verified clip boundaries. External video playback has not been tested.

## Use and verify

- `npm run dev` serves `site/` at http://localhost:4173.
- `npm test` runs five model tests.
- `npm run validate` checks unique IDs, provenance and HTTPS URLs.
- `node scripts/browser-test.mjs` uses the installed headless Chrome and bundled Playwright runtime on this Mac. Evidence goes to `evidence/`.
- `python3 scripts/refresh.py` discovers review candidates from NVIDIA and TED’s official feeds with no key. It never auto-publishes new factual claims.

Swipe/scroll vertically, use arrow keys or next/previous buttons. Like or select “Less like this”; save to Read later or create named collections. Collections return to the exact idea. Preferences, saved cards, reading time and skips use this browser’s localStorage. There is no account or cross-device sync. Storage failures show a session-only notice. Export and reset are available in Preferences.

Ranking uses editorial usefulness, novelty, credibility and influence, plus bounded explicit topic/like/save/less feedback and a small capped active-reading signal. Rapid skips reduce topic preference. Hidden/unfocused tabs, dialogs, paused measurement and time beyond 45 seconds without interaction do not accrue dwell. Explicit feedback is stronger than dwell. New Discover sessions and the next button reorder upcoming ideas; swiping keeps the session stable to avoid jumping cards under a reader.

## Infrastructure and refresh

Remote companion: `/Users/ding/projects/video-mingli-world` on `agent`.
A dedicated `world.mingli.video.refresh` LaunchAgent configuration is preserved on that host but is unloaded and disabled pending scope approval. Its configured cadence is run-at-load and every 86400 seconds. Manual discovery remains available and writes private editorial candidate/status files to `data/`. No listener data or credentials are used. Failures preserve the last successful queue. Humans/agents must verify speaker, source, date and gist before editing `site/content.json` and deploying.

Static hosting needs only `site/`. `wrangler.toml` targets a separate `video-mingli-world` Pages project. There is no service worker, avoiding stale personal-state shells. Hosting headers disable third-party requests, frame embedding of this site, camera, microphone and geolocation. External source links open only after user action.

The proposed release checkout in `deployment-ci/` is an isolated branch of the existing repository. It adds only a companion folder and a companion-only CI workflow, preserving existing files. Its push is blocked pending approval; see RELEASE.md. The original podcast checkout has not been edited.

Design used the frontend-design skill: quiet navy/cool-blue reader, Avenir/system type, speaker monograms rather than invented portraits, and a full-screen idea as the opening experience. Local environment and podcast ingestion guidance informed the architecture and rights limits.

## Authenticated video release

The updated release presents seven verified-source YouTube embeds, loaded only after Play; all 14 editorial analyses remain in the protected metadata archive. Each player previews 45 seconds from an evidenced publisher chapter/transcript anchor. That end is an app preview limit, not a reviewed excerpt boundary. Footage stays on YouTube; there are no downloaded/rehosted talks.

Server-side middleware delegates sign-in and session validation to the podcast’s existing supported HTTPS endpoints. It stores only an opaque host-only HttpOnly/Secure companion cookie, blocks every feed asset before authentication, and fails closed when upstream auth is unavailable. No signing secret or owner credential is embedded in this app. This creates a dependency on podcast authentication availability; companion logout clears the companion cookie without changing podcast sessions.

A separate private `video-mingli-world-state` R2 bucket stores one owner profile behind the same middleware: likes, collections, topic preferences, card dwell/skips, actual player position/watch seconds, preview completion, observed source quality events and availability/error state. An ETag guard rejects concurrent stale writes. Browser storage is a fallback, not cross-device durability. Sync status is displayed in Preferences. This simple authentication identifies a single owner, not separate users.

YouTube controls provider login, region, age, embed permission and quality. Availability begins unknown. Successful playback or a player error updates observed state. Only supported playback-quality events are recorded; no forced HD or unsupported quality picker is used. The player contacts YouTube when requested and pauses when hidden or less than half visible. Controls remain outside the iframe. The discovery schedule stays disabled.
