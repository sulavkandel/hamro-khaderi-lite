"""SPI (Standardized Precipitation Index) computation — McKee et al. (1993).

Why hand-rolled scipy instead of the `climate-indices` package?
---------------------------------------------------------------
`climate-indices` drags in numba/llvmlite (heavy, slow to build, version
-sensitive). Our need is one index at three scales for three districts —
~40 lines of scipy. See docs/DECISIONS.md.

Method
------
1. Aggregate daily precipitation into calendar-month totals.
2. Rolling k-month sums (k = 3, 6, 12).
3. For each calendar month separately (Jan..Dec), fit a gamma distribution
   to the non-zero historical sums (MLE, floc=0) and estimate q = P(sum=0).
4. Mixture CDF: H(x) = q + (1 - q) * G(x | shape, scale).
5. SPI = Phi^{-1}(H(x)), clamped to +/-3.5 (standard practice — beyond
   that the fitted tails are meaningless).
"""
from __future__ import annotations

import datetime as dt
from collections import OrderedDict

import numpy as np
from scipy import stats

# Need at least this many yearly samples per calendar month to fit a gamma.
MIN_YEARS_FOR_FIT = 5
_SPI_CLAMP = 3.5


def monthly_totals(daily: dict[dt.date, float | None]) -> "OrderedDict[tuple[int, int], float]":
    """Sum daily values into (year, month) totals. None values are skipped
    (treated as missing, not zero)."""
    totals: dict[tuple[int, int], float] = {}
    for day, value in daily.items():
        if value is None:
            continue
        key = (day.year, day.month)
        totals[key] = totals.get(key, 0.0) + float(value)
    return OrderedDict(sorted(totals.items()))


def rolling_sums(
    totals: "OrderedDict[tuple[int, int], float]", k: int
) -> "OrderedDict[tuple[int, int], float]":
    """k-month rolling sums ending at each (year, month).

    A sum is only produced when all k consecutive months are present.
    """
    keys = list(totals.keys())
    out: "OrderedDict[tuple[int, int], float]" = OrderedDict()
    for i in range(k - 1, len(keys)):
        window = keys[i - k + 1 : i + 1]
        # verify the window is truly consecutive months
        ok = True
        for a, b in zip(window, window[1:]):
            nxt = (a[0] + (a[1] == 12), a[1] % 12 + 1)
            if b != nxt:
                ok = False
                break
        if ok:
            out[keys[i]] = sum(totals[m] for m in window)
    return out


def _fit_month_group(values: np.ndarray) -> tuple[float, tuple[float, float] | None]:
    """Fit the zero-mixture gamma for one calendar month's history.

    Returns (q, (shape, scale)) or (q, None) when a fit is impossible
    (all zeros, too few points, or degenerate/constant data).
    """
    n = len(values)
    zeros = int(np.sum(values <= 0.0))
    q = zeros / n if n else 1.0
    nonzero = values[values > 0.0]
    if len(nonzero) < 3:
        return q, None
    # Degenerate guard: constant non-zero data breaks scipy's MLE
    # (digamma root-finding in optimize.brentq raises ValueError).
    if float(np.std(nonzero)) < 1e-9:
        return q, None
    try:
        shape, _loc, scale = stats.gamma.fit(nonzero, floc=0)
    except Exception:
        return q, None
    if not np.isfinite(shape) or not np.isfinite(scale) or shape <= 0 or scale <= 0:
        return q, None
    return q, (shape, scale)


def spi_series(
    daily: dict[dt.date, float | None], scale_months: int
) -> "OrderedDict[tuple[int, int], float | None]":
    """Full SPI series keyed by (year, month) for the given scale.

    Returns None for months where no distribution could be fitted.
    """
    totals = monthly_totals(daily)
    sums = rolling_sums(totals, scale_months)

    # Group the rolling sums by ending calendar month (deseasonalisation).
    by_month: dict[int, list[tuple[tuple[int, int], float]]] = {}
    for key, val in sums.items():
        by_month.setdefault(key[1], []).append((key, val))

    fits: dict[int, tuple[float, tuple[float, float] | None]] = {}
    for month, entries in by_month.items():
        vals = np.array([v for _, v in entries], dtype=float)
        if len(vals) < MIN_YEARS_FOR_FIT:
            fits[month] = (0.0, None)
            continue
        fits[month] = _fit_month_group(vals)

    out: "OrderedDict[tuple[int, int], float | None]" = OrderedDict()
    for key, val in sums.items():
        q, params = fits[key[1]]
        if params is None:
            out[key] = None
            continue
        shape, scale = params
        if val <= 0.0:
            # probability mass at zero: use q/2 (median of the zero block)
            h = max(q / 2.0, 1e-6)
        else:
            g = stats.gamma.cdf(val, shape, loc=0, scale=scale)
            h = q + (1.0 - q) * g
        h = min(max(h, 1e-6), 1.0 - 1e-6)
        spi = float(stats.norm.ppf(h))
        out[key] = float(np.clip(spi, -_SPI_CLAMP, _SPI_CLAMP))
    return out


def latest_spi(
    daily: dict[dt.date, float | None], scale_months: int
) -> tuple[tuple[int, int], float | None] | None:
    """(period, value) of the most recent month in the series, or None."""
    series = spi_series(daily, scale_months)
    if not series:
        return None
    key = next(reversed(series))
    return key, series[key]
