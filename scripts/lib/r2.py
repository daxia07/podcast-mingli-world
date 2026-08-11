#!/usr/bin/env python3
"""r2.py — R2 access for the lib package.

Deliberately a thin shim over the existing wrangler-backed `scripts/r2_utils.py`
rather than a boto3 client. The boto3 rewrite was dropped (DECISIONS.md,
2026-08-11): it needs R2 S3 credentials that don't exist and can never be read
back once created, and the only capability it actually bought — listing — is
available for free through the R2 binding the Pages Functions already hold.

`list_prefix` therefore goes over HTTP to `/api/feedback-list` instead of the
S3 API. It is the one operation wrangler cannot do.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from r2_utils import (  # noqa: F401  — re-exported as the module's public API
    BUCKET,
    download,
    get_json,
    get_text,
    upload,
    upload_bytes,
    upload_json,
)

BASE_URL = os.environ.get("BASE_URL", "https://podcast.mingli.world")


def list_prefix(prefix: str, *, base_url: str | None = None, timeout: int = 30) -> list[str]:
    """Object keys under `prefix`, via the Pages Function's R2 binding.

    Returns [] rather than raising when the endpoint is unreachable, so a
    caller can fall back to convention-based key guessing offline.
    """
    url = f"{(base_url or BASE_URL).rstrip('/')}/api/feedback-list?prefix={prefix}"
    keys: list[str] = []
    cursor = None

    while True:
        target = url + (f"&cursor={cursor}" if cursor else "")
        try:
            with urllib.request.urlopen(target, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return keys

        keys.extend(payload.get("keys", []))
        cursor = payload.get("cursor")
        if not payload.get("truncated") or not cursor:
            return keys
