from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

THUMB_MAX_EDGE = 256
THUMB_JPEG_QUALITY = 72


def build_thumbnail_file(photo_field) -> ContentFile:
    """Return a small JPEG ContentFile from an ImageFieldFile."""
    photo_field.open("rb")
    try:
        with Image.open(photo_field) as image:
            image = ImageOps.exif_transpose(image)
            image = image.convert("RGB")
            image.thumbnail((THUMB_MAX_EDGE, THUMB_MAX_EDGE), Image.Resampling.LANCZOS)
            buffer = BytesIO()
            image.save(
                buffer,
                format="JPEG",
                quality=THUMB_JPEG_QUALITY,
                optimize=True,
                progressive=True,
            )
    finally:
        photo_field.close()
    return ContentFile(buffer.getvalue())


def thumbnail_basename(photo_name: str) -> str:
    stem = Path(photo_name).stem
    return f"{stem}.jpg"


def ensure_entry_thumbnail(entry, *, force: bool = False) -> bool:
    """
    Create/update entry.thumbnail from entry.photo.
    Returns True when a thumbnail was written.
    """
    if not entry.photo:
        return False
    if entry.thumbnail and not force:
        return False

    content = build_thumbnail_file(entry.photo)
    filename = thumbnail_basename(entry.photo.name)
    # Avoid recursive save signals: write file then update row once.
    if entry.thumbnail:
        entry.thumbnail.delete(save=False)
    entry.thumbnail.save(filename, content, save=False)
    entry.save(update_fields=["thumbnail"])
    return True
