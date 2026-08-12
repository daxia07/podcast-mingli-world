# Reading Codex — teardown notes

Companion to the **Building Agentic Systems** series. Everything here was read
from the [OpenAI Codex CLI source](https://github.com/openai/codex) (Apache-2.0)
at commit `9ca0337`, August 2026. Paths are given here rather than spoken in the
episodes, because file paths make terrible audio.

To follow along:

```bash
git clone --depth 1 https://github.com/openai/codex.git
cd codex/codex-rs
```

## Scale, for calibration

| Crate | Rust lines | What it is |
|---|---|---|
| `core` | ~315,000 | the agent: turns, tools, safety, context, state |
| `tui` | ~247,000 | terminal interface |
| `app-server` | ~135,000 | the API surface other clients drive |
| `windows-sandbox-rs` | ~19,200 | sandboxing, one platform |
| `protocol` | ~23,500 | wire types |

The "agent loop" as usually taught is a rounding error against this. That is the
first lesson of the series.

## Episode 1 — the shape of a turn

- `core/src/session/turn.rs` (~2,760 lines). Read the function names top to
  bottom for the phase sequence: `capture_step_context` → `build_world_state` →
  `run_pre_sampling_compact` → `run_sampling_request` → streaming parsers →
  `drain_in_flight`.
- `CancellationToken` is threaded throughout rather than checked at the top.
- `core/src/tools/parallel.rs` — concurrent tool calls with `AbortOnDropHandle`
  and per-call timing guards.

## Episode 2 — tools are an interface

- `core/src/tools/handlers/` — note the `*_spec.rs` / `*.rs` pairs.
  `plan_spec.rs` is 58 lines against `plan.rs` at 105; `shell_spec.rs` is 414
  against `shell.rs` at 256.
- `get_context_remaining_spec.rs` is the clearest short example: name,
  description, parameter schema, **and an output schema**.
- `core/src/tools/registry.rs` — `register_trusted` vs `register_external`, and
  `first_collision` tracking so a late registration can't silently shadow a
  built-in.
- `defer_loading` on `ToolSpec`, plus `handlers/tool_search.rs` — the answer to
  schema bloat once you have many tools.
- Tools that hand control back: `request_user_input`, `request_permissions`,
  `request_plugin_install`.

## Episode 3 — permission is the product

- `core/src/safety.rs` — `SafetyCheck::{AutoApprove, AskUser, Reject { reason }}`.
  Three values, and the reason is returned to the model.
- `AskForApproval::{Never, OnRequest, UnlessTrusted, Granular(..)}` — user
  preference, kept independent of the per-action assessment.
- **The hardlink comment**, the single most instructive thing I found:

  > "Even though the patch appears to be constrained to writable paths, it is
  > possible that paths in the patch are hard links to files outside the
  > writable roots, so we should still run `apply_patch` in a sandbox in that case."

  Policy reasons about strings; the kernel enforces on inodes. They fail
  differently, which is exactly why you want both.
- `sandboxing/` (Landlock, bubblewrap), `linux-sandbox/`, `windows-sandbox-rs/`,
  `core/src/exec_policy.rs`. Note how much of the repo is this.
- The assessment functions are pure — action and policy in, verdict out — which
  is why `safety_tests.rs` and `exec_policy_tests.rs` can be thousands of lines.

## Episode 4 — context is a budget

- Roughly ten `compact*` modules in `core/src/`: `compact.rs`,
  `compact_token_budget.rs`, `compact_remote.rs`, `compact_remote_v2.rs`,
  `compact_model_fallback.rs` and their tests.
- `core/src/context_manager/` — `history.rs`, `normalize.rs`, `updates.rs`.
- `CompactionTrigger::{Manual, ...}` — triggers are distinguished in analytics.
- `run_pre_sampling_compact` runs *before* the model call, on the happy path.
- Pre- and post-compact hooks: `hook_runtime.rs`.
- Token-budget compaction skips summarisation entirely and installs a fresh
  window, but is still modelled as compaction so hooks and turn items see one
  lifecycle. The comment saying so is in `compact_token_budget.rs`.
- `handlers/get_context_remaining.rs` — the model can ask how much room is left.

## Things worth a future episode

- `core/src/agent/` and `handlers/multi_agents*` — delegation to sub-agents.
- `core/src/guardian/` — a subsystem I did not read; the tests alone are 3,500 lines.
- `rmcp-client`, `codex-mcp`, `mcp-server` — three crates for Model Context
  Protocol, in three different roles.
- `core/src/rollout.rs` and `thread-store` — how a session is persisted and
  reconstructed, which is what makes resume work.
- `exec-server` and `code-mode` — running model-authored code rather than tool calls.

## Honest limits

I read structure, signatures, comments and tests. I did not run it, did not read
the 315,000 lines, and deliberately described mechanisms rather than reproducing
source. Where the episodes state a line count or a type name it was checked;
where they explain *why*, that is my reading of the design and you should treat
it as an argument rather than as the authors' stated intent.
