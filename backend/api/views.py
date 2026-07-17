"""API views.

Every endpoint returns the same envelope::

    {"data": ..., "meta": {...}, "errors": [...]}

so the frontend can handle responses uniformly.
"""
from __future__ import annotations

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from districts.models import District, SpiSnapshot
from spi.severity import SEVERITY_META
from spi.service import full_history_series

from .serializers import DistrictSerializer, SpiSnapshotSerializer

VALID_SCALES = (3, 6, 12)


def envelope(data=None, meta=None, errors=None, status_code=status.HTTP_200_OK):
    return Response(
        {"data": data, "meta": meta or {}, "errors": errors or []},
        status=status_code,
    )


@extend_schema(summary="List districts")
@api_view(["GET"])
def district_list(request):
    qs = District.objects.all().order_by("name_en")
    return envelope(
        data=DistrictSerializer(qs, many=True).data,
        meta={"count": qs.count()},
    )


@extend_schema(summary="SPI time series for a district")
@api_view(["GET"])
def district_spi(request, pk: int):
    try:
        district = District.objects.get(pk=pk)
    except District.DoesNotExist:
        return envelope(
            errors=[{"code": "not_found", "detail": "District not found."}],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    try:
        scale = int(request.GET.get("scale", 3))
    except (TypeError, ValueError):
        scale = -1
    if scale not in VALID_SCALES:
        return envelope(
            errors=[{
                "code": "invalid_scale",
                "detail": f"scale must be one of {VALID_SCALES}",
            }],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    series = full_history_series(district, scale)
    return envelope(
        data={
            "district": DistrictSerializer(district).data,
            "scale_months": scale,
            "series": series,
        },
        meta={
            "count": len(series),
            "severity_meta": SEVERITY_META,
        },
    )


@extend_schema(summary="Latest SPI snapshot for a district (all scales)")
@api_view(["GET"])
def district_current(request, pk: int):
    try:
        district = District.objects.get(pk=pk)
    except District.DoesNotExist:
        return envelope(
            errors=[{"code": "not_found", "detail": "District not found."}],
            status_code=status.HTTP_404_NOT_FOUND,
        )

    latest = (
        SpiSnapshot.objects.filter(district=district)
        .order_by("-computed_for")
        .values_list("computed_for", flat=True)
        .first()
    )
    snapshots = []
    if latest:
        snapshots = SpiSnapshot.objects.filter(
            district=district, computed_for=latest
        ).order_by("scale_months")

    return envelope(
        data={
            "district": DistrictSerializer(district).data,
            "computed_for": latest.isoformat() if latest else None,
            "snapshots": SpiSnapshotSerializer(snapshots, many=True).data,
        },
        meta={"severity_meta": SEVERITY_META},
    )


@extend_schema(summary="GeoJSON of latest SPI per district for the map")
@api_view(["GET"])
def map_current(request):
    try:
        scale = int(request.GET.get("scale", 3))
    except (TypeError, ValueError):
        scale = -1
    if scale not in VALID_SCALES:
        return envelope(
            errors=[{
                "code": "invalid_scale",
                "detail": f"scale must be one of {VALID_SCALES}",
            }],
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    features = []
    computed_for = None
    for district in District.objects.all().order_by("name_en"):
        snap = (
            SpiSnapshot.objects.filter(district=district, scale_months=scale)
            .order_by("-computed_for")
            .first()
        )
        props = DistrictSerializer(district).data
        if snap:
            computed_for = computed_for or snap.computed_for
            meta = SEVERITY_META.get(snap.severity_class, {})
            props.update({
                "spi_value": snap.spi_value,
                "severity_class": snap.severity_class,
                "severity_label_en": meta.get("label_en"),
                "severity_label_ne": meta.get("label_ne"),
                "severity_color": meta.get("color"),
                "computed_for": snap.computed_for.isoformat(),
            })
        else:
            props.update({
                "spi_value": None,
                "severity_class": None,
                "severity_color": "#9ca3af",
                "computed_for": None,
            })
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                # GeoJSON order: [lng, lat]
                "coordinates": [
                    float(district.centroid_lng),
                    float(district.centroid_lat),
                ],
            },
            "properties": props,
        })

    return envelope(
        data={"type": "FeatureCollection", "features": features},
        meta={
            "scale_months": scale,
            "computed_for": computed_for.isoformat() if computed_for else None,
            "severity_meta": SEVERITY_META,
        },
    )


@extend_schema(summary="Trigger ingestion + SPI compute (auth required)")
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ingest_run(request):
    from ingestion.service import default_ingest_window, ingest_range
    from spi.service import compute_all

    days = int(request.data.get("days", 14))
    frm, to = default_ingest_window(days)
    runs = ingest_range(frm, to)
    computed = compute_all()
    return envelope(
        data={
            "ingested_from": frm.isoformat(),
            "ingested_to": to.isoformat(),
            "runs": [
                {"district": r.district.slug, "status": r.status,
                 "rows_upserted": r.rows_upserted}
                for r in runs
            ],
            "snapshots_computed": computed,
        },
        meta={"triggered_at": timezone.now().isoformat()},
    )


@extend_schema(summary="Health check")
@api_view(["GET"])
def health(request):
    return envelope(
        data={"status": "ok"},
        meta={
            "time": timezone.now().isoformat(),
            "weather_source": settings.WEATHER_SOURCE,
        },
    )
