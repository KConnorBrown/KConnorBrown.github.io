from pathlib import Path
import re

from django.core.management.base import BaseCommand
from django.db import connections


class Command(BaseCommand):
    help = "Seed the playground database with official PostgreSQL tutorial data."

    def handle(self, *args, **options):
        seed_path = Path(__file__).resolve().parents[2] / "sql" / "seed.sql"
        sql = seed_path.read_text()
        statements = [
            statement.strip()
            for statement in re.split(r";\s*\n", sql)
            if statement.strip() and not statement.strip().startswith("--")
        ]

        with connections["playground"].cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)

        self.stdout.write(self.style.SUCCESS("Playground database seeded successfully."))
