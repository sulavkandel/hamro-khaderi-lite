"""Weather source adapter interface.

Any provider (Open-Meteo today, DHM tomorrow) implements ``WeatherSource``.
The rest of the system only ever sees ``Observation`` objects, so swapping
providers is a one-line env-var change (``WEATHER_SOURCE``).
"""
from __future__ import annotations

import datetime as dt
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Observation:
    date: dt.date
    precip_mm: float | None  # None = missing at the provider


class WeatherSource(ABC):
    """Adapter contract for daily precipitation providers."""

    name: str = "base"

    @abstractmethod
    def fetch_daily(
        self,
        lat: float,
        lng: float,
        from_date: dt.date,
        to_date: dt.date,
    ) -> list[Observation]:
        """Return one Observation per day in [from_date, to_date]."""
        raise NotImplementedError
