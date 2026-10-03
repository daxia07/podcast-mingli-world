# Phone feed review — isolated candidate, not published

Audited live release 72c22e534ae10cee02aeb3978840109dfc78f7cd at https://video.mingli.world on the connected MacBook using headless Chrome. No native foreground browser or executor switch. Live profile requests were intercepted locally: no owner state changes.

The live layout has a real short-phone defect. At 320×568 its card is 713px tall inside a 440px feed; Like/Save end at y635 and source detail at y685, below the visible feed. At 390×664 a 677px card exceeds the 536px feed. Height-based CSS also weakens mandatory snapping. The earlier no-card-overflow check passed because the card grew, rather than checking one card equals one viewport.

The local candidate uses one mandatory snap stage per dynamic viewport at ordinary portrait phone sizes. A large official player stays unobstructed, the concise gist expands through Full gist & source, and Like/Save stay near the bottom with 44–48px targets. Compact chrome, two-line title/gist, safe-area CSS, viewport resizing, source-context and recommendation explanations are preserved. Native swipe happens beside the iframe; source controls receive their own gestures. Play remains an explicit user action because provider/mobile autoplay restrictions apply. Horizontal source footage remains letterboxed rather than cropped or stretched to imitate vertical footage.

Extremely short landscape windows below 500px height retain a scrolling fallback: a compliant minimum 200×200 provider player plus accessible controls cannot fit one stage. Physical devices, real notched safe-area rendering, Safari/browser toolbar behavior, zoomed text and other provider regions remain unverified. No guaranteed quality or autoplay claim.

## Evidence

- `phone-live-before.json` and screenshots: live geometry defect.
- `phone-candidate.json` and screenshots: 320×568, 390×844, 390×664, 1440×900, manually reviewed.
- `phone-acceptance.json`: all fresh stages fit at 320×568, 390×844, 390×664 and 320×520; accessible target/player dimensions, expanded source gist, actual official playback, source-error recovery, dynamic viewport contraction, native touch and keyboard controls.
- `browser-results.json`: existing 13 acceptance checks passed (like/save/named collection/exact return/reload/source context/native swipe/dwell/skips/topic opt-out/mobile/desktop/no errors).
- `npm test`: 16 passing tests; metadata validation: 14; private bundle scan passed.

## Concrete proposed release — approval required

No rejected push has been retried. Release checkout remains clean at 72c22e5. Build any approved release from fresh canonical repository state containing podcast commit b05436c32f41f41fbdb1327ff148bff856f2f219; do not push or reset the podcast production branch. Preserve current podcast episode catalogue, auth Functions, deployments and unrelated changes.

Proposed patch paths: `video-companion/site/app.js`, `site/style.css`, `site/content.json`, `site/js/model.js`, `site/js/player.js`; local-only test helpers and acceptance scripts, `scripts/preflight-existing.mjs`, its test and companion review documentation; and `.github/workflows/video-companion.yml` using the exact reviewed replacement in `release-plan/video-companion.yml`. Existing held replay/reset/error/quality-timestamp refinements are included explicitly. The integrated release also updates source metadata and ranking as documented in RECENCY-REVIEW.md; auth/profile Functions and R2 bindings remain unchanged.

The proposed workflow removes both provisioning steps. Its preflight performs GET requests only for the existing companion Pages project, private state bucket and domain association. If any is absent, fail without creating it. It then deploys only `video-mingli-world` using the existing credential and verifies protected endpoints. No resource creation, DNS changes, grants/new credentials, purchases, discovery enabling, podcast deployment or master push. The proposal has been tested with mocked existing/missing resources, but has NOT been run against infrastructure or installed in the release checkout.

Approval requested for pushing this concrete companion-only patch and deploy-only workflow to `video-companion-release`, allowing the existing CI credential to update the existing companion Pages deployment. Re-read current repository instructions and resolve conflicts on the fresh base before execution. If automatic review rejects again, stop; no alternate upload or workflow.
