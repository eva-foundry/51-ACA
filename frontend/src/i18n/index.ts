// EVA-STORY: ACA-09-001
import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import Backend from "i18next-http-backend";

// Supported locales
// Phase 1: en, fr-CA
// Phase 2: pt-BR, es, de
export const SUPPORTED_LOCALES = ["en", "fr", "pt-BR", "es", "de"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

// Supported currencies (display-only; all payments go through Stripe in CAD)
export const CURRENCY_LOCALES: Record<string, string> = {
  en: "en-CA",
  fr: "fr-CA",
  "pt-BR": "pt-BR",
  es: "es",
  de: "de-DE",
};

export const DEFAULT_CURRENCIES: Record<string, string> = {
  en: "CAD",
  fr: "CAD",
  "pt-BR": "BRL",
  es: "USD",
  de: "EUR",
};

/** Format a number as currency for the active locale */
export function formatCurrency(
  amount: number,
  currency?: string,
  locale?: string
): string {
  const resolvedLocale = locale ?? CURRENCY_LOCALES[i18n.language] ?? "en-CA";
  const resolvedCurrency =
    currency ?? DEFAULT_CURRENCIES[i18n.language] ?? "CAD";
  return new Intl.NumberFormat(resolvedLocale, {
    style: "currency",
    currency: resolvedCurrency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "en",
    supportedLngs: SUPPORTED_LOCALES,
    ns: ["translation"],
    defaultNS: "translation",
    backend: {
      loadPath: "/locales/{{lng}}/translation.json",
    },
    interpolation: {
      escapeValue: false, // React handles XSS
    },
    detection: {
      order: ["querystring", "localStorage", "navigator"],
      caches: ["localStorage"],
    },
    react: {
      useSuspense: true,
    },
  });

export default i18n;
