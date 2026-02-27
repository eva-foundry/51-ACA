import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Title2, Text, Button, RadioGroup, Radio,
  Card, CardHeader, makeStyles, tokens, Spinner,
} from "@fluentui/react-components";
import { trackPageView, trackEvent } from "../telemetry/analytics";
import { formatCurrency } from "../i18n";

const useStyles = makeStyles({
  root: { maxWidth: "600px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
  tierOptions: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalM },
  priceCard: { padding: tokens.spacingVerticalM },
});

export default function Checkout() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const styles = useStyles();
  const [tier, setTier] = useState(params.get("tier") ?? "2");
  const [billingMode, setBillingMode] = useState<"onetime" | "subscription">("onetime");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    trackPageView("/checkout", "Checkout");
    trackEvent("checkout_started", { tier });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleCheckout() {
    setLoading(true);
    try {
      const endpoint = tier === "3" ? "/v1/checkout/tier3" : "/v1/checkout/tier2";
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ billing_mode: billingMode }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      // Redirect to Stripe Checkout hosted page
      if (data.checkout_url) {
        trackEvent("purchase", { tier, billing_mode: billingMode });
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      console.error("Checkout error", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.root}>
      <Title2 id="checkout-heading">{t("actions.upgrade")}</Title2>
      <div className={styles.tierOptions} role="region" aria-labelledby="checkout-heading">
        {/* Tier selector */}
        <fieldset style={{ border: "none", padding: 0 }}>
          <legend><Text weight="semibold">Select tier</Text></legend>
          <RadioGroup value={tier} onChange={(_, d) => setTier(d.value)}>
            <Radio value="2" label={`${t("tiers.standard.name")} -- ${formatCurrency(499, "CAD")} one-time or ${formatCurrency(150, "CAD")}/mo`} />
            <Radio value="3" label={`${t("tiers.professional.name")} -- ${formatCurrency(1499, "CAD")} one-time`} />
          </RadioGroup>
        </fieldset>

        {/* Billing mode (only for Tier 2) */}
        {tier === "2" && (
          <fieldset style={{ border: "none", padding: 0 }}>
            <legend><Text weight="semibold">Billing mode</Text></legend>
            <RadioGroup value={billingMode} onChange={(_, d) => setBillingMode(d.value as "onetime" | "subscription")}>
              <Radio value="onetime" label={`One-time -- ${formatCurrency(499, "CAD")}`} />
              <Radio value="subscription" label={`Monthly subscription -- ${formatCurrency(150, "CAD")}/month`} />
            </RadioGroup>
          </fieldset>
        )}

        <Card className={styles.priceCard}>
          <CardHeader
            header={
              <Text weight="semibold">
                {tier === "3"
                  ? `Total: ${formatCurrency(1499, "CAD")}`
                  : billingMode === "subscription"
                    ? `${formatCurrency(150, "CAD")}/month`
                    : `Total: ${formatCurrency(499, "CAD")}`
                }
              </Text>
            }
          />
          <Text>All prices in CAD. Processed securely by Stripe.</Text>
        </Card>

        <Button
          appearance="primary"
          onClick={handleCheckout}
          disabled={loading}
          aria-label={`Proceed to payment for Tier ${tier}`}
        >
          {loading ? <Spinner size="tiny" label={t("a11y.loading")} /> : "Proceed to Payment"}
        </Button>
        <Button appearance="subtle" onClick={() => navigate(-1)}>Cancel</Button>
      </div>
    </main>
  );
}
