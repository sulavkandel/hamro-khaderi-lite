"""Tests for the weather-source adapter layer (no real network)."""
import datetime as dt
from unittest import mock

import pytest
import requests

from ingestion.sources.base import Observation
from ingestion.sources.dhm import DHMSource
from ingestion.sources.open_meteo import API_URL, OpenMeteoSource
from ingestion.sources.registry import get_source

FIXTURE = {
    "daily": {
        "time": ["2024-06-01", "2024-06-02", "2024-06-03"],
        "precipitation_sum": [12.5, 0.0, None],
    }
}


def make_session(payload=FIXTURE, status=200):
    session = mock.MagicMock(spec=requests.Session)
    resp = mock.MagicMock()
    resp.status_code = status
    resp.json.return_value = payload
    if status >= 400:
        resp.raise_for_status.side_effect = requests.HTTPError(f"{status}")
    else:
        resp.raise_for_status.return_value = None
    session.get.return_value = resp
    return session


class TestOpenMeteoSource:
    def test_fixture_replay(self):
        src = OpenMeteoSource(session=make_session())
        obs = src.fetch_daily(28.68, 80.89, dt.date(2024, 6, 1), dt.date(2024, 6, 3))
        assert obs == [
            Observation(dt.date(2024, 6, 1), 12.5),
            Observation(dt.date(2024, 6, 2), 0.0),
            Observation(dt.date(2024, 6, 3), None),
        ]

    def test_request_params(self):
        session = make_session()
        src = OpenMeteoSource(session=session)
        src.fetch_daily(28.686111, 80.897222, dt.date(2024, 1, 1), dt.date(2024, 1, 31))
        args, kwargs = session.get.call_args
        assert args[0] == API_URL
        params = kwargs["params"]
        assert params["latitude"] == 28.686111
        assert params["longitude"] == 80.897222
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-01-31"
        assert params["daily"] == "precipitation_sum"
        assert params["timezone"] == "Asia/Kathmandu"

    @mock.patch("ingestion.sources.open_meteo.time.sleep")
    def test_retries_then_raises(self, _sleep):
        session = make_session(status=500)
        src = OpenMeteoSource(session=session)
        with pytest.raises(RuntimeError, match="failed after 3 attempts"):
            src.fetch_daily(28.0, 80.0, dt.date(2024, 1, 1), dt.date(2024, 1, 2))
        assert session.get.call_count == 3


class TestRegistry:
    def test_resolves_open_meteo(self):
        assert isinstance(get_source("open_meteo"), OpenMeteoSource)

    def test_resolves_dhm(self):
        assert isinstance(get_source("dhm"), DHMSource)

    def test_unknown_source_raises(self):
        with pytest.raises(ValueError, match="Unknown weather source"):
            get_source("nasa")


class TestDHMStub:
    def test_stub_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            DHMSource().fetch_daily(28.0, 80.0, dt.date(2024, 1, 1), dt.date(2024, 1, 2))
