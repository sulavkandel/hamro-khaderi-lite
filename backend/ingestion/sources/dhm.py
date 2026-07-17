"""DHM (Department of Hydrology and Meteorology, Nepal) adapter — STUB.

DHM has no public programmatic API today. When one becomes available
(or a data-sharing agreement is signed), implement ``fetch_daily`` here
and set ``WEATHER_SOURCE=dhm``. Nothing else in the codebase changes.
"""
from __future__ import annotations

import datetime as dt

from .base import Observation, WeatherSource


class DHMSource(WeatherSource):
    name = "dhm"

    def fetch_daily(
        self,
        lat: float,
        lng: float,
        from_date: dt.date,
        to_date: dt.date,
    ) -> list[Observation]:
        raise NotImplementedError(
            "DHM adapter is a stub. Implement once DHM exposes a data API, "
            "then switch with WEATHER_SOURCE=dhm."
        )
