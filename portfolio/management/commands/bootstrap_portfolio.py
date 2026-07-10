from django.core.management.base import BaseCommand

from portfolio.models import Project


class Command(BaseCommand):
    help = "Create initial featured projects for the development portfolio."

    def handle(self, *args, **options):
        project, created = Project.objects.get_or_create(
            slug="sql-playground",
            defaults={
                "title": "SQL Playground",
                "summary": (
                    "A read-only PostgreSQL sandbox aligned with the official "
                    "tutorial, built into this site."
                ),
                "tech_stack": "Django, PostgreSQL, JavaScript",
                "live_url": "/playground/sql/",
                "featured": True,
                "case_study": (
                    "This playground mirrors the weather, cities, and empsalary "
                    "datasets from the PostgreSQL documentation. Visitors can run "
                    "SELECT queries in the browser while write operations remain "
                    "available locally in psql during tutorial practice."
                ),
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Created SQL Playground project."))
        else:
            self.stdout.write("SQL Playground project already exists.")
