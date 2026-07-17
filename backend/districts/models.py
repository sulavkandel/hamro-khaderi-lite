"""Core data model: districts, daily precipitation, SPI snapshots.

Design notes
------------
* ``DailyPrecip.precip_mm`` is nullable — a NULL means "observation failed
  quality control or was missing", which is different from 0.0 mm (no rain).
* ``SpiSnapshot`` stores one row per (district, thursday, scale) so the
  weekly history is queryable without recomputation.
"""
from django.db import models


class District(models.Model):
    name_en = models.CharField(max_length=100)
    name_ne = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    province = models.CharField(max_length=100)
    centroid_lat = models.DecimalField(max_digits=9, decimal_places=6)
    centroid_lng = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name_en


class DailyPrecip(models.Model):
    SOURCE_CHOICES = [
        ("open_meteo", "Open-Meteo"),
        ("dhm", "DHM"),
    ]

    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="daily_precip"
    )
    date = models.DateField()
    # NULL = missing/failed-QC observation (distinct from 0.0 = no rain)
    precip_mm = models.FloatField(null=True, blank=True)
    source = models.CharField(max_length=32, choices=SOURCE_CHOICES)
    ingested_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["district", "date", "source"],
                name="uniq_district_date_source",
            )
        ]
        indexes = [
            models.Index(fields=["district", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.district.slug} {self.date}: {self.precip_mm} mm"


class SpiSnapshot(models.Model):
    SCALE_CHOICES = [(3, "SPI-3"), (6, "SPI-6"), (12, "SPI-12")]

    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="spi_snapshots"
    )
    # The Thursday this snapshot was computed for (weekly cadence).
    computed_for = models.DateField()
    scale_months = models.PositiveSmallIntegerField(choices=SCALE_CHOICES)
    spi_value = models.FloatField(null=True, blank=True)
    severity_class = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["district", "computed_for", "scale_months"],
                name="uniq_district_thursday_scale",
            )
        ]
        ordering = ["-computed_for", "scale_months"]

    def __str__(self) -> str:
        return (
            f"{self.district.slug} SPI-{self.scale_months} "
            f"@{self.computed_for}: {self.spi_value}"
        )


class IngestionRun(models.Model):
    STATUS_CHOICES = [
        ("ok", "OK"),
        ("partial", "Partial"),
        ("failed", "Failed"),
    ]

    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="ingestion_runs"
    )
    source = models.CharField(max_length=32)
    from_date = models.DateField()
    to_date = models.DateField()
    rows_upserted = models.IntegerField(default=0)
    rows_rejected = models.IntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES)
    detail = models.TextField(blank=True, default="")
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.district.slug} {self.from_date}..{self.to_date} [{self.status}]"
