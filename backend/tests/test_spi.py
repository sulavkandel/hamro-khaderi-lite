"""Unit tests for SPI computation and severity classification."""
import datetime as dt

import numpy as np
import pytest

from spi.compute import monthly_totals, rolling_sums, spi_series
from spi.severity import classify


class TestSeverity:
    @pytest.mark.parametrize("spi,expected", [
        (-3.0, "extreme_dry"),
        (-2.0, "extreme_dry"),     # boundary: <= -2.0
        (-1.99, "severe_dry"),
        (-1.5, "severe_dry"),      # boundary: <= -1.5
        (-1.49, "moderate_dry"),
        (-1.0, "moderate_dry"),    # boundary: <= -1.0
        (-0.99, "near_normal"),
        (0.0, "near_normal"),
        (0.99, "near_normal"),
        (1.0, "moderate_wet"),     # boundary: >= 1.0
        (1.49, "moderate_wet"),
        (1.5, "severe_wet"),       # boundary: >= 1.5
        (1.99, "severe_wet"),
        (2.0, "extreme_wet"),      # boundary: >= 2.0
        (3.0, "extreme_wet"),
        (None, "no_data"),
    ])
    def test_classify(self, spi, expected):
        assert classify(spi) == expected


def synthetic_daily(years=15, seed=42, dry_last_year=False):
    """Synthetic monsoon-like daily precipitation for `years` years.

    Monsoon (Jun-Sep) is wet, winter is dry — like the Terai.
    """
    rng = np.random.default_rng(seed)
    daily = {}
    start = dt.date(2010, 1, 1)
    end = dt.date(2010 + years - 1, 12, 31)
    day = start
    while day <= end:
        monsoon = day.month in (6, 7, 8, 9)
        base = 12.0 if monsoon else 0.6
        # gamma-ish daily rain with many dry days
        wet = rng.random() < (0.55 if monsoon else 0.12)
        value = float(rng.gamma(0.9, base)) if wet else 0.0
        if dry_last_year and day.year == end.year:
            value *= 0.05  # severe drought in the final year
        daily[day] = value
        day += dt.timedelta(days=1)
    return daily


class TestMonthlyTotals:
    def test_sums_by_month(self):
        daily = {
            dt.date(2020, 1, 1): 5.0,
            dt.date(2020, 1, 15): 10.0,
            dt.date(2020, 2, 1): 3.0,
        }
        totals = monthly_totals(daily)
        assert totals[(2020, 1)] == 15.0
        assert totals[(2020, 2)] == 3.0

    def test_none_values_skipped(self):
        daily = {
            dt.date(2020, 1, 1): 5.0,
            dt.date(2020, 1, 2): None,
        }
        totals = monthly_totals(daily)
        assert totals[(2020, 1)] == 5.0


class TestRollingSums:
    def test_requires_consecutive_months(self):
        totals = monthly_totals({
            dt.date(2020, 1, 1): 10.0,
            dt.date(2020, 2, 1): 20.0,
            dt.date(2020, 3, 1): 30.0,
            # gap: no April
            dt.date(2020, 5, 1): 50.0,
        })
        sums = rolling_sums(totals, 3)
        assert sums[(2020, 3)] == 60.0
        assert (2020, 5) not in sums  # window crosses the gap

    def test_year_boundary(self):
        totals = monthly_totals({
            dt.date(2020, 11, 1): 1.0,
            dt.date(2020, 12, 1): 2.0,
            dt.date(2021, 1, 1): 3.0,
        })
        sums = rolling_sums(totals, 3)
        assert sums[(2021, 1)] == 6.0


class TestSpiSeries:
    def test_spi_roughly_standard_normal(self):
        """Over the whole history, SPI should be ~N(0,1)."""
        daily = synthetic_daily(years=20)
        series = spi_series(daily, 3)
        values = np.array([v for v in series.values() if v is not None])
        assert len(values) > 100
        assert abs(float(values.mean())) < 0.35
        assert 0.6 < float(values.std()) < 1.4

    def test_dry_year_flags_drought(self):
        daily = synthetic_daily(years=15, dry_last_year=True)
        series = spi_series(daily, 3)
        # take the last monsoon-season SPI of the dry year
        last_year = max(k[0] for k in series)
        monsoon_keys = [k for k in series if k[0] == last_year and k[1] in (8, 9)]
        vals = [series[k] for k in monsoon_keys if series[k] is not None]
        assert vals, "expected monsoon SPI values in the dry year"
        assert min(vals) < -1.5  # severe or extreme drought detected

    def test_constant_data_does_not_crash(self):
        """Degenerate (zero-variance) data must return None, not raise."""
        daily = {}
        day = dt.date(2010, 1, 1)
        while day <= dt.date(2021, 12, 31):
            daily[day] = 2.0  # identical every single day
            day += dt.timedelta(days=1)
        series = spi_series(daily, 3)
        assert len(series) > 0
        # Note: month lengths differ (leap-year Feb), so a few calendar-month
        # groups are not perfectly constant and may legitimately get a fit.
        # The contract here is: no crash, and every value is None or finite.
        import math
        assert all(v is None or math.isfinite(v) for v in series.values())
        # Truly constant groups (windows without February) must be None.
        assert any(v is None for v in series.values())

    def test_insufficient_history_returns_none(self):
        daily = synthetic_daily(years=2)  # < MIN_YEARS_FOR_FIT
        series = spi_series(daily, 3)
        assert all(v is None for v in series.values())

    def test_clamped_to_3_5(self):
        daily = synthetic_daily(years=20)
        series = spi_series(daily, 12)
        vals = [v for v in series.values() if v is not None]
        assert all(-3.5 <= v <= 3.5 for v in vals)
