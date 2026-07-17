"use client";
import Link from "next/link";
import { useLang } from "./LangContext";
import { t } from "@/lib/i18n";

export default function Nav() {
  const { lang, setLang } = useLang();
  return (
    <header id="site-header" className="site-header">
      <nav className="nav-inner">
        <Link href="/" className="brand">
          🌾 {t("app_title", lang)}
        </Link>
        <div className="nav-links">
          <Link href="/">{t("nav_home", lang)}</Link>
          <Link href="/about">{t("nav_about", lang)}</Link>
          <button
            id="lang-toggle"
            className="lang-toggle"
            onClick={() => setLang(lang === "en" ? "ne" : "en")}
            aria-label="Toggle language"
          >
            {lang === "en" ? "नेपाली" : "English"}
          </button>
        </div>
      </nav>
    </header>
  );
}
