from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from journal.instagram_export import (
    export_caption,
    export_date,
    export_shortcode,
    export_title,
    iter_export_posts,
    resolve_export_media,
)
from journal.models import JournalEntry


class Command(BaseCommand):
    help = "Import photos from Instagram's official data export (no Instaloader login)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-dir",
            required=True,
            help="Path to extracted Instagram export folder",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview imports without writing to the database",
        )

    def handle(self, *args, **options):
        source_dir = Path(options["source_dir"]).expanduser().resolve()
        if not source_dir.exists():
            self.stderr.write(f"Export folder not found: {source_dir}")
            return

        created = 0
        skipped = 0
        missing = 0

        for item, root in iter_export_posts(source_dir):
            uri = item.get("uri") or item.get("path") or ""
            media_path = resolve_export_media(root, uri)
            if not media_path:
                missing += 1
                continue

            shortcode = export_shortcode(item, media_path)
            if JournalEntry.objects.filter(instagram_shortcode=shortcode).exists():
                skipped += 1
                continue

            if options["dry_run"]:
                self.stdout.write(f"Would import: {media_path.name} ({shortcode})")
                created += 1
                continue

            entry = JournalEntry(
                title=export_title(item, media_path),
                caption=export_caption(item),
                entry_date=export_date(item),
                instagram_shortcode=shortcode,
            )
            with media_path.open("rb") as handle:
                entry.photo.save(media_path.name, File(handle), save=False)
            entry.save()
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done: {created} imported, {skipped} skipped, {missing} missing files"
            )
        )
