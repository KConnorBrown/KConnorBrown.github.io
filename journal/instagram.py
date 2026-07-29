import json
import lzma
from datetime import date, datetime
from pathlib import Path


def load_post_metadata(path: Path) -> dict | None:
    for candidate in (path.with_suffix(path.suffix + ".json.xz"), path.with_suffix(".json.xz"), path.with_suffix(".json")):
        if not candidate.exists():
            continue
        if candidate.suffix == ".xz":
            with lzma.open(candidate, "rt", encoding="utf-8") as handle:
                return json.load(handle)
        with candidate.open(encoding="utf-8") as handle:
            return json.load(handle)
    return None


def parse_post_date(metadata: dict | None, image_path: Path) -> date:
    if metadata:
        for key in ("date", "date_local", "taken_at_timestamp"):
            value = metadata.get(key)
            if isinstance(value, (int, float)):
                return datetime.fromtimestamp(value).date()
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    stem = image_path.stem.replace("_UTC", "")
    try:
        return datetime.strptime(stem, "%Y-%m-%d_%H-%M-%S").date()
    except ValueError:
        return date.today()


def post_title(metadata: dict | None, image_path: Path) -> str:
    if metadata:
        caption = (metadata.get("caption") or metadata.get("edge_media_to_caption") or "").strip()
        if caption:
            first_line = caption.splitlines()[0].strip()
            if first_line:
                return first_line[:200]
        shortcode = metadata.get("shortcode")
        if shortcode:
            return shortcode
    return image_path.stem


def post_caption(metadata: dict | None) -> str:
    if not metadata:
        return ""
    caption = metadata.get("caption") or metadata.get("edge_media_to_caption") or ""
    return caption.strip()


def post_shortcode(metadata: dict | None, image_path: Path) -> str:
    base = metadata.get("shortcode") if metadata else image_path.stem.replace("_UTC", "")
    stem = image_path.stem
    if "_UTC_" in stem:
        suffix = stem.rsplit("_UTC_", 1)[-1]
        if suffix.isdigit():
            return f"{base}_{suffix}"
    return base or image_path.stem


def iter_downloaded_images(root: Path):
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
            continue
        if path.name.startswith("."):
            continue
        yield path
