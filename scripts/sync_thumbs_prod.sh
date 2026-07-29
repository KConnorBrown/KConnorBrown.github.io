#!/usr/bin/env bash
# Push local journal thumbnails to R2, migrate Neon, set thumbnail paths + cache headers.
# Usage (from repo root):
#   ./scripts/sync_thumbs_prod.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="$(mktemp)"
cleanup() { rm -f "$ENV_FILE"; }
trap cleanup EXIT

echo "Pulling production env…"
npx --yes vercel env pull "$ENV_FILE" --environment=production --yes >/dev/null

./.venv/bin/python - "$ENV_FILE" <<'PY'
import os
import subprocess
import sys
from pathlib import Path

env_path = Path(sys.argv[1])
vals: dict[str, str] = {}
for raw in env_path.read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    vals[key] = value

for key in (
    "DATABASE_URL_UNPOOLED",
    "DATABASE_URL",
    "AWS_ACCESS_KEY_ID",
    "AWS_SECRET_ACCESS_KEY",
    "AWS_STORAGE_BUCKET_NAME",
    "AWS_S3_ENDPOINT_URL",
):
    value = vals.get(key, "")
    ok = bool(value) and value != "[SENSITIVE]" and not value.startswith("[")
    print(f"{key}: {'ok' if ok else 'MISSING/SCRUBBED'}")
    if not ok:
        print(
            "Production secrets were scrubbed in this environment.\n"
            "Run this script in Terminal.app (outside Cursor), or export\n"
            "DATABASE_URL_UNPOOLED + AWS_* yourself first.",
            file=sys.stderr,
        )
        sys.exit(2)

url = vals.get("DATABASE_URL_UNPOOLED") or vals["DATABASE_URL"]
if not url.startswith(("postgres://", "postgresql://")):
    print("DATABASE_URL is not postgres", file=sys.stderr)
    sys.exit(2)

child_env = os.environ.copy()
for key, value in vals.items():
    if key.startswith(("AWS_", "DATABASE_", "DJANGO_", "PG", "POSTGRES", "CSRF", "NEON_")):
        child_env[key] = value
child_env["DATABASE_URL"] = vals.get("DATABASE_URL") or url

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
    region_name=vals.get("AWS_S3_REGION_NAME", "auto"),
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": vals.get("AWS_S3_ADDRESSING_STYLE", "path")},
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
