# Release status — 2026-10-02

## Implemented and checked locally

Isolated static companion in `site/`, using inspected podcast architecture: vanilla ES modules and Cloudflare Pages, no build step. 14 original source-backed summary cards include 2026 sources and historical context. Explicit provenance, date type, role at event, evidence limits, commercial context, interpretations, conditional outlooks and practical experiments are visible in Source & context.

Likes, named collections, exact-card return, reload persistence, topic choices, skips and bounded foreground dwell personalize recommendations. State stays in this browser, with export/reset and clear disclosure of no account sync. No third-party analytics or public interaction API exists.

Unit/model checks: five passed. Content validation: 14 IDs, complete provenance, HTTPS links. Headless Chrome tests cover mobile feed, like/save, named collections, return, reload, source context, gesture/navigation, skips/dwell, topic and dwell controls, and 320/390/1440 layouts. See `evidence/browser-results.json` and screenshots. This is emulated-browser testing; no physical phone or external video playback has been tested.

Review loops fixed small-screen content clipping, an upcoming-queue recommendation bug that excluded feedback on already-viewed cards, and idle-time measurement. Small-height cards grow vertically so all controls remain reachable; there is no horizontal overflow. Dwell pauses for dialogs, background/unfocused tabs and idle periods beyond 45 seconds.

## Manual discovery; recurring configuration paused

On `agent`, `/Users/ding/projects/video-mingli-world/scripts/refresh.py` is available manually. The newly created LaunchAgent `world.mingli.video.refresh` is unloaded and disabled pending scope approval; its preserved configuration specifies run-at-load and every 86400 seconds. The first run returned exit 0 with both official feeds successful and 14 editorial candidates. It writes private candidate/status files in the companion directory. It does not auto-author or publish claims. The website feed remains the reviewed curated edition until a source-backed editorial update is deployed.

## Deployment blocker and approval required

No live companion URL exists yet. The requested destination is **https://video.mingli.world**; it must not be presented as live.

Existing host Pages CLI can list projects but cannot create/deploy without `CLOUDFLARE_API_TOKEN` in the non-interactive environment. This Mac’s GitHub authorization is valid when network access is granted, and the existing `daxia07/podcast-mingli-world` CI has the `CLOUDFLARE_API_TOKEN` secret. Secret values were never copied or exposed.

A concrete proposed CI release is staged in `deployment-ci/` on local branch `video-companion-release`. It only adds `video-companion/` and `.github/workflows/video-companion.yml`; existing podcast files are unchanged. The companion workflow creates a separate Pages project, deploys only companion static assets, then requests association of `video.mingli.world` and creates only that CNAME if absent. It stops if an incompatible record exists. It does not touch podcast R2, its Pages project, master branch or workflow. Whether the existing token has DNS scope is still unknown.

**Automatic approval review rejected the push**: “Pushing this branch modifies the existing podcast repository and triggers a privileged CI workflow that can create Cloudflare resources and DNS records; that conflicts with the explicit instruction not to alter the existing podcast and exceeds authorization for deployment.” No push, CI run, Pages creation or DNS write occurred. The concrete next approval is permission to push this additive isolated branch and run this companion-only workflow using the existing CI secret, including only the requested hostname’s domain association/CNAME. Alternatively, an explicitly authorized separate existing credential route is needed. No new paid service, credential, permission change or unrelated infrastructure is proposed.

Earlier automatic review also rejected broad deployment-host credential/config inspection as a potential secret exposure, and rejected a progress message to the parent thread because the delegated request prohibited user-facing updates. Both actions were stopped; no workaround was attempted. The normal final-task result can notify the parent.

## Delivery locations

- Local source: `/Users/daxia/Documents/Codex/2026-10-02/task-5`
- Static deploy directory: `site/`
- Remote isolated companion: `agent:/Users/ding/projects/video-mingli-world`
- Proposed release: `deployment-ci/`, local branch `video-companion-release`
- Evidence: `evidence/`

## Updated authorized scope

The user explicitly approved the companion-only CI/hosting/DNS release, with matching simple authentication, playable video and persisted metrics/progress. This supersedes the earlier missing-authorization blocker for one retry of the same push; it does not reenable discovery. Implementation now includes seven official YouTube preview players and a private server-backed owner profile in a separate R2 bucket. All assets/profile endpoints are gated. Auth calls only the podcast’s existing HTTPS login/session routes and does not copy its credential constants or secret into the companion.

Local checks after changes: 11 model/auth/profile tests, 14-card metadata validation, credential-literal/static-bundle scan and all feed acceptance interactions behind authenticated fixture passed. Live acceptance and external player checks are required after deployment; none should be inferred from fixture success. Any initial source-inspection redaction limitations are not a basis for claiming credentials were never displayed; current bundle/config/log checks avoid printing credential or token values.
