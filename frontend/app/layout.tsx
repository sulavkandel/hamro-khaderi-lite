import type { Metadata } from "next";
import "./globals.css";
import "leaflet/dist/leaflet.css";
import { LangProvider } from "@/components/LangContext";
import Nav from "@/components/Nav";
import Footer from "@/components/Footer";

export const metadata: Metadata = {
  title: "Hamro Khaderi-Lite — Terai Drought Monitor",
  description:
    "District-level SPI drought monitoring dashboard for Nepal's Terai (prototype).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <LangProvider>
          <Nav />
          <main id="main-content">{children}</main>
          <Footer />
        </LangProvider>
      </body>
    </html>
  );
}
