# Architecture — Hamro Khaderi-Lite

## Components

```
backend/
├── config/          Django settings (env-driven), urls, wsgi
├── districts/       Models: District, DailyPrecip, SpiSnapshot, IngestionRun
│   └── management/  seed_districts
├── ingestion/       Weather adapters + pipeline + weekly scheduler
│   ├── sources/     base (ABC), open_meteo, dhm (stub), registry
│   └── management/  ingest
├── spi/             SPI math (compute), severity classes, orchestration
│   └── management/  compute_spi
├── api/             DRF views/serializers/urls ({data, meta, errors})
└── tests/           42 tests: SPI math, adapters, API

frontend/
├── app/             Next.js 14 App Router
│   ├── page.tsx             Dashboard: Leaflet map + district list
│   ├── district/[slug]/     Detail: severity cards + SPI-3/6/12 charts
│   └── about/               Bilingual SPI explainer
├── components/      DroughtMap (Leaflet), SpiChart (Chart.js), Nav, i18n context
└── lib/             api.ts (typed client), i18n.ts (EN/NE strings)
```

## Data flow

1. **Ingest** (weekly Thursday 06:00 KTM, or `manage.py ingest`):
   the configured `WeatherSource` fetches daily precipitation per district
   centroid; QC nulls negative/>500mm values; rows upsert into
   `daily_precip`; an `IngestionRun` audit row records ok/partial/failed.
2. **Compute** (`spi/service.py`): daily → monthly totals → rolling 3/6/12
   sums → per-calendar-month gamma fit → SPI. Latest value per scale is
   written to `spi_snapshots` for the current Thursday.
3. **Serve**: DRF endpoints read snapshots (map/current) or compute full
   history (charts). Severity labels/colors ship in `meta.severity_meta`.
4. **Render**: Next.js client pages fetch the API and render Leaflet
   circles + Chart.js bars, colored by the shared severity palette.

## Key invariants

- `daily_precip.precip_mm` NULL ⇢ missing/failed-QC (never conflated with 0.0).
- One snapshot row per (district, Thursday, scale) — enforced by constraint.
- SPI values clamped to ±3.5; unfittable month groups yield None ("No Data").
- All API responses: `{data, meta, errors}`.

## Scheduled job

`ingestion/scheduler.py` registers `weekly_spi_pipeline` (cron: Thu 06:00
Asia/Kathmandu, DjangoJobStore, max_instances=1). Started from
`IngestionConfig.ready()` only when `SCHEDULER_AUTOSTART=1`.
