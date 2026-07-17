"use client";
/**
 * SPI बारे व्याख्या पृष्ठ (द्विभाषी)।
 * नोट: यो पृष्ठ स्थिर सामग्री मात्र हो — API कल आवश्यक छैन।
 */
import { useLang } from "@/components/LangContext";

export default function AboutPage() {
  const { lang } = useLang();

  if (lang === "ne") {
    return (
      <article id="about-article">
        <h1>SPI (मानकीकृत वर्षा सूचकाङ्क) भनेको के हो?</h1>
        <div className="card">
          <p>
            SPI (Standardized Precipitation Index) ले कुनै स्थानको वर्षा
            त्यहाँको ऐतिहासिक औसतभन्दा कति फरक छ भनी मापन गर्छ। शून्य (0)
            भनेको सामान्य, ऋणात्मक मान भनेको सुक्खा (खडेरी), र धनात्मक मान
            भनेको सामान्यभन्दा बढी भिजेको अवस्था हो।
          </p>
          <p>
            यो ड्यासबोर्डले <strong>SPI-3, SPI-6 र SPI-12</strong> देखाउँछ —
            क्रमशः पछिल्लो ३, ६ र १२ महिनाको वर्षामा आधारित। छोटो स्केलले
            कृषि खडेरी (माटोको चिस्यान) र लामो स्केलले जलस्रोत खडेरी
            (जलाशय, भूमिगत पानी) संकेत गर्छ।
          </p>
        </div>
        <div className="card">
          <h2>गम्भीरता वर्गहरू (McKee et al., 1993)</h2>
          <ul>
            <li>SPI ≤ −2.0 — अत्यधिक सुक्खा</li>
            <li>−2.0 &lt; SPI ≤ −1.5 — गम्भीर सुक्खा</li>
            <li>−1.5 &lt; SPI ≤ −1.0 — मध्यम सुक्खा</li>
            <li>−1.0 &lt; SPI &lt; 1.0 — सामान्य नजिक</li>
            <li>1.0 ≤ SPI &lt; 1.5 — मध्यम भिजेको</li>
            <li>1.5 ≤ SPI &lt; 2.0 — गम्भीर भिजेको</li>
            <li>SPI ≥ 2.0 — अत्यधिक भिजेको</li>
          </ul>
        </div>
        <div className="card">
          <h2>तथ्याङ्क स्रोत र सीमाहरू</h2>
          <p>
            वर्षा तथ्याङ्क Open-Meteo (ERA5 पुनर्विश्लेषण) बाट लिइएको हो र
            प्रत्येक बिहीबार अद्यावधिक हुन्छ। यो DHM को आधिकारिक उत्पादन
            होइन — अनुसन्धान र शिक्षाका लागि मात्र प्रयोग गर्नुहोस्।
          </p>
        </div>
      </article>
    );
  }

  return (
    <article id="about-article">
      <h1>What is SPI (Standardized Precipitation Index)?</h1>
      <div className="card">
        <p>
          The SPI measures how much rainfall at a place deviates from its own
          historical average. Zero means normal; negative values mean drier
          than normal (drought); positive values mean wetter than normal.
          Because it is standardized, SPI values are comparable across
          districts with very different climates.
        </p>
        <p>
          This dashboard shows <strong>SPI-3, SPI-6 and SPI-12</strong> —
          based on the last 3, 6 and 12 months of precipitation. Short scales
          track agricultural drought (soil moisture); long scales track
          hydrological drought (reservoirs, groundwater).
        </p>
      </div>
      <div className="card">
        <h2>Severity classes (McKee et al., 1993)</h2>
        <ul>
          <li>SPI ≤ −2.0 — Extremely Dry</li>
          <li>−2.0 &lt; SPI ≤ −1.5 — Severely Dry</li>
          <li>−1.5 &lt; SPI ≤ −1.0 — Moderately Dry</li>
          <li>−1.0 &lt; SPI &lt; 1.0 — Near Normal</li>
          <li>1.0 ≤ SPI &lt; 1.5 — Moderately Wet</li>
          <li>1.5 ≤ SPI &lt; 2.0 — Severely Wet</li>
          <li>SPI ≥ 2.0 — Extremely Wet</li>
        </ul>
      </div>
      <div className="card">
        <h2>How it is computed here</h2>
        <ol>
          <li>Daily precipitation per district centroid (2012 → today).</li>
          <li>Monthly totals, then rolling 3/6/12-month sums.</li>
          <li>
            A gamma distribution is fitted per calendar month (zero-rain months
            handled with a mixture), then transformed to a standard normal —
            that value is the SPI.
          </li>
          <li>Recomputed every Thursday for the latest data.</li>
        </ol>
      </div>
      <div className="card">
        <h2>Data source &amp; limitations</h2>
        <p>
          Rainfall comes from Open-Meteo (ERA5 reanalysis) at each district
          centroid — a prototype simplification (one point per district, no
          station kriging). This is <strong>not</strong> an official DHM
          product; use for research and education only.
        </p>
      </div>
    </article>
  );
}
