from django.apps import AppConfig
from django.conf import settings


class IngestionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ingestion"

    def ready(self):
        # Only autostart in a real web process (gunicorn / runserver),
        # never during migrations, tests or one-off management commands.
        if settings.SCHEDULER_AUTOSTART:
            from . import scheduler
            scheduler.start()
