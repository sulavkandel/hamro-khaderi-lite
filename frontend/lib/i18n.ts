/**
 * हल्का द्विभाषी (EN/NE) अनुवाद तालिका — प्रोटोटाइपका लागि भारी i18n
 * लाइब्रेरी आवश्यक छैन; एउटा React context र यो शब्दकोश नै पर्याप्त छ।
 */
export type Lang = "en" | "ne";

export const STRINGS: Record<string, { en: string; ne: string }> = {
  app_title: { en: "Hamro Khaderi-Lite", ne: "हाम्रो खडेरी-लाइट" },
  tagline: {
    en: "District-level drought monitoring for Nepal's Terai",
    ne: "नेपालको तराईका जिल्लाहरूको खडेरी अनुगमन",
  },
  nav_home: { en: "Dashboard", ne: "ड्यासबोर्ड" },
  nav_about: { en: "About SPI", ne: "SPI बारे" },
  last_updated: { en: "Last updated (Thursday)", ne: "पछिल्लो अद्यावधिक (बिहीबार)" },
  districts: { en: "Districts", ne: "जिल्लाहरू" },
  spi_scale: { en: "SPI Scale", ne: "SPI स्केल" },
  months: { en: "months", ne: "महिना" },
  view_details: { en: "View details", ne: "विवरण हेर्नुहोस्" },
  no_data: { en: "No data", ne: "तथ्याङ्क छैन" },
  loading: { en: "Loading…", ne: "लोड हुँदैछ…" },
  error_loading: {
    en: "Could not load data. Is the API running?",
    ne: "तथ्याङ्क लोड गर्न सकिएन। API चलिरहेको छ?",
  },
  disclaimer: {
    en: "Prototype — not an official DHM product. Data: Open-Meteo (ERA5 reanalysis). For research/education only.",
    ne: "प्रोटोटाइप — यो DHM को आधिकारिक उत्पादन होइन। तथ्याङ्क: Open-Meteo (ERA5)। अनुसन्धान/शिक्षाका लागि मात्र।",
  },
  spi_history: { en: "SPI history", ne: "SPI इतिहास" },
  current_conditions: { en: "Current conditions", ne: "हालको अवस्था" },
  back_to_map: { en: "Back to map", ne: "नक्सामा फर्कनुहोस्" },
  province: { en: "Province", ne: "प्रदेश" },
  legend: { en: "Severity legend", ne: "गम्भीरता सूची" },
};

export function t(key: string, lang: Lang): string {
  return STRINGS[key]?.[lang] ?? key;
}
