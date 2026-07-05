"""R2 operations via wrangler CLI — reliable with any Cloudflare API token.

Requires CLOUDFLARE_API_TOKEN in environment.
Wrangler downloads files to the current working directory.
"""

import json, os, subprocess, tempfile

BUCKET = "podcast-mingli-world"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)


def _run(*args):
    """Run wrangler CLI from the project directory."""
    cmd = ["npx", "wrangler"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_DIR)
    if result.returncode != 0:
        raise RuntimeError(f"wrangler failed: {result.stderr[:500]}")
    return result.stdout


def upload(key, filepath):
    """Upload a local file to R2."""
    _run("r2", "object", "put", f"{BUCKET}/{key}", "--file", filepath, "--remote")


def upload_bytes(key, data):
    """Upload bytes as an R2 object."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".tmp")
    try:
        tmp.write(data if isinstance(data, bytes) else data.encode())
        tmp.close()
        upload(key, tmp.name)
    finally:
        os.unlink(tmp.name)


def upload_json(key, data):
    """Upload JSON-serializable data to R2."""
    upload_bytes(key, json.dumps(data, indent=2).encode())


def download(key):
    """Download a file from R2. Returns bytes or None."""
    filename = key.split("/")[-1]
    local_path = os.path.join(PROJECT_DIR, filename)

    # Remove if exists
    if os.path.exists(local_path):
        os.unlink(local_path)

    try:
        _run("r2", "object", "get", f"{BUCKET}/{key}", "--remote")
    except RuntimeError:
        return None

    if os.path.exists(local_path):
        with open(local_path, "rb") as f:
            data = f.read()
        os.unlink(local_path)
        return data
    return None


def get_json(key):
    """Download and parse a JSON object from R2. Returns dict or None."""
    data = download(key)
    if data:
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError):
            pass
    return None


def get_text(key):
    """Download and return text from R2. Returns str or None."""
    data = download(key)
    if data:
        try:
            return data.decode()
        except UnicodeDecodeError:
            pass
    return None
