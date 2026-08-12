# Agentic AI — Following the Money: source notes

Reference material behind the three episodes, with the figures actually used and
where they came from. Kept separately because these numbers date fast: treat
anything here as of **August 2026** and re-check before reusing it.

## The framing

This show is **education, not investment advice**. No securities are named as
buys or sells, no prices are predicted, and nothing here is a recommendation
about what to do with money. The goal is that you can read the next headline and
judge it yourself. Where credible sources disagree, the episodes say so rather
than picking the convenient number.

## Figures used

| Figure | Value | Source |
|---|---|---|
| Agentic AI market size, 2026 | ~$7–11B, definition-dependent | [State of AI Agents 2026](https://www.digitalapplied.com/blog/state-of-ai-agents-2026-200-data-points), [Keyhole](https://keyholesoftware.com/enterprise-agentic-ai-market-2026/) |
| Agentic VC funding, 2025 | $6.42B | [AgentMarketCap](https://agentmarketcap.ai/blog/2026/04/08/agentic-ai-funding-velocity-2026-sector-map-vertical-distribution) |
| Agentic VC funding, 2026 to April | $2.66B across 44 rounds | AgentMarketCap |
| Average round size | $155M (Q4 25–Q1 26) vs $82M (H1 25) | AgentMarketCap |
| Enterprise apps with agents by end 2026 | 40%, from <5% in 2025 | Gartner, via [Barchart](https://www.barchart.com/story/news/1204699/belitsoft-releases-ai-agent-development-forecast-2026-40-of-enterprise-applications-to-include-task-specific-agents-by-year-end) |
| Adoption vs production | ~4 in 5 adopted; ~1 in 9 in production | State of AI Agents 2026 |
| Hyperscaler capex 2026 | ~$805B (Morgan Stanley), from $261B in 2024 | [AL Capital](https://alcapitaladvisory.com/research/intelligence/ai-infrastructure.html) |
| Understated depreciation 2026–28 | ~$176B | [Silicon Analysts](https://siliconanalysts.com/analysis/hyperscaler-ai-capex-depreciation-wall-2026) |
| Signed-not-commenced leases | ~$662B (Moody's, early 2026) | Silicon Analysts |
| Productivity gains | +14–15% support, +26% software dev | Stanford HAI meta-analysis, April 2026 |
| Anthropic ARR / valuation | ~$14B ARR; $380B post-money Series G | State of AI Agents 2026 |
| Salesforce Agentforce ARR | ~$800M, +169% YoY | Salesforce FY2026 updates, via State of AI Agents 2026 |

## Where the sources disagree

- **Market size** is the least reliable figure in the whole space. Estimates for
  2030 range from roughly $24B (enterprise-only) to $52B (all agents) to $183B
  (broadest definition). The spread is definitional, not empirical.
- **Depreciation** is genuinely contested, not settled. The bear argument is a
  2–3 year economic life; the counter is that older accelerators cascade down to
  inference and cheaper tiers rather than being retired.

## Threads worth following

Not yet covered, and each could be its own episode:

- **Agent runtime as a procurement category** — Bedrock AgentCore, Foundry, Vertex.
  If enterprises start evaluating this the way they evaluate databases, that
  layer has become durable. [TGVP report](https://www.tgvp.vc/releases/tgvp-report-ai-agent-infrastructure-in-2026)
- **The orchestration-framework question** — widely used, mostly open source,
  unresolved whether that converts to revenue or gets absorbed by the clouds.
- **Evaluation and observability** as a category. If agents go to production,
  someone has to prove they work; that is a market with no clear winner yet.
- **The energy constraint.** Capex assumes power that in several regions is not
  contracted yet.
- **Circular revenue disclosure.** Watch the related-party share, not the anecdote.

## Suggested further listening and reading

Deliberately picked for disagreement rather than agreement:

- Goldman Sachs' Jim Covello — the most rigorous public sceptic on whether the
  spend can be justified.
- [Moody's / Silicon Analysts on the depreciation wall](https://siliconanalysts.com/analysis/hyperscaler-ai-capex-depreciation-wall-2026) — the bear case in accounting terms.
- [Valtorian on AI moats](https://www.valtorian.com/blog/ai-moats-2026) and
  [the SaaS moat question](https://bigideasdb.com/saas-moat-ai-era-2026) — the defensibility argument.
- Stanford HAI's AI Index — the least promotional source of productivity data.

If you want any of these turned into episodes, `/ingest <url>` runs the
youtube-ingest skill, and the same distil-then-rewrite path works for articles.
