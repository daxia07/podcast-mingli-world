# Video · Mingli

Currently deployed: https://video.mingli.world — sign in with the existing podcast account. The phone/recency candidate below is isolated and unpublished.

A private mobile-first swipe feed of seven official YouTube sources from influential AI leaders, with original analysis. Footage remains on YouTube. The app hosts metadata and analysis, and stores a single private owner's progress/preferences in a separate R2 bucket. It follows the podcast's vanilla ES module + Cloudflare Pages architecture; podcast files/runtime/catalogue are unchanged.

The first fresh-profile idea is a complete transcript-reviewed Demis Hassabis paragraph at 53:06–53:28. Six other playable items are clearly labeled 45-second previews from evidenced chapter/transcript anchors; those ends are reader preview limits, not reviewed excerpt boundaries. Original source/context links, publication/date type, speaker role, evidence limits, commercial context, editorial interpretations and practical experiments are visible. All 14 original editorial analyses remain in protected metadata; seven have verified playable source references and appear in the video feed.

## Authentication and private state

Server middleware delegates to the podcast's existing HTTPS login/session endpoints. Owner credentials and signing secrets are not copied into this app or its static bundles. The companion stores an opaque host-only HttpOnly/Secure cookie and protects every static asset and profile endpoint. Auth fails closed when the upstream is unavailable. Sign-out clears only the companion cookie, preserving podcast sessions; the upstream scheme is stateless, without separate device/session identities.

Likes, named collections, topics, skips/dwell, actual player position/watch time, preview completion, source availability/errors and supported quality events sync to a private owner profile in `video-mingli-world-state`. This is one owner, not a multi-user account system. Browser storage is a local fallback/cache; Preferences displays sync state. The last card and source position resume across authenticated devices. Conflicting stale writes are rejected rather than silently overwriting another device. A dedicated profile version header avoids CDN compression changing HTTP ETags. Export/reset are available in Preferences.

Recommendations emphasize editorial usefulness, novelty, credibility, relevance and influence. Explicit feedback outweighs bounded reading/watch signals. Background/unfocused reading, dialogs, paused measurement and inactivity beyond 45 seconds do not add dwell. Raw views are not a ranking input.

## Official playback

The YouTube privacy-enhanced player loads only after Play. Its controls remain unobstructed; swipe beside the player or use next/previous buttons. Only one player exists at a time; it pauses when hidden or less than half visible. Reviewed boundaries and preview limits are guarded while restoring source position. Availability starts unknown and is updated by real player events. Errors and provider restrictions are explained with original-source access; they are not bypassed.

Only the supported playback-quality-change event is recorded. No HD guarantee, unsupported quality getter/setter or forced-quality picker is used. YouTube controls region, age, source-account login, quality and embedding availability, and receives requests when you choose playback. The app has no third-party analytics or public interaction feed.

## Run and verify

- `npm test`: model, authentication and private-profile tests.
- `npm run validate`: 14 IDs, evidence fields and HTTPS source checks.
- `npm run dev`: local static UI demonstration only; does not reproduce production authentication/storage.
- `node scripts/test-server.mjs`: isolated authenticated local fixture on localhost:4174, with test-only credentials and in-memory profile storage.
- `TEST_BASE=http://localhost:4174 TEST_AUTH_FIXTURE=1 node scripts/browser-test.mjs`: mobile feed regression using installed headless Chrome/Playwright on this Mac.
- Live acceptance scripts use the existing original auth source only in memory; never output credentials/tokens. `verify-live.mjs` is read-only when a profile exists. Browser/matrix results and screenshots are in `evidence/`.

## Release and discovery

Source: this workspace. Release repository: `deployment-ci/`, canonical origin https://github.com/daxia07/podcast-mingli-world.git, isolated branch `video-companion-release`. CI touches only the new companion and its workflow. It uses the existing CI token without new grants/credentials or a paid plan. A separate Pages project and private R2 bucket serve this app. Aliyun/HiChina is the domain's authoritative DNS provider; the existing owner helper created only the requested CNAME to video-mingli-world.pages.dev. Cloudflare Pages association/TLS and real HTTPS access are verified.

`python3 scripts/refresh.py` remains available manually. It discovers candidates from official NVIDIA/TED feeds without a key and never auto-publishes claims. Its newly created recurring LaunchAgent on `agent` is unloaded and disabled, with configuration and first-run evidence preserved. Publication does not reenable it.

## Held phone + recency candidate (October 3)

The live seven-item seed has no source from the last 30 days. Its displayed dates are 66–472 days old; one is a transcript publication rather than a verified original-video date. Editorial ingestion on October 2 did not make those sources fresh.

The candidate has four reviewed fresh ideas from three official video sources: Sam Altman at DevDay (September 29 original event; upload date unknown), Noam Brown (September 17 original episode publication), and John Schulman/Beren Millidge (September 11 original panel publication). Dates and age are visible on the phone. The 30-day Fresh edition gives strongest priority to the last seven days, with usefulness/credibility gates and bounded feedback. Recent (90 days), Evergreen (older) and unknown-original-date editions are separate. Crawl/review/repost dates cannot reset age; uncompleted events do not qualify. Existing state/IDs are retained; saved archive items still return exactly.

One snap stage occupies each ordinary portrait dynamic viewport, with large official player, thumb controls and expandable gist/source details. The source controls stay unobstructed. Horizontal talks remain letterboxed. Playback starts after Play; mobile/provider autoplay limits still apply. Physical-phone/Safari/safe-area rendering remains unverified. See PHONE-REVIEW.md and RECENCY-REVIEW.md for evidence and the concrete deploy-only approval plan.
