"use client";
/** Dashboard: Leaflet map + district list + scale switcher. */
import { useCallback, useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { fetchMap, type MapFeature, type SeverityMeta } from "@/lib/api";
import { useLang } from "@/components/LangContext";
import { t } from "@/lib/i18n";

// Leaflet is browser-only: load without SSR.
const DroughtMap = dynamic(() => import("@/components/DroughtMap"), {
  ssr: false,
  loading: () => <div className="map-wrap card">Loading map…</div>,
});

const SCALES = [3, 6, 12];

export default function DashboardPage() {
  const { lang } = useLang();
  const [scale, setScale] = useState(3);
  const [features, setFeatures] = useState<MapFeature[]>([]);
  const [severityMeta, setSeverityMeta] = useState<SeverityMeta>({});
  const [computedFor, setComputedFor] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (s: number) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchMap(s);
      setFeatures(res.data.features);
      setSeverityMeta((res.meta.severity_meta as SeverityMeta) ?? {});
      setComputedFor((res.meta.computed_for as string) ?? null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load(scale);
  }, [scale, load]);

  return (
    <>
      <section id="hero-section">
        <h1>{t("tagline", lang)}</h1>
        {computedFor && (
          <div className="banner" id="last-updated-banner">
            📅 {t("last_updated", lang)}: <strong>{computedFor}</strong> — SPI-{scale}
          </div>
        )}
      </section>

      <div className="scale-buttons" id="scale-switcher" role="tablist">
        {SCALES.map((s) => (
          <button
            key={s}
            className={s === scale ? "active" : ""}
            onClick={() => setScale(s)}
            role="tab"
            aria-selected={s === scale}
          >
            SPI-{s}
          </button>
        ))}
      </div>

      {error && <div className="card" style={{ color: "#b91c1c" }}>{t("error_loading", lang)} — {error}</div>}

      <div className="grid">
        <section className="card" id="map-section" aria-label="Drought map">
          <DroughtMap features={features} />
        </section>

        <aside id="district-list" className="card">
          <h2 style={{ marginTop: 0 }}>{t("districts", lang)}</h2>
          {loading && <p className="muted">{t("loading", lang)}</p>}
          {features.map((f) => {
            const p = f.properties;
            const name = lang === "ne" ? p.name_ne : p.name_en;
            const label =
              lang === "ne"
                ? p.severity_label_ne ?? t("no_data", lang)
                : p.severity_label_en ?? t("no_data", lang);
            return (
              <div className="district-row" key={p.slug}>
                <div>
                  <Link href={`/district/${p.slug}`}>
                    <strong>{name}</strong>
                  </Link>
                  <div className="muted">
                    SPI-{scale}: {p.spi_value != null ? p.spi_value.toFixed(2) : "—"}
                  </div>
                </div>
                <span
                  className="severity-pill"
                  style={{ backgroundColor: p.severity_color }}
                >
                  {label}
                </span>
              </div>
            );
          })}

          <h3>{t("legend", lang)}</h3>
          <table className="legend">
            <tbody>
              {Object.entries(severityMeta)
                .sort((a, b) => a[1].order - b[1].order)
                .map(([key, m]) => (
                  <tr key={key}>
                    <td>
                      <span className="swatch" style={{ backgroundColor: m.color }} />
                    </td>
                    <td>{lang === "ne" ? m.label_ne : m.label_en}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </aside>
      </div>
    </>
  );
}
