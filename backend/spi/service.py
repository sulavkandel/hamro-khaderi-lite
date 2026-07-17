"""SPI orchestration: pull daily data from DB, compute, snapshot."""
from __future__ import annotations

import datetime as dt

from districts.models import DailyPrecip, District, SpiSnapshot

from .compute import latest_spi, spi_series
from .severity import classify

SCALES = (3, 6, 12)


def last_thursday(today: dt.date | None = None) -> dt.date:
    """The most recent Thursday on or before `today` (weekly cadence)."""
    today = today or dt.date.today()
    offset = (today.weekday() - 3) % 7  # Thursday = weekday 3
    return today - dt.timedelta(days=offset)


def _daily_dict(district: District) -> dict[dt.date, float | None]:
    rows = DailyPrecip.objects.filter(district=district).values_list(
        "date", "precip_mm"
    )
    return {d: p for d, p in rows}


def compute_for_district(
    district: District, computed_for: dt.date | None = None
) -> int:
    """Compute + persist snapshots for all scales. Returns count written."""
    computed_for = computed_for or last_thursday()
    daily = _daily_dict(district)
    written = 0
    for scale in SCALES:
        result = latest_spi(daily, scale)
        value = result[1] if result else None
        SpiSnapshot.objects.update_or_create(
            district=district,
            computed_for=computed_for,
            scale_months=scale,
            defaults={
                "spi_value": value,
                "severity_class": classify(value),
            },
        )
        written += 1
    return written


def compute_all(computed_for: dt.date | None = None) -> int:
    total = 0
    for district in District.objects.all():
        total += compute_for_district(district, computed_for)
    return total


def full_history_series(district: District, scale: int) -> list[dict]:
    """Whole SPI history for charts: [{period, spi, severity}, ...]."""
    daily = _daily_dict(district)
    series = spi_series(daily, scale)
    out = []
    for (year, month), value in series.items():
        out.append({
            "period": f"{year:04d}-{month:02d}",
            "spi": None if value is None else round(value, 3),
            "severity": classify(value),
        })
    return out
