"""Seed the three pilot Terai districts. Idempotent (update_or_create)."""
from django.core.management.base import BaseCommand

from districts.models import District

DISTRICTS = [
    {
        "slug": "kailali",
        "name_en": "Kailali",
        "name_ne": "कैलाली",
        "province": "Sudurpaschim",
        "centroid_lat": "28.686111",
        "centroid_lng": "80.897222",
    },
    {
        "slug": "bardiya",
        "name_en": "Bardiya",
        "name_ne": "बर्दिया",
        "province": "Lumbini",
        "centroid_lat": "28.309444",
        "centroid_lng": "81.429167",
    },
    {
        "slug": "kapilvastu",
        "name_en": "Kapilvastu",
        "name_ne": "कपिलवस्तु",
        "province": "Lumbini",
        "centroid_lat": "27.596389",
        "centroid_lng": "83.028889",
    },
]


class Command(BaseCommand):
    help = "Seed the pilot districts (idempotent)."

    def handle(self, *args, **options):
        for row in DISTRICTS:
            obj, created = District.objects.update_or_create(
                slug=row["slug"], defaults=row
            )
            verb = "created" if created else "updated"
            self.stdout.write(f"{verb}: {obj.name_en}")
        self.stdout.write(self.style.SUCCESS("Districts seeded."))
