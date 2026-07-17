"""Open-Meteo Historical Weather API adapter.

Free, no API key, global coverage (ERA5-based reanalysis). The archive
lags realtime by roughly 5 days — callers must clamp their window
(see ``ingestion.service.default_ingest_window``).
"""
from __future__ import annotations

import datetime as dt
import time

import requests

from .base import Observation, WeatherSource

API_URL = "https://archive-api.open-meteo.com/v1/archive"
MAX_RETRIES = 3
BACKOFF_SECONDS = 2.0


class OpenMeteoSource(WeatherSource):
    name = "open_meteo"

    def __init__(self, session: requests.Session | None = None):
        # Injectable session -> tests can replay fixtures without network.
        self.session = session or requests.Session()

    def fetch_daily(
        self,
        lat: float,
        lng: float,
        from_date: dt.date,
        to_date: dt.date,
    ) -> list[Observation]:
        params = {
            "latitude": lat,
            "longitude": lng,
            "start_date": from_date.isoformat(),
            "end_date": to_date.isoformat(),
            "daily": "precipitation_sum",
            "timezone": "Asia/Kathmandu",
        }
        payload = self._get_with_retry(params)
        daily = payload.get("daily", {})
        dates = daily.get("time", [])
        precip = daily.get("precipitation_sum", [])
        out: list[Observation] = []
        for d, p in zip(dates, precip):
            out.append(
                Observation(
                    date=dt.date.fromisoformat(d),
                    precip_mm=float(p) if p is not None else None,
                )
            )
        return out

    def _get_with_retry(self, params: dict) -> dict:
        last_exc: Exception | None = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = self.session.get(API_URL, params=params, timeout=30)
                resp.raise_for_status()
                return resp.json()
            except (requests.RequestException, ValueError) as exc:
                last_exc = exc
                if attempt < MAX_RETRIES - 1:
                    time.sleep(BACKOFF_SECONDS * (attempt + 1))
        raise RuntimeError(
            f"Open-Meteo request failed after {MAX_RETRIES} attempts: {last_exc}"
        ) from last_exc
