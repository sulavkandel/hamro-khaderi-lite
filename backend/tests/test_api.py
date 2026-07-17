"""API endpoint tests: envelope shape, data correctness, auth."""
import datetime as dt

import numpy as np
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from districts.models import DailyPrecip, District, SpiSnapshot

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def kailali():
    return District.objects.create(
        slug="kailali", name_en="Kailali", name_ne="कैलाली",
        province="Sudurpaschim",
        centroid_lat="28.686111", centroid_lng="80.897222",
    )


@pytest.fixture
def snapshot(kailali):
    return SpiSnapshot.objects.create(
        district=kailali,
        computed_for=dt.date(2026, 7, 16),
        scale_months=3,
        spi_value=-1.75,
        severity_class="severe_dry",
    )


def assert_envelope(payload):
    assert set(payload.keys()) == {"data", "meta", "errors"}
    assert isinstance(payload["meta"], dict)
    assert isinstance(payload["errors"], list)


class TestDistrictList:
    def test_lists_districts(self, client, kailali):
        resp = client.get("/api/v1/districts/")
        assert resp.status_code == 200
        payload = resp.json()
        assert_envelope(payload)
        assert payload["meta"]["count"] == 1
        assert payload["data"][0]["slug"] == "kailali"
        assert payload["data"][0]["name_ne"] == "कैलाली"


class TestDistrictCurrent:
    def test_latest_snapshot(self, client, kailali, snapshot):
        resp = client.get(f"/api/v1/districts/{kailali.pk}/current/")
        assert resp.status_code == 200
        payload = resp.json()
        assert_envelope(payload)
        assert payload["data"]["computed_for"] == "2026-07-16"
        snap = payload["data"]["snapshots"][0]
        assert snap["spi_value"] == -1.75
        assert snap["severity_class"] == "severe_dry"
        assert snap["severity"]["label_ne"] == "गम्भीर सुक्खा"

    def test_404(self, client):
        resp = client.get("/api/v1/districts/9999/current/")
        assert resp.status_code == 404
        assert resp.json()["errors"][0]["code"] == "not_found"


class TestMapCurrent:
    def test_geojson_coordinates(self, client, kailali, snapshot):
        resp = client.get("/api/v1/map/current/?scale=3")
        assert resp.status_code == 200
        payload = resp.json()
        assert_envelope(payload)
        fc = payload["data"]
        assert fc["type"] == "FeatureCollection"
        feature = fc["features"][0]
        # GeoJSON: [lng, lat]
        assert feature["geometry"]["coordinates"] == [80.897222, 28.686111]
        assert feature["properties"]["severity_color"] == "#dc2626"

    def test_invalid_scale(self, client, kailali):
        resp = client.get("/api/v1/map/current/?scale=7")
        assert resp.status_code == 400
        assert resp.json()["errors"][0]["code"] == "invalid_scale"


class TestSpiSeries:
    def test_invalid_scale(self, client, kailali):
        resp = client.get(f"/api/v1/districts/{kailali.pk}/spi/?scale=99")
        assert resp.status_code == 400

    def test_series_from_daily_data(self, client, kailali):
        # 12 years of VARIED synthetic daily data (constant data would make
        # the gamma fit degenerate — that path is covered in test_spi.py).
        rng = np.random.default_rng(7)
        day = dt.date(2012, 1, 1)
        rows = []
        while day <= dt.date(2023, 12, 31):
            monsoon = day.month in (6, 7, 8, 9)
            base = 10.0 if monsoon else 0.5
            wet = rng.random() < (0.5 if monsoon else 0.1)
            value = float(rng.gamma(0.6, base) * 3) if wet else 0.0
            rows.append(DailyPrecip(
                district=kailali, date=day, precip_mm=value, source="open_meteo",
            ))
            day += dt.timedelta(days=1)
        DailyPrecip.objects.bulk_create(rows)

        resp = client.get(f"/api/v1/districts/{kailali.pk}/spi/?scale=3")
        assert resp.status_code == 200
        payload = resp.json()
        assert_envelope(payload)
        series = payload["data"]["series"]
        assert len(series) > 100
        non_null = [p for p in series if p["spi"] is not None]
        assert len(non_null) > 50
        assert {"period", "spi", "severity"} <= set(series[0].keys())


class TestIngestRunAuth:
    def test_anonymous_rejected(self, client):
        resp = client.post("/api/v1/ingest/run/", {})
        assert resp.status_code in (401, 403)

    def test_authenticated_allowed(self, client, kailali, monkeypatch):
        # Stub network so the endpoint logic runs without Open-Meteo.
        from ingestion.sources.base import Observation

        def fake_fetch(self, lat, lng, frm, to):
            return [Observation(frm, 1.0)]

        monkeypatch.setattr(
            "ingestion.sources.open_meteo.OpenMeteoSource.fetch_daily", fake_fetch
        )
        user = User.objects.create_user("admin", password="x")
        client.force_authenticate(user)
        resp = client.post("/api/v1/ingest/run/", {"days": 2}, format="json")
        assert resp.status_code == 200
        payload = resp.json()
        assert_envelope(payload)
        assert payload["data"]["runs"][0]["district"] == "kailali"


class TestHealth:
    def test_health(self, client):
        resp = client.get("/api/v1/health/")
        assert resp.status_code == 200
        payload = resp.json()
        assert_envelope(payload)
        assert payload["data"]["status"] == "ok"
        assert payload["meta"]["weather_source"]
