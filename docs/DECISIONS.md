# Architecture Decision Records — Hamro Khaderi-Lite

Each decision was made by asking: *is the "obvious" choice actually
necessary for a 3-district weekly-cadence prototype?*

## ADR-1: APScheduler instead of Celery + Redis

**Context.** The spec needs exactly one scheduled job: Thursday 06:00,
ingest + recompute. Celery requires a broker (Redis/RabbitMQ), a worker
process, and beat — three extra moving parts.

**Decision.** `django-apscheduler` with a `BackgroundScheduler` inside the
web process, guarded by `SCHEDULER_AUTOSTART` so tests/management commands
never start it. `DjangoJobStore` persists job state across restarts.

**Consequences.** One process to deploy. If the project ever needs retries
with backoff across many jobs, task fan-out, or multi-node workers, revisit
Celery. The `weekly_pipeline()` function is scheduler-agnostic, so a
migration would touch only `scheduler.py`.

## ADR-2: Hand-rolled scipy SPI instead of `climate-indices`

**Context.** The `climate-indices` package implements SPI but drags in
numba/llvmlite — heavy native builds, Python-version sensitivity, slow cold
installs (a real pain in CI and small VMs).

**Decision.** Implement SPI directly (~120 lines, `spi/compute.py`):
monthly totals → rolling k-month sums → per-calendar-month gamma MLE fit
(`floc=0`) with a zero-rain mixture `H(x) = q + (1-q)G(x)` → `Φ⁻¹` → clamp
±3.5. Guards: minimum 5 yearly samples per month group, zero-variance
(degenerate) groups return None instead of crashing scipy's brentq.

**Consequences.** Full control and testability (42 tests include
statistical sanity checks: SPI ≈ N(0,1) over history; a forced dry year
must classify severe/extreme). Trade-off: we own the math. Mitigated by
McKee (1993) being a stable, well-documented standard.

## ADR-3: Open-Meteo as default source, DHM as stub adapter

**Context.** DHM has no public programmatic API. The tool is inspired by
DHM's Khaderi Monitoring Tool but must work today.

**Decision.** `WeatherSource` ABC with `fetch_daily(lat, lng, from, to)`.
`OpenMeteoSource` (ERA5 reanalysis, free, no key, ~5-day lag) is default;
`DHMSource` raises NotImplementedError with instructions. Provider chosen
via `WEATHER_SOURCE` env var through a registry.

**Consequences.** Swapping providers is config, not code. ERA5 reanalysis
at a district centroid is coarser than station data — acceptable for a
prototype, disclosed in the UI footer and About page.

## ADR-4: Three districts, centroid point sampling (no kriging)

**Context.** The real Khaderi tool covers all 77 districts with station
interpolation.

**Decision.** Pilot with Kailali, Bardiya, Kapilvastu (drought-prone Terai,
west-to-east spread) and sample one point at each district centroid.

**Consequences.** The data model (`districts` table) already scales to 77
rows — adding districts is a seed change. Future work: replace centroid
sampling with station kriging or gridded zonal statistics; that lives
entirely inside the ingestion layer.

## ADR-5: Weekly Thursday snapshots stored, not computed on request

**Context.** SPI for a district/scale changes only when new data arrives
(weekly). Computing on every request wastes CPU and makes response times
depend on scipy.

**Decision.** `spi_snapshots` table keyed (district, computed_for Thursday,
scale) with a uniqueness constraint; the API reads snapshots for
`current`/`map` endpoints. The full-history `/spi/` endpoint computes
on the fly (cheap: one district, cached daily rows) so charts always show
the entire record without storing thousands of snapshot rows.

**Consequences.** Fast map/current endpoints; history endpoint stays fresh.
If history endpoints become hot, add per-(district, scale) caching.

## ADR-6: `{data, meta, errors}` envelope everywhere

**Context.** Mixed response shapes force frontend special-casing.

**Decision.** Every endpoint — success or error — returns the same envelope.
Severity metadata (labels EN/NE + colors) ships in `meta.severity_meta` so
the frontend never hardcodes the palette.

**Consequences.** One fetch wrapper in `lib/api.ts`; bilingual labels and
colors stay single-sourced in `spi/severity.py`.

## ADR-7: PostgreSQL default with SQLite escape hatch

**Context.** Production wants PostgreSQL; CI and quick local runs want
zero setup.

**Decision.** Postgres by default (env-configurable), `USE_SQLITE=1` flips
to SQLite. The ORM layer keeps the schema portable; the only
Postgres-specific feature used is `bulk_create(update_conflicts=True)`,
which Django also supports on SQLite 3.24+.

**Consequences.** CI can run either way; developers without Postgres are
not blocked.
