import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Title2, Text, Button, RadioGroup, Radio,
  Field, Input, Spinner, makeStyles, tokens,
} from "@fluentui/react-components";
import { trackPageView, trackEvent } from "../telemetry/analytics";

type Mode = "A" | "B";

const useStyles = makeStyles({
  root: { maxWidth: "600px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
  form: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalL },
});

export default function Connect() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const styles = useStyles();
  const [mode, setMode] = useState<Mode>("A");
  const [tenantId, setTenantId] = useState("");
  const [subscriptionId, setSubscriptionId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { trackPageView("/connect", "Connect Subscription"); }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    trackEvent("connect_mode_selected", { mode });
    try {
      const res = await fetch("/v1/auth/connect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, tenant_id: tenantId, subscription_id: subscriptionId }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      navigate("/preflight");
    } catch (err) {
      setError(err instanceof Error ? err.message : t("errors.generic"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className={styles.root}>
      <Title2>{t("actions.connect_subscription")}</Title2>
      <form onSubmit={handleSubmit} className={styles.form} aria-label="Connect subscription form" noValidate>
        <fieldset style={{ border: "none", padding: 0 }}>
          <legend><Text weight="semibold">Onboarding mode</Text></legend>
          <RadioGroup
            value={mode}
            onChange={(_, d) => setMode(d.value as Mode)}
            aria-required="true"
          >
            <Radio value="A" label="Mode A -- Delegated (recommended)" />
            <Radio value="B" label="Mode B -- Service Principal" />
          </RadioGroup>
        </fieldset>
        <Field label="Tenant ID" required>
          <Input
            value={tenantId}
            onChange={(_, d) => setTenantId(d.value)}
            placeholder="00000000-0000-0000-0000-000000000000"
            aria-required="true"
          />
        </Field>
        <Field label="Subscription ID" required>
          <Input
            value={subscriptionId}
            onChange={(_, d) => setSubscriptionId(d.value)}
            placeholder="00000000-0000-0000-0000-000000000000"
            aria-required="true"
          />
        </Field>
        {error && (
          <div role="alert" aria-live="assertive" style={{ color: tokens.colorPaletteRedForeground1 }}>
            {error}
          </div>
        )}
        <Button type="submit" appearance="primary" disabled={loading}>
          {loading ? <Spinner size="tiny" label={t("a11y.loading")} /> : t("actions.connect_subscription")}
        </Button>
      </form>
    </main>
  );
}
