"use client";
/** District detail: severity cards for the latest Thursday + SPI-3/6/12 charts. */
import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  fetchCurrent,
  fetchDistricts,
  fetchSeries,
  type District,
  type SeriesPoint,
  type SeverityMeta,
  type Snapshot,
} from "@/lib/api";
import SpiChart from "@/components/SpiChart";
import { useLang } from "@/components/LangContext";
import { t } from "@/lib/i18n";

const SCALES = [3, 6, 12];

export default function DistrictPage() {
  const params = useParams<{ slug: string }>();
  const { lang } = useLang();
  const [district, setDistrict] = useState<District | null>(null);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [computedFor, setComputedFor] = useState<string | null>(null);
  const [series, setSeries] = useState<Record<number, SeriesPoint[]>>({});
  const [severityMeta, setSeverityMeta] = useState<SeverityMeta>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const list = await fetchDistricts();
        const d = list.data.find((x) => x.slug === params.slug);
        if (!d) {
          setError("District not found");
          return;
        }
        setDistrict(d);
        const cur = await fetchCurrent(d.id);
        setSnapshots(cur.data.snapshots);
        setComputedFor(cur.data.computed_for);
        setSeverityMeta((cur.meta.severity_meta as SeverityMeta) ?? {});
        const results = await Promise.all(SCALES.map((s) => fetchSeries(d.id, s)));
        const bySc: Record<number, SeriesPoint[]> = {};
        results.forEach((r, i) => {
          bySc[SCALES[i]] = r.data.series;
        });
        setSeries(bySc);
      } catch (e) {
        setError((e as Error).message);
      }
    })();
  }, [params.slug]);

  if (error) return <div className="card" style={{ color: "#b91c1c" }}>{error}</div>;
  if (!district) return <div className="card">{t("loading", lang)}</div>;

  const name = lang === "ne" ? district.name_ne : district.name_en;

  return (
    <>
      <p>
        <Link href="/">← {t("back_to_map", lang)}</Link>
      </p>
      <section id="district-header">
        <h1 style={{ marginBottom: 0 }}>{name}</h1>
        <p className="muted">
          {t("province", lang)}: {district.province}
          {computedFor && <> · {t("last_updated", lang)}: {computedFor}</>}
        </p>
      </section>

      <section id="current-conditions" aria-label="Current conditions">
        <h2>{t("current_conditions", lang)}</h2>
        <div className="cards-3">
          {snapshots.map((s) => (
            <div className="card" key={s.scale_months} style={{ textAlign: "center" }}>
              <div className="muted">SPI-{s.scale_months}</div>
              <div className="spi-big">
                {s.spi_value != null ? s.spi_value.toFixed(2) : "—"}
              </div>
              <span
                className="severity-pill"
                style={{ backgroundColor: s.severity?.color ?? "#9ca3af" }}
              >
                {lang === "ne"
                  ? s.severity?.label_ne ?? t("no_data", lang)
                  : s.severity?.label_en ?? t("no_data", lang)}
              </span>
            </div>
          ))}
          {snapshots.length === 0 && <p className="muted">{t("no_data", lang)}</p>}
        </div>
      </section>

      <section id="spi-history" aria-label="SPI history charts">
        <h2>{t("spi_history", lang)}</h2>
        {SCALES.map((s) => (
          <div className="card" key={s}>
            <h3 style={{ marginTop: 0 }}>SPI-{s} ({s} {t("months", lang)})</h3>
            {series[s] ? (
              <SpiChart series={series[s]} severityMeta={severityMeta} title={`SPI-${s}`} />
            ) : (
              <p className="muted">{t("loading", lang)}</p>
            )}
          </div>
        ))}
      </section>
    </>
  );
}
