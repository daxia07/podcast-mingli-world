# Integrated phone + recency candidate — held for publication approval

Read-only audit of https://video.mingli.world on October 3: seven live source dates are 66–472 days old; six represent original event/publication dates and one is only a publisher transcript date. No live video qualifies for a 30-day fresh window. The October 2 editorial update is not source freshness. Live ranking did not use age. See `evidence/recency-live-audit.json`.

## Default and evidence rules

Fresh contains verified original sources from the last 30 days, with strongest priority to the last seven. Credibility/usefulness must each reach 3/5; explicit Less feedback excludes a card from the edition. Within freshness groups, age reduces score and existing quality, novelty and bounded explicit/dwell signals still matter. Raw views are not used. Recent includes the last 90 days. Evergreen is older than 90 days; unknown original dates are a separate edition. If Fresh is empty, say so and offer the archive rather than relabeling it.

Source age uses the original verified event or original episode/video publication date, never ingestion, transcript update, review, repost or crawl date. Event dates require completed events. Known event dates and unknown upload dates remain distinct. Every phone card shows its source date basis and age; Source & context explains date type/evidence. Source publication dates do not claim to be recording dates. Existing original IDs, likes, topics, collections, progress and playback remain; v1 profiles default to Fresh without deletion. An explicitly opened saved archive returns exactly and is labeled as archive; Discover returns to the selected edition.

## Reviewed fresh playable batch

| Speaker / idea | Original source date | Reviewed source interval | Evidence |
|---|---|---|---|
| Sam Altman / build where users work | September 29 event, 4 days old; YouTube publication unknown | 00:50–01:18, 28s | [Official recap](https://openai.com/index/devday-2026-recap/), [official OpenAI video](https://www.youtube.com/watch?v=Fls_onRviPM&t=50s) |
| Noam Brown / latency trade-offs | September 17 episode publication, 16 days old | 01:26–02:08, 42s | [Publisher transcript/date](https://www.dwarkesh.com/p/noam-brown), [official video](https://www.youtube.com/watch?v=6AgOfiZOWiY&t=86s) |
| John Schulman / judgment bottlenecks | September 11 panel publication, 22 days old | 01:48–02:53, 65s | [Publisher transcript/date](https://www.dwarkesh.com/p/john-beren-charlie), [official video](https://www.youtube.com/watch?v=PrSf7IOYu-I&t=108s) |
| Beren Millidge / conditional generalization gap | Same September 11 panel, 22 days old | 01:00–01:48, 48s | Same original panel; qualification that the scenario is unlikely is preserved |

Four ideas, three original videos, 18 total editorial analyses and 11 playable references. The four fresh ideas cover complete content units checked through bounded official captions and publisher evidence; chapter markers were not used as reviewed ends. Seeks/captions remain approximate. Commercial context and our interpretation/experiment are separate. All footage stays with the official source. No full talk or transcript was downloaded/rehosted.

WIRED Timnit Gebru’s September 30 video release is verified, but provider embed and short boundaries remain unverified. Fresh CBS Jensen Huang/Dario Amodei and RSA Demis Hassabis leads remain outside the playable batch until exact source/date/range checks complete. No recent Wang source was verified. An OpenCV event announcement alone does not establish completed footage. Discovery remains manual and its recurring LaunchAgent remains disabled.

## Acceptance and retained limitations

`npm test`: 16 passing tests; `npm run validate`: 18 analyses; bundle scan passed. Recency tests cover original dates, invalid/future/missing dates, uncompleted events, no recrawl freshness, archive separation, feedback and old-profile preservation. `recency-browser-results.json` verifies the default, visible dates, exact saved archive return, edition changes and honest empty Fresh state.

`fresh-playback-results.json`: all four fresh ideas actually played on the isolated 390px phone candidate and stopped at reviewed ends (78, 128, 173, 108 seconds). All reported quality `large`; no HD guarantee. `phone-acceptance.json` covers portrait stage/player/action dimensions, expandable gist and recommendation explanation, actual playback, dynamic height contraction, native swipe stopping prior playback, keyboard/Previous and same-session provider error → Next → swipe. Retained evergreen interaction regression results are in `browser-results.json`. Screenshots at 320px, 390px and desktop were manually reviewed.

Edition rebuilding exposed a navigation reset regression: assigning scrollTop with CSS smooth scrolling could continue an earlier movement, causing Next to skip. The candidate now resets scroll instantly and observes live geometry rather than stale intersection entries. Final acceptance includes this path. Earlier failed runs are not claimed as passed.

Physical phones/Safari/toolbars/notches, zoomed text, other provider regions/login states and HD remain untested. Very short landscape windows need a scrolling fallback. Private state remains one owner profile; concurrent stale edits still need reload. No live profile was modified by this audit; tests used localhost or intercepted profile requests.

## Exact proposed publication scope

Companion changes: `site/app.js`, `site/style.css`, `site/content.json`, `site/js/model.js`, `site/js/player.js`; acceptance/validation/preflight scripts and tests; README/RELEASE/PHONE-REVIEW/this review. Previously held replay/reset/error/quality timestamps are explicitly included. Auth/profile Functions and `wrangler.toml` remain unchanged.

CI replacement is reviewable in `release-plan/video-companion.yml`: remove resource provisioning and domain-association writes, GET-check existing companion Pages project/R2 bucket/domain, fail if missing, then deploy and verify only the existing companion. No new infrastructure, DNS, grants, credentials, service purchases, recurring discovery, podcast runtime/episode changes or production-branch push. Preflight is mocked/tested, not executed against Cloudflare.

No push/retry occurred. Live stays at 72c22e534ae10cee02aeb3978840109dfc78f7cd, and release clone remains clean. An approved release must start from fresh canonical state preserving podcast commit b05436c32f41f41fbdb1327ff148bff856f2f219 and any newer changes. Approval is needed for this concrete companion-only patch and deploy-only CI update on `video-companion-release`. The earlier automatic review rejection remains in `evidence/final-approval-rejection.json`; do not use an alternative upload/workflow to bypass it.
