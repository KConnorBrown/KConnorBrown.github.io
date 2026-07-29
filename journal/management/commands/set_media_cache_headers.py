"""Set Cache-Control on existing R2/S3 media objects (thumbs + originals)."""

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


CACHE_CONTROL = "public, max-age=31536000, immutable"


class Command(BaseCommand):
    help = "Apply long-lived Cache-Control metadata to objects in the media bucket."

    def add_arguments(self, parser):
        parser.add_argument(
            "--prefix",
            default="journal/",
            help="Only update keys under this prefix (default: journal/).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List how many keys would be updated without writing.",
        )

    def handle(self, *args, **options):
        bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", None)
        if not bucket:
            raise CommandError("AWS_STORAGE_BUCKET_NAME is not configured.")

        import boto3
        from botocore.config import Config

        client = boto3.client(
            "s3",
            endpoint_url=getattr(settings, "AWS_S3_ENDPOINT_URL", None) or None,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=getattr(settings, "AWS_S3_REGION_NAME", "auto"),
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": getattr(settings, "AWS_S3_ADDRESSING_STYLE", "path")},
            ),
        )

        prefix = options["prefix"]
        dry_run = options["dry_run"]
        token = None
        updated = 0
        scanned = 0

        self.stdout.write(f"Updating Cache-Control on s3://{bucket}/{prefix} …")
        while True:
            kwargs = {"Bucket": bucket, "Prefix": prefix, "MaxKeys": 1000}
            if token:
                kwargs["ContinuationToken"] = token
            page = client.list_objects_v2(**kwargs)
            for obj in page.get("Contents") or []:
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                scanned += 1
                if dry_run:
                    continue
                head = client.head_object(Bucket=bucket, Key=key)
                content_type = head.get("ContentType") or "application/octet-stream"
                # R2/S3: rewrite metadata via copy in place.
                client.copy_object(
                    Bucket=bucket,
                    Key=key,
                    CopySource={"Bucket": bucket, "Key": key},
                    MetadataDirective="REPLACE",
                    ContentType=content_type,
                    CacheControl=CACHE_CONTROL,
                    Metadata={k: v for k, v in (head.get("Metadata") or {}).items()},
                )
                updated += 1
                if updated % 50 == 0:
                    self.stdout.write(f"  updated {updated}/{scanned}")
            if not page.get("IsTruncated"):
                break
            token = page.get("NextContinuationToken")

        if dry_run:
            self.stdout.write(self.style.WARNING(f"Dry run: would update {scanned} objects."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Done. scanned={scanned} updated={updated}"))
