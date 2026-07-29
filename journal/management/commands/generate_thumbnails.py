from django.core.management.base import BaseCommand

from journal.models import JournalEntry
from journal.thumbnails import ensure_entry_thumbnail


class Command(BaseCommand):
    help = "Generate missing (or all) journal grid thumbnails from full-size photos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Rebuild thumbnails even when one already exists.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Optional max number of entries to process.",
        )

    def handle(self, *args, **options):
        force = options["force"]
        limit = options["limit"]
        qs = JournalEntry.objects.exclude(photo="").order_by("id")
        if not force:
            qs = qs.filter(thumbnail="")
        if limit > 0:
            qs = qs[:limit]

        entries = list(qs)
        total = len(entries)
        made = 0
        skipped = 0
        errors = 0

        self.stdout.write(f"Processing {total} journal entries (force={force})…")
        for i, entry in enumerate(entries, 1):
            try:
                wrote = ensure_entry_thumbnail(entry, force=force)
                if wrote:
                    made += 1
                else:
                    skipped += 1
            except Exception as exc:
                errors += 1
                self.stderr.write(f"  [{entry.pk}] {entry.photo.name}: {exc}")
            if i % 50 == 0 or i == total:
                self.stdout.write(
                    f"  {i}/{total} (made={made}, skipped={skipped}, errors={errors})"
                )

        self.stdout.write(
            self.style.SUCCESS(f"Done. made={made} skipped={skipped} errors={errors}")
        )
