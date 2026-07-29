#!/usr/bin/env bash
# Push local journal thumbnails to R2, migrate Neon, set thumbnail paths + cache headers.
#
# Prefers env vars you already exported (Cursor often scrubs `vercel env pull`).
# Example:
#   export DATABASE_URL_UNPOOLED='postgresql://…'
#   export AWS_ACCESS_KEY_ID=…
#   export AWS_SECRET_ACCESS_KEY=…
#   export AWS_STORAGE_BUCKET_NAME=connorbrown-media
#   export AWS_S3_ENDPOINT_URL='https://….r2.cloudflarestorage.com'
#   ./scripts/sync_thumbs_prod.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="$(mktemp)"
cleanup() { rm -f "$ENV_FILE"; }
trap cleanup EXIT

# Optional fill-in from Vercel for any keys you did not export.
if [[ -z "${AWS_ACCESS_KEY_ID:-}" || -z "${AWS_STORAGE_BUCKET_NAME:-}" ]]; then
  echo "Pulling production env (fills missing AWS_* only)…"
  npx --yes vercel env pull "$ENV_FILE" --environment=production --yes >/dev/null || true
else
  echo "Using AWS_* / DATABASE_* from your shell environment."
  : >"$ENV_FILE"
fi

./.venv/bin/python - "$ENV_FILE" <<'PY'
import os
import subprocess
import sys
from pathlib import Path

env_path = Path(sys.argv[1])
pulled: dict[str, str] = {}
if env_path.exists() and env_path.stat().st_size:
    for raw in env_path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value and value != "[SENSITIVE]" and not value.startswith("["):
            pulled[key] = value

def pick(*keys: str) -> str:
    for key in keys:
        value = os.environ.get(key) or pulled.get(key) or ""
        if value and value != "[SENSITIVE]" and not value.startswith("["):
            return value
    return ""

vals = {
    "DATABASE_URL_UNPOOLED": pick("DATABASE_URL_UNPOOLED", "POSTGRES_URL_NON_POOLING"),
    "DATABASE_URL": pick("DATABASE_URL", "POSTGRES_URL"),
    "AWS_ACCESS_KEY_ID": pick("AWS_ACCESS_KEY_ID"),
    "AWS_SECRET_ACCESS_KEY": pick("AWS_SECRET_ACCESS_KEY"),
    "AWS_STORAGE_BUCKET_NAME": pick("AWS_STORAGE_BUCKET_NAME"),
    "AWS_S3_ENDPOINT_URL": pick("AWS_S3_ENDPOINT_URL"),
    "AWS_S3_REGION_NAME": pick("AWS_S3_REGION_NAME") or "auto",
    "AWS_S3_ADDRESSING_STYLE": pick("AWS_S3_ADDRESSING_STYLE") or "path",
    "AWS_S3_CUSTOM_DOMAIN": pick("AWS_S3_CUSTOM_DOMAIN"),
}

required = [
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_STORAGE_BUCKET_NAME",
    "AWS_S3_ENDPOINT_URL",
]
missing = [k for k in required if not vals[k]]
url = vals["DATABASE_URL_UNPOOLED"] or vals["DATABASE_URL"]
if not url:
    missing.append("DATABASE_URL_UNPOOLED")

for key in list(required) + ["DATABASE_URL_UNPOOLED", "DATABASE_URL"]:
    print(f"{key}: {'ok' if (vals.get(key) or (key.startswith('DATABASE') and url)) else 'MISSING'}")

if missing:
    print(
        "Missing: "
        + ", ".join(missing)
        + "\nExport them in this shell (vercel env pull is scrubbed inside Cursor).",
        file=sys.stderr,
    )
    sys.exit(2)

if not url.startswith(("postgres://", "postgresql://")):
    print("DATABASE_URL is not postgres", file=sys.stderr)
    sys.exit(2)

child_env = os.environ.copy()
child_env.update({k: v for k, v in vals.items() if v})
child_env["DATABASE_URL"] = vals["DATABASE_URL"] or url
child_env["DATABASE_URL_UNPOOLED"] = url

print("Migrating journal app on Neon…")
subprocess.run(
    [str(Path(".venv/bin/python")), "manage.py", "migrate", "journal", "--noinput"],
    env=child_env,
    check=True,
)

print("Uploading media/journal/thumbs → R2…")
import boto3
from botocore.config import Config

client = boto3.client(
    "s3",
    endpoint_url=vals["AWS_S3_ENDPOINT_URL"],
    aws_access_key_id=vals["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=vals["AWS_SECRET_ACCESS_KEY"],
    region_name=vals["AWS_S3_REGION_NAME"],
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": vals["AWS_S3_ADDRESSING_STYLE"]},
    ),
)
bucket = vals["AWS_STORAGE_BUCKET_NAME"]
thumbs = sorted(Path("media/journal/thumbs").glob("*.jpg"))
cache = "public, max-age=31536000, immutable"
print(f"Uploading {len(thumbs)} thumbnails…")
for i, path in enumerate(thumbs, 1):
    key = f"journal/thumbs/{path.name}"
    client.upload_file(
        str(path),
        bucket,
        key,
        ExtraArgs={"ContentType": "image/jpeg", "CacheControl": cache},
    )
    if i % 100 == 0 or i == len(thumbs):
        print(f"  {i}/{len(thumbs)}")

print("Pointing Neon rows at thumbnail keys…")
sql = """
UPDATE journal_journalentry
SET thumbnail = 'journal/thumbs/' || regexp_replace(regexp_replace(photo, '^journal/', ''), '\\.[^.]+$', '.jpg')
WHERE photo IS NOT NULL AND photo <> '';
"""
subprocess.run(["psql", url, "-v", "ON_ERROR_STOP=1", "-c", sql], check=True)
subprocess.run(
    [
        "psql",
        url,
        "-c",
        "SELECT count(*) FILTER (WHERE thumbnail <> '') AS with_thumb, count(*) AS total FROM journal_journalentry;",
    ],
    check=True,
)

print("Setting Cache-Control on journal/* in R2…")
subprocess.run(
    [str(Path(".venv/bin/python")), "manage.py", "set_media_cache_headers", "--prefix", "journal/"],
    env=child_env,
    check=True,
)
print("Done. Hard-refresh https://connorbrown.net/photo-journal/")
PY
