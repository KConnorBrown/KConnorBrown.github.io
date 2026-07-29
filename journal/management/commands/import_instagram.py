from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from journal.instagram import (
    iter_downloaded_images,
    load_post_metadata,
    parse_post_date,
    post_caption,
    post_shortcode,
    post_title,
)
from journal.models import JournalEntry


class Command(BaseCommand):
    help = "Import downloaded Instagram images into the photo journal."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-dir",
            default="",
            help="Folder containing downloaded Instagram images (default: data/instagram/rupaulsoilrig)",
        )
        parser.add_argument(
            "--username",
            default="rupaulsoilrig",
            help="Used to locate the default source directory",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be imported without writing to the database",
        )

    def handle(self, *args, **options):
        source_dir = Path(
            options["source_dir"]
            or settings.BASE_DIR / "data" / "instagram" / options["username"]
        )
        if not source_dir.exists():
            self.stderr.write(f"Source directory not found: {source_dir}")
            self.stderr.write("Run: python manage.py fetch_instagram")
            return

        created = 0
        skipped = 0

        for image_path in iter_downloaded_images(source_dir):
            metadata = load_post_metadata(image_path)
            shortcode = post_shortcode(metadata, image_path)

            if JournalEntry.objects.filter(instagram_shortcode=shortcode).exists():
                skipped += 1
                continue

            if options["dry_run"]:
                self.stdout.write(f"Would import: {image_path.name} ({shortcode})")
                created += 1
                continue

            entry = JournalEntry(
                title=post_title(metadata, image_path),
                caption=post_caption(metadata),
                entry_date=parse_post_date(metadata, image_path),
                instagram_shortcode=shortcode,
            )
            with image_path.open("rb") as handle:
                entry.photo.save(image_path.name, File(handle), save=False)
            entry.save()
            created += 1

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Dry run: {created} new, {skipped} skipped"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Imported {created} photos, skipped {skipped} duplicates"))
