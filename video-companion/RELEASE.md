# Release evidence

Verified requested URL: **https://video.mingli.world**. Existing podcast credentials are required. DNS alone was not treated as readiness: HTTPS, protected assets, existing-auth login and actual embedded playback were tested on that URL.

## Delivered architecture

Separate Cloudflare Pages project `video-mingli-world`, Pages Functions guarding all assets, separate private R2 bucket `video-mingli-world-state`, vanilla ES modules. No video downloads/rehosting, full transcripts, third-party app analytics, new credentials/grants, paid plan or podcast production/catalogue changes. Original footage streams directly from official YouTube embeds after user action.

Seven real playable source references, covering Jensen Huang, Alexandr Wang, Dario Amodei, Andrej Karpathy, Andrew Ng, Fei-Fei Li and Demis Hassabis. One 22-second complete paragraph is transcript-reviewed (Demis 53:06–53:28, primary Lex Fridman timestamped transcript). Six are honest 45-second anchor previews requiring further editorial boundary review. All 14 original analyses remain protected metadata; do not describe them as 14 videos or 14 reviewed clips.

Simple authentication delegates to the existing podcast endpoints, with a host-only opaque secure cookie. All paths are gated; auth outages fail closed. One private owner profile provides cross-device likes, collections, preferences, source position/watch metrics, completion and observed availability/quality. It does not create separate per-user identities. Browser caching is disclosed as a fallback, not account durability.

## Passed checks

- 11 model/auth/profile tests, including rejected stale writes and CDN weak-ETag regression.
- 14-analysis evidence/HTTPS validation; static-bundle credential/token scan.
- Authenticated local feed checks: like, save, named collection, exact return, reload, real touch gesture, skips/dwell, recommendation effect, source context, opt-out, 320/390/1440 layouts and no runtime errors.
- Requested-domain live checks: unauthenticated private assets/profile denied; existing-auth login; no-store responses; actual footage; player progress after reload and independent authenticated context; logout/relogin; next stops previous player; original-context link; mobile/desktop layout.
- Live source matrix: all seven sources played; each emitted quality `large` in this logged-out-provider headless session. This is observed provider output, not an HD guarantee.
- Actual UI likes, named collection and topic preference read from the private server by an independent login. Test-only preferences restored.
- Complete reviewed paragraph actually played and stopped at its transcript boundary.
- Provider unavailable-reference probe produced embed restriction code 150 and the explanatory source fallback, without persisting fake data or bypassing restrictions.
- Separate deployed touch check passed: native touch scroll 0→716, card 2/7. The earlier combined matrix's final swipe assertion failed after its unavailable-player probe; retain that evidence rather than hiding it. A cleaner combined rerun is recorded separately when completed.

The live test caught a real issue missed by fixtures: CDN compression produced weak HTTP ETags, which caused false conditional-write conflicts and prevented browser progress from syncing. Fixed using explicit profile-version headers plus legacy normalization, preserving real stale-write protection. Independent-session persistence then passed.

## Limits

Physical-phone testing, other regions/provider-login states and guaranteed HD are unrun. Six preview-only items still need coherent editorial ends. App login does not sign into YouTube. Source providers control restrictions/quality and can change availability. One owner profile is shared across authenticated devices; simultaneous stale edits are rejected with a visible reload prompt. Watch state is periodically saved; an abrupt close can lose the most recent seconds while local cache remains.

## Hosting, auth and rollback

Authoritative NS: dns17.hichina.com / dns18.hichina.com. Existing Aliyun owner route created only `video.mingli.world CNAME video-mingli-world.pages.dev`, TTL 600, record ID 2106158590498654208. Pages association and TLS are verified. The first CI DNS attempt wrongly assumed a Cloudflare zone; that was removed, with no added credential scopes.

CI runs and deployment commits are attached in release evidence. The podcast checkout's working files, original workflow, Pages project and R2 catalogue were not modified. An early accepted push targeted the local source clone's origin and created only an additive companion branch ref; origin was corrected to canonical GitHub before CI publication.

Rollback: use the companion Pages project's rollback to a prior **authenticated** deployment or publish a gated maintenance version through its isolated branch. Never disable middleware or roll back to public static hosting. Preserve the private R2 profile bucket. If removing the companion hostname is requested, the existing Aliyun owner helper can remove only the above newly created CNAME by its receipt ID; do not touch other records or the podcast project. No rollback has been performed.

Discovery remains manual. Newly created `world.mingli.video.refresh` on `agent` is unloaded and disabled across login; its plist and first successful 14-candidate run are preserved. No new recurring notifications/messaging, paid API or automatic production-feed publication exists.

## Final state and held candidate

Currently deployed commit: `72c22e534ae10cee02aeb3978840109dfc78f7cd`; successful CI https://github.com/daxia07/podcast-mingli-world/actions/runs/37076409183.

The combined source matrix again retained its final swipe failure after an unavailable probe on the final card and a Discover reset. It is not reported as a full matrix pass. The specific resilience requirement was then verified in the SAME live session: provider error 150 → accessible Next → card 2/7 → native touch swipe → card 3/7, scroll 0→716→1432, without reload/context reset, with original context still available. See `live-error-recovery.json` and screenshots. All seven real source playback checks, reviewed-boundary stop and independent UI state persistence passed.

Automatic review rejected the last combined check/copy/commit/push command before execution, citing the stale AGENTS deployment block and absence of approval despite the explicit human approval relayed earlier. No retry or workaround followed. Exact command arguments/reason are in `evidence/final-approval-rejection.json`. This holds only the later local replay/status/reset refinements and final docs; the tested authenticated video release above remains live. A separate progress-message action was also rejected under the no-user-facing-updates instruction; final task delivery is the supported parent notification.

## Integrated phone/recency candidate — not published

See RECENCY-REVIEW.md. Four reviewed fresh ideas from three official videos were added locally; original dates are explicit. All four played and stopped at reviewed boundaries in the isolated phone fixture. Source/profile Functions and binding remain unchanged. Source-date/ranking tests, migration/collection-return acceptance, phone layouts and retained interaction checks are recorded in evidence. The source matrix after edition integration exposed a navigation reset bug: CSS smooth scrolling continued while rebuilding an edition, so Next could skip ahead. An explicit instant scroll reset plus observation of current geometry fixed it; same-session provider-error recovery passed afterward. The proposal replaces conditional provisioning CI steps with read-only existing-resource preflight; it has not been pushed or run.
