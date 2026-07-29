import json
from datetime import date, datetime
from pathlib import Path


def find_export_roots(source_dir: Path) -> list[Path]:
    roots = [source_dir]
    activity = source_dir / "your_instagram_activity"
    if activity.exists():
        roots.append(activity)
    return roots


def iter_export_posts(source_dir: Path):
    seen = set()
    for root in find_export_roots(source_dir):
        content_dir = root / "content"
        if not content_dir.exists():
            continue
        for json_path in sorted(content_dir.glob("posts*.json")):
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            for item in payload if isinstance(payload, list) else payload.get("media", []):
                if not isinstance(item, dict):
                    continue
                uri = item.get("uri") or item.get("path") or ""
                if not uri or uri in seen:
                    continue
                seen.add(uri)
                yield item, root


def resolve_export_media(root: Path, uri: str) -> Path | None:
    candidates = [
        root / uri,
        root.parent / uri,
        root / "media" / "posts" / Path(uri).name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = list(root.rglob(Path(uri).name))
    return matches[0] if matches else None


def export_shortcode(item: dict, media_path: Path) -> str:
    for key in ("shortcode", "id", "media_id"):
        if item.get(key):
            return str(item[key])
    return media_path.stem


def export_title(item: dict, media_path: Path) -> str:
    caption = (item.get("title") or item.get("caption") or "").strip()
    if caption:
        return caption.splitlines()[0][:200]
    return media_path.stem


def export_caption(item: dict) -> str:
    return (item.get("title") or item.get("caption") or "").strip()


def export_date(item: dict) -> date:
    for key in ("creation_timestamp", "taken_at", "timestamp"):
        value = item.get(key)
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value).date()
    if item.get("creation_timestamp_utc"):
        return datetime.fromisoformat(str(item["creation_timestamp_utc"]).replace("Z", "+00:00")).date()
    return date.today()
