"""Ingestion pipeline: fetch -> QC -> upsert -> audit log."""
from __future__ import annotations

import datetime as dt

from django.conf import settings
from django.db import transaction

from districts.models import DailyPrecip, District, IngestionRun

from .sources.registry import get_source


def qc_value(raw: float | None) -> tuple[float | None, bool]:
    """Quality control a single daily value.

    Returns (clean_value, rejected). Negative or absurdly large values
    (> PRECIP_MAX_MM_PER_DAY) are stored as NULL and counted as rejected.
    """
    if raw is None:
        return None, False
    if raw < 0 or raw > settings.PRECIP_MAX_MM_PER_DAY:
        return None, True
    return raw, False


def default_ingest_window(days: int = 14) -> tuple[dt.date, dt.date]:
    """Last `days` days, clamped by the provider archive lag."""
    to_date = dt.date.today() - dt.timedelta(days=settings.ARCHIVE_LAG_DAYS)
    from_date = to_date - dt.timedelta(days=days - 1)
    return from_date, to_date


def ingest_district(
    district: District,
    from_date: dt.date,
    to_date: dt.date,
    source_name: str | None = None,
) -> IngestionRun:
    source_name = source_name or settings.WEATHER_SOURCE
    run = IngestionRun(
        district=district,
        source=source_name,
        from_date=from_date,
        to_date=to_date,
    )
    try:
        source = get_source(source_name)
        observations = source.fetch_daily(
            float(district.centroid_lat),
            float(district.centroid_lng),
            from_date,
            to_date,
        )
        rows: list[DailyPrecip] = []
        rejected = 0
        for obs in observations:
            clean, was_rejected = qc_value(obs.precip_mm)
            rejected += int(was_rejected)
            rows.append(
                DailyPrecip(
                    district=district,
                    date=obs.date,
                    precip_mm=clean,
                    source=source_name,
                )
            )
        with transaction.atomic():
            DailyPrecip.objects.bulk_create(
                rows,
                update_conflicts=True,
                update_fields=["precip_mm", "ingested_at"],
                unique_fields=["district", "date", "source"],
            )
        run.rows_upserted = len(rows)
        run.rows_rejected = rejected
        run.status = "partial" if rejected else "ok"
        run.detail = f"{rejected} values failed QC" if rejected else ""
    except Exception as exc:  # noqa: BLE001 — audit everything
        run.status = "failed"
        run.detail = str(exc)[:2000]
    run.save()
    return run


def ingest_range(
    from_date: dt.date,
    to_date: dt.date,
    source_name: str | None = None,
    district_slug: str | None = None,
) -> list[IngestionRun]:
    qs = District.objects.all()
    if district_slug:
        qs = qs.filter(slug=district_slug)
    return [ingest_district(d, from_date, to_date, source_name) for d in qs]
