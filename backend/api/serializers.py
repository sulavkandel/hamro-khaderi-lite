"""DRF serializers for the public API."""
from rest_framework import serializers

from districts.models import District, SpiSnapshot
from spi.severity import SEVERITY_META


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = [
            "id", "slug", "name_en", "name_ne",
            "province", "centroid_lat", "centroid_lng",
        ]


class SpiSnapshotSerializer(serializers.ModelSerializer):
    severity = serializers.SerializerMethodField()

    class Meta:
        model = SpiSnapshot
        fields = [
            "computed_for", "scale_months", "spi_value",
            "severity_class", "severity",
        ]

    def get_severity(self, obj):
        meta = SEVERITY_META.get(obj.severity_class)
        if not meta:
            return None
        return {
            "class": obj.severity_class,
            "label_en": meta["label_en"],
            "label_ne": meta["label_ne"],
            "color": meta["color"],
        }
