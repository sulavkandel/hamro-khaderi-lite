"use client";
/**
 * Leaflet drought map. Client-only (Leaflet touches `window`), so the
 * dashboard imports it with next/dynamic { ssr: false }.
 */
import { useEffect, useRef } from "react";
import L from "leaflet";
import type { MapFeature } from "@/lib/api";
import { useLang } from "./LangContext";

export default function DroughtMap({ features }: { features: MapFeature[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const layerRef = useRef<L.LayerGroup | null>(null);
  const { lang } = useLang();

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    const map = L.map(containerRef.current).setView([28.2, 81.7], 7);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://openstreetmap.org">OpenStreetMap</a>',
      maxZoom: 12,
    }).addTo(map);
    mapRef.current = map;
    layerRef.current = L.layerGroup().addTo(map);
    return () => {
      map.remove();
      mapRef.current = null;
      layerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const layer = layerRef.current;
    if (!layer) return;
    layer.clearLayers();
    for (const f of features) {
      const [lng, lat] = f.geometry.coordinates;
      const p = f.properties;
      const name = lang === "ne" ? p.name_ne : p.name_en;
      const label =
        lang === "ne"
          ? p.severity_label_ne ?? "तथ्याङ्क छैन"
          : p.severity_label_en ?? "No data";
      const spiText = p.spi_value != null ? p.spi_value.toFixed(2) : "—";
      L.circleMarker([lat, lng], {
        radius: 16,
        color: "#334155",
        weight: 1.5,
        fillColor: p.severity_color,
        fillOpacity: 0.85,
      })
        .bindPopup(
          `<strong>${name}</strong><br/>SPI: ${spiText}<br/>${label}<br/>` +
            `<a href="/district/${p.slug}">→ details</a>`
        )
        .bindTooltip(name, { permanent: true, direction: "bottom", offset: [0, 14] })
        .addTo(layer);
    }
  }, [features, lang]);

  return <div ref={containerRef} className="map-wrap" id="drought-map" />;
}
