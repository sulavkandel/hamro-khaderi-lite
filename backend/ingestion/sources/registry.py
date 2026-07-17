"""Provider registry: resolve a WeatherSource by name (env-driven)."""
from __future__ import annotations

from .base import WeatherSource
from .dhm import DHMSource
from .open_meteo import OpenMeteoSource

_SOURCES: dict[str, type[WeatherSource]] = {
    "open_meteo": OpenMeteoSource,
    "dhm": DHMSource,
}


def get_source(name: str) -> WeatherSource:
    try:
        cls = _SOURCES[name]
    except KeyError:
        raise ValueError(
            f"Unknown weather source '{name}'. Available: {sorted(_SOURCES)}"
        ) from None
    return cls()
