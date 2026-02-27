// EVA-STORY: ACA-09-003
import { useTranslation } from "react-i18next";
import {
  Select,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { SUPPORTED_LOCALES, type SupportedLocale } from "../i18n";
import { trackEvent } from "../telemetry/analytics";

const LOCALE_LABELS: Record<SupportedLocale, string> = {
  en: "English",
  fr: "Francais",
  "pt-BR": "Portugues (Brasil)",
  es: "Espanol",
  de: "Deutsch",
};

const useStyles = makeStyles({
  root: {
    display: "flex",
    alignItems: "center",
    gap: tokens.spacingHorizontalXS,
  },
});

export function LanguageSelector() {
  const { i18n, t } = useTranslation();
  const styles = useStyles();

  function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const next = e.target.value as SupportedLocale;
    i18n.changeLanguage(next);
    trackEvent("language_changed", { locale: next });
  }

  return (
    <div className={styles.root}>
      <label htmlFor="lang-selector" style={{ position: "absolute", width: 1, height: 1, overflow: "hidden" }}>
        {t("nav.language")}
      </label>
      <Select
        id="lang-selector"
        value={i18n.language}
        onChange={handleChange}
        aria-label={t("nav.language")}
      >
        {SUPPORTED_LOCALES.map((l) => (
          <option key={l} value={l}>
            {LOCALE_LABELS[l]}
          </option>
        ))}
      </Select>
    </div>
  );
}
