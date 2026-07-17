"use client";
import { useLang } from "./LangContext";
import { t } from "@/lib/i18n";

export default function Footer() {
  const { lang } = useLang();
  return (
    <footer className="site-footer">
      <p>{t("disclaimer", lang)}</p>
    </footer>
  );
}
