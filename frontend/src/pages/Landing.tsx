// EVA-STORY: ACA-05-016
import { useTranslation } from "react-i18next";
import {
  Title1,
  Text,
  Button,
  Card,
  CardHeader,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { trackPageView, trackEvent } from "../telemetry/analytics";
import { formatCurrency } from "../i18n";
import { LanguageSelector } from "../components/LanguageSelector";

const useStyles = makeStyles({
  root: {
    maxWidth: "1024px",
    margin: "0 auto",
    padding: `${tokens.spacingVerticalXXL} ${tokens.spacingHorizontalL}`,
  },
  hero: {
    textAlign: "center",
    marginBottom: tokens.spacingVerticalXXL,
  },
  tierGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
    gap: tokens.spacingHorizontalL,
    marginTop: tokens.spacingVerticalXL,
  },
  tierCard: {
    padding: tokens.spacingVerticalL,
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: tokens.spacingVerticalL,
  },
});

export default function Landing() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const styles = useStyles();

  useEffect(() => {
    trackPageView("/", t("app.title"));
  }, [t]);

  const tiers = [
    {
      key: "free",
      name: t("tiers.free.name"),
      description: t("tiers.free.description"),
      price: t("actions.connect_subscription"),
      onSelect: () => navigate("/connect"),
    },
    {
      key: "standard",
      name: t("tiers.standard.name"),
      description: t("tiers.standard.description"),
      price: t("tiers.standard.price_onetime", {
        amount: formatCurrency(499, "CAD"),
      }),
      onSelect: () => {
        trackEvent("tier_viewed", { tier: "standard" });
        navigate("/checkout?tier=2");
      },
    },
    {
      key: "professional",
      name: t("tiers.professional.name"),
      description: t("tiers.professional.description"),
      price: t("tiers.professional.price_onetime", {
        amount: formatCurrency(1499, "CAD"),
      }),
      onSelect: () => {
        trackEvent("tier_viewed", { tier: "professional" });
        navigate("/checkout?tier=3");
      },
    },
  ];

  return (
    <main className={styles.root}>
      <header className={styles.header}>
        <Text weight="semibold">{t("app.title")}</Text>
        <LanguageSelector />
      </header>
      <section className={styles.hero} aria-labelledby="hero-heading">
        <Title1 id="hero-heading">{t("app.title")}</Title1>
        <Text size={400}>{t("app.tagline")}</Text>
      </section>
      {/* Tier cards */}
      <ul className={styles.tierGrid} role="list" aria-label="Service tiers">
        {tiers.map((tier) => (
          <li key={tier.key} style={{ listStyle: "none" }}>
            <Card className={styles.tierCard}>
              <CardHeader header={<Text weight="semibold">{tier.name}</Text>} />
              <Text>{tier.description}</Text>
              <Text weight="semibold" block style={{ marginTop: tokens.spacingVerticalM }}>
                {tier.price}
              </Text>
              <Button
                appearance={tier.key === "standard" ? "primary" : "secondary"}
                onClick={tier.onSelect}
                style={{ marginTop: tokens.spacingVerticalM }}
              >
                {tier.key === "free" ? t("actions.connect_subscription") : t("actions.upgrade")}
              </Button>
            </Card>
          </li>
        ))}
      </ul>
    </main>
  );
}
