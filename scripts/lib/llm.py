#!/usr/bin/env python3
"""llm.py — LLM access for the podcast pipeline.

Follows the credential convention already used across these projects
(`convfinqa-agent/src/convfinqa/llm.py`, `job-hunter`, `ai-feeds`): the key is
resolved at call time from the environment, then from `pass`. Nothing is stored
beside the code, and no key needs to exist for the pipeline to run — callers
catch `LlmUnavailable` and fall back to the deterministic template path
(docs/UPGRADE-SPEC.md §0 D1).

Resolution order, matching the house convention:

    LLM_API_KEY -> DEEPSEEK_API_KEY -> OPENAI_API_KEY
      -> `pass show $LLM_PASS_ENTRY`            (default: deepseek/api_key)
      -> `ssh $LLM_PASS_SSH_HOST pass show ...` (only if LLM_PASS_SSH_HOST set)

Endpoint and model follow `LLM_ENDPOINT` / `LLM_MODEL`, the same variables
generic-tutor and convfinqa use, so one exported pair configures everything.

Two roles, because the jobs differ: `writer` produces episode prose and wants
the best model available; `distiller` turns 30-minute YouTube transcripts into
study blueprints and wants cheap tokens and long context. Both default to the
same DeepSeek model; override per role when a better writer is worth paying for.

Diagnostics that never print a secret:

    python3 -m scripts.lib.llm --check
    python3 -m scripts.lib.llm --role writer --say "Say hello in five words."
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_PASS_ENTRY = "deepseek/api_key"

# Per-role model overrides. Both fall back to LLM_MODEL, so a single-key,
# single-model setup works with no extra configuration.
ROLE_ENV = {
    "writer": "PODCAST_WRITER_MODEL",
    "distiller": "PODCAST_DISTILLER_MODEL",
}


class LlmError(RuntimeError):
    """A call was attempted and failed."""


class LlmUnavailable(LlmError):
    """No key is configured. Callers must fall back to templates."""


# ---------------------------------------------------------------------------
# Key resolution — origins are safe to print, values never are.
# ---------------------------------------------------------------------------


def resolve_api_key() -> tuple[str, str] | None:
    """Return (key, origin) or None. `origin` is safe to log."""
    for var in ("LLM_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"):
        value = os.environ.get(var, "").strip()
        if value:
            return value, f"env:{var}"

    entry = os.environ.get("LLM_PASS_ENTRY", DEFAULT_PASS_ENTRY)

    local = _first_line(["pass", "show", entry], timeout=10)
    if local:
        return local, f"pass:{entry}"

    # The password store lives on another machine in some setups; the podcast
    # repo's own data/ symlink points at one (see AGENTS.md gotcha #1).
    host = os.environ.get("LLM_PASS_SSH_HOST", "").strip()
    if host:
        remote = _first_line(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8", host, "pass", "show", entry],
            timeout=30,
        )
        if remote:
            return remote, f"ssh:{host}:{entry}"

    return None


def _first_line(cmd: list[str], timeout: int) -> str | None:
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=True
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.split("\n", 1)[0].strip() or None


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


@dataclass
class Model:
    """A chat endpoint plus the settings a run needs to hold fixed."""

    role: str = "writer"
    model: str | None = None
    base_url: str = os.environ.get("LLM_ENDPOINT", DEFAULT_BASE_URL)
    temperature: float = 0.7
    max_tokens: int = 8000
    max_retries: int = 3
    api_key: str | None = None
    key_origin: str | None = None

    def __post_init__(self) -> None:
        if self.model is None:
            self.model = os.environ.get(
                ROLE_ENV.get(self.role, ""), ""
            ).strip() or os.environ.get("LLM_MODEL", DEFAULT_MODEL)

        if self.api_key is None:
            found = resolve_api_key()
            if found:
                self.api_key, self.key_origin = found

    # -- request ------------------------------------------------------------

    def complete(self, messages: list[dict]) -> str:
        """Send a chat completion and return the assistant's text."""
        if not self.api_key:
            raise LlmUnavailable(
                "no API key: set LLM_API_KEY (or DEEPSEEK_API_KEY / OPENAI_API_KEY), "
                f"or store one at `pass show {os.environ.get('LLM_PASS_ENTRY', DEFAULT_PASS_ENTRY)}`. "
                "If the store is on another machine, set LLM_PASS_SSH_HOST."
            )

        body = json.dumps(
            {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            }
        ).encode("utf-8")

        last: Exception | None = None
        for attempt in range(self.max_retries):
            try:
                return self._post(body)
            except LlmError as exc:
                last = exc
                if not _retryable(exc):
                    raise
                time.sleep(2**attempt)

        raise LlmError(f"failed after {self.max_retries} attempts: {last}")

    def _post(self, body: bytes) -> str:
        req = urllib.request.Request(
            f"{self.base_url.rstrip('/')}/chat/completions",
            data=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # Don't echo the body — it quotes the request, which quotes nothing
            # secret today but would if a prompt ever carried one.
            raise LlmError(f"HTTP {exc.code}") from None
        except (urllib.error.URLError, TimeoutError) as exc:
            raise LlmError(f"transport: {type(exc).__name__}") from None
        except json.JSONDecodeError:
            raise LlmError("malformed JSON response") from None

        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError):
            raise LlmError("response had no message content") from None


def _retryable(exc: Exception) -> bool:
    text = str(exc)
    if "HTTP 4" in text and "HTTP 429" not in text:
        return False
    return True


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------


def complete(role: str, prompt: str, system: str | None = None, **kw) -> str:
    """One-shot completion for a role."""
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    return Model(role=role, **kw).complete(messages)


def complete_json(role: str, prompt: str, system: str | None = None, **kw) -> dict:
    """`complete` plus JSON extraction — models like to wrap objects in prose."""
    raw = complete(role, prompt, system, **kw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end > start:
            return json.loads(raw[start : end + 1])
        raise LlmError("response contained no JSON object") from None


def available() -> bool:
    return resolve_api_key() is not None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _check() -> int:
    entry = os.environ.get("LLM_PASS_ENTRY", DEFAULT_PASS_ENTRY)
    host = os.environ.get("LLM_PASS_SSH_HOST", "").strip()

    print("Key search order:")
    print("  env LLM_API_KEY / DEEPSEEK_API_KEY / OPENAI_API_KEY")
    print(f"  pass show {entry}")
    print(f"  ssh {host} pass show {entry}" if host else "  (LLM_PASS_SSH_HOST unset — remote store not searched)")
    print()

    found = resolve_api_key()
    if not found:
        print("No key found. The pipeline will use the deterministic template path.")
        print(f"Fix: export LLM_PASS_SSH_HOST=<host>, or export DEEPSEEK_API_KEY=...")
        return 1

    _, origin = found
    print(f"Key found via {origin}")
    print(f"  endpoint  {os.environ.get('LLM_ENDPOINT', DEFAULT_BASE_URL)}")
    for role in ROLE_ENV:
        print(f"  role {role:<10} -> {Model(role=role).model}")
    return 0


def main(argv: list[str]) -> int:
    if not argv or "--check" in argv:
        return _check()

    role = argv[argv.index("--role") + 1] if "--role" in argv else "writer"

    if "--say" in argv:
        try:
            print(complete(role, argv[argv.index("--say") + 1], max_tokens=200))
        except LlmUnavailable as exc:
            print(f"unavailable: {exc}", file=sys.stderr)
            return 1
        except LlmError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        return 0

    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
