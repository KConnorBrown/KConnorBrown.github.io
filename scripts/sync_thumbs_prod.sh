#!/usr/bin/env bash
# Push local journal thumbnails to R2, migrate Neon, set thumbnail paths + cache headers.
# Usage (from repo root, with network):
#   ./scripts/sync_thumbs_prod.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="$(mktemp)"
cleanup() { rm -f "$ENV_FILE"; }
trap cleanup EXIT

echo "Pulling production env…"
npx --yes vercel env pull "$ENV_FILE" --environment=production --yes >/dev/null

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

export DATABASE_URL="${DATABASE_URL:-$DATABASE_URL_UNPOOLED}"
URL="${DATABASE_URL_UNPOOLED:-$DATABASE_URL}"

if [[ -z "${AWS_STORAGE_BUCKET_NAME:-}" || -z "$URL" ]]; then
  echo "Missing AWS_STORAGE_BUCKET_NAME or DATABASE_URL in production env." >&2
  exit 1
fi

echo "Migrating journal app on Neon…"
./.venv/bin/python manage.py migrate journal --noinput

echo "Uploading media/journal/thumbs → R2…"
./.venv/bin/python - <<'PY'
import os
from pathlib import Path
import boto3
from botocore.config import Config

client = boto3.client(
    "s3",
    endpoint_url=os.environ["AWS_S3_ENDPOINT_URL"],
    aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    region_name=os.environ.get("AWS_S3_REGION_NAME", "auto"),
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": os.environ.get("AWS_S3_ADDRESSING_STYLE", "path")},
    ),
)
bucket = os.environ["AWS_STORAGE_BUCKET_NAME"]
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
print("Upload done.")
PY

echo "Pointing Neon rows at thumbnail keys…"
psql "$URL" -v ON_ERROR_STOP=1 -c "
UPDATE journal_journalentry
SET thumbnail = 'journal/thumbs/' || regexp_replace(regexp_replace(photo, '^journal/', ''), '\.[^.]+$', '.jpg')
WHERE photo IS NOT NULL AND photo <> '';
"
psql "$URL" -c "SELECT count(*) FILTER (WHERE thumbnail <> '') AS with_thumb, count(*) AS total FROM journal_journalentry;"

echo "Setting Cache-Control on journal/* in R2…"
./.venv/bin/python manage.py set_media_cache_headers --prefix journal/

echo "Done. Redeploy or hard-refresh https://connorbrown.net/photo-journal/"
