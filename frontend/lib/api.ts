/** Typed API client for the Khaderi-Lite backend. */

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1";

export interface Envelope<T> {
  data: T;
  meta: Record<string, unknown>;
  errors: { code: string; detail: string }[];
}

export interface District {
  id: number;
  slug: string;
  name_en: string;
  name_ne: string;
  province: string;
  centroid_lat: string;
  centroid_lng: string;
}

export interface SeverityInfo {
  class: string;
  label_en: string;
  label_ne: string;
  color: string;
}

export interface Snapshot {
  computed_for: string;
  scale_months: number;
  spi_value: number | null;
  severity_class: string;
  severity: SeverityInfo | null;
}

export interface SeriesPoint {
  period: string; // "YYYY-MM"
  spi: number | null;
  severity: string;
}

export interface MapFeature {
  type: "Feature";
  geometry: { type: "Point"; coordinates: [number, number] };
  properties: District & {
    spi_value: number | null;
    severity_class: string | null;
    severity_label_en?: string;
    severity_label_ne?: string;
    severity_color: string;
    computed_for: string | null;
  };
}

export type SeverityMeta = Record<
  string,
  { label_en: string; label_ne: string; color: string; order: number }
>;

async function get<T>(path: string): Promise<Envelope<T>> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    const detail = body?.errors?.[0]?.detail ?? res.statusText;
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json();
}

export const fetchDistricts = () => get<District[]>("/districts/");

export const fetchCurrent = (id: number) =>
  get<{ district: District; computed_for: string | null; snapshots: Snapshot[] }>(
    `/districts/${id}/current/`
  );

export const fetchSeries = (id: number, scale: number) =>
  get<{ district: District; scale_months: number; series: SeriesPoint[] }>(
    `/districts/${id}/spi/?scale=${scale}`
  );

export const fetchMap = (scale: number) =>
  get<{ type: "FeatureCollection"; features: MapFeature[] }>(
    `/map/current/?scale=${scale}`
  );
