"use client";
/** Chart.js SPI bar chart, colored per McKee severity class. */
import { useEffect, useRef } from "react";
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import type { SeriesPoint, SeverityMeta } from "@/lib/api";

Chart.register(BarController, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

export default function SpiChart({
  series,
  severityMeta,
  title,
}: {
  series: SeriesPoint[];
  severityMeta: SeverityMeta;
  title: string;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const chartRef = useRef<Chart | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    chartRef.current?.destroy();
    const points = series.filter((p) => p.spi !== null);
    chartRef.current = new Chart(canvasRef.current, {
      type: "bar",
      data: {
        labels: points.map((p) => p.period),
        datasets: [
          {
            label: title,
            data: points.map((p) => p.spi),
            backgroundColor: points.map(
              (p) => severityMeta[p.severity]?.color ?? "#9ca3af"
            ),
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            suggestedMin: -3,
            suggestedMax: 3,
            title: { display: true, text: "SPI" },
          },
          x: { ticks: { maxTicksLimit: 18 } },
        },
        plugins: { legend: { display: false } },
      },
    });
    return () => chartRef.current?.destroy();
  }, [series, severityMeta, title]);

  return (
    <div className="chart-wrap">
      <canvas ref={canvasRef} />
    </div>
  );
}
