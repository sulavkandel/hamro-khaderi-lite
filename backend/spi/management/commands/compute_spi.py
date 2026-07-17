"""manage.py compute_spi — compute SPI snapshots for all districts."""
import datetime as dt

from django.core.management.base import BaseCommand

from spi.service import compute_all, last_thursday


class Command(BaseCommand):
    help = "Compute SPI-3/6/12 snapshots for every district."

    def add_arguments(self, parser):
        parser.add_argument("--for", dest="for_date", type=str, default=None,
                            help="Compute-for date YYYY-MM-DD (default: last Thursday).")

    def handle(self, *args, **options):
        for_date = (dt.date.fromisoformat(options["for_date"])
                    if options["for_date"] else last_thursday())
        count = compute_all(for_date)
        self.stdout.write(self.style.SUCCESS(
            f"Computed {count} snapshots for {for_date}."
        ))
