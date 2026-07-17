from django.contrib import admin

from .models import DailyPrecip, District, IngestionRun, SpiSnapshot


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name_en", "name_ne", "slug", "province")
    prepopulated_fields = {"slug": ("name_en",)}


@admin.register(DailyPrecip)
class DailyPrecipAdmin(admin.ModelAdmin):
    list_display = ("district", "date", "precip_mm", "source")
    list_filter = ("district", "source")
    date_hierarchy = "date"


@admin.register(SpiSnapshot)
class SpiSnapshotAdmin(admin.ModelAdmin):
    list_display = ("district", "computed_for", "scale_months", "spi_value", "severity_class")
    list_filter = ("district", "scale_months", "severity_class")


@admin.register(IngestionRun)
class IngestionRunAdmin(admin.ModelAdmin):
    list_display = ("district", "source", "from_date", "to_date", "status", "rows_upserted")
    list_filter = ("status", "source")
