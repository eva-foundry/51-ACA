// EVA-STORY: ACA-06-017
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Title2, Text, Button, Spinner, makeStyles, tokens } from "@fluentui/react-components";
import { trackPageView } from "../telemetry/analytics";

const useStyles = makeStyles({
  root: { maxWidth: "600px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
});

export default function BillingPortal() {
  const { t } = useTranslation();
  const styles = useStyles();
  const [loading, setLoading] = useState(false);

  useEffect(() => { trackPageView("/billing", "Billing Portal"); }, []);

  async function openPortal() {
    setLoading(true);
    try {
      const res = await fetch("/v1/billing/portal");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.portal_url) window.location.href = data.portal_url;
    } catch {
      /* handled by API error boundary */
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.root}>
      <Title2>{t("nav.billing")}</Title2>
      <Text block>Manage your subscription, download invoices, and update payment methods via the Stripe billing portal.</Text>
      <Button
        appearance="primary"
        onClick={openPortal}
        disabled={loading}
        style={{ marginTop: tokens.spacingVerticalL }}
        aria-label="Open Stripe billing portal in new tab"
      >
        {loading
          ? <Spinner size="tiny" label={t("a11y.loading")} />
          : t("actions.manage_billing")
        }
      </Button>
    </main>
  );
}
