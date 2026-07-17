"""manage.py ingest — fetch daily precipitation into DailyPrecip."""
import datetime as dt

from django.conf import settings
from django.core.management.base import BaseCommand

from ingestion.service import default_ingest_window, ingest_range


class Command(BaseCommand):
    help = "Ingest daily precipitation for all (or one) districts."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=14,
                            help="Window size in days (default 14).")
        parser.add_argument("--from", dest="from_date", type=str, default=None,
                            help="Start date YYYY-MM-DD (overrides --days).")
        parser.add_argument("--to", dest="to_date", type=str, default=None,
                            help="End date YYYY-MM-DD.")
        parser.add_argument("--source", type=str, default=None,
                            help=f"Weather source (default {settings.WEATHER_SOURCE}).")
        parser.add_argument("--district", type=str, default=None,
                            help="Restrict to one district slug.")

    def handle(self, *args, **options):
        if options["from_date"]:
            frm = dt.date.fromisoformat(options["from_date"])
            to = (dt.date.fromisoformat(options["to_date"])
                  if options["to_date"]
                  else default_ingest_window(1)[1])
        else:
            frm, to = default_ingest_window(options["days"])

        self.stdout.write(f"Ingesting {frm} .. {to}")
        runs = ingest_range(frm, to, options["source"], options["district"])
        for run in runs:
            style = (self.style.SUCCESS if run.status == "ok"
                     else self.style.WARNING if run.status == "partial"
                     else self.style.ERROR)
            self.stdout.write(style(
                f"  {run.district.slug}: {run.status} "
                f"(upserted={run.rows_upserted}, rejected={run.rows_rejected}) {run.detail}"
            ))
