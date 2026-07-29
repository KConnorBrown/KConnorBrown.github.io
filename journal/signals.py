from django.db.models.signals import post_save
from django.dispatch import receiver

from journal.models import JournalEntry
from journal.thumbnails import ensure_entry_thumbnail


@receiver(post_save, sender=JournalEntry)
def journal_entry_make_thumbnail(sender, instance, **kwargs):
    if not instance.photo:
        return
    # Skip if thumbnail already matches a fresh generate unless photo changed.
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and "thumbnail" in update_fields and "photo" not in update_fields:
        return
    force = bool(update_fields and "photo" in update_fields)
    if instance.thumbnail and not force:
        return
    try:
        ensure_entry_thumbnail(instance, force=force)
    except Exception:
        # Don't block admin saves if Pillow fails on a bad file.
        pass
