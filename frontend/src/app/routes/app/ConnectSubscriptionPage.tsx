// EVA-STORY: ACA-05-017
/**
 * ConnectSubscriptionPage -- /app/connect
 * Collects Azure subscription ID, selects onboarding mode (A/B/C),
 * calls POST /v1/auth/connect then POST /v1/collect/start.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Button,
  Field,
  Input,
  Radio,
  RadioGroup,
  Subtitle1,
  Body1,
} from "@fluentui/react-components";
import { appApi } from "../../api/appApi";
import { ErrorState } from "../../components/ErrorState";

type OnboardMode = "A" | "B" | "C";

export default function ConnectSubscriptionPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [subscriptionId, setSubscriptionId] = useState(
    sessionStorage.getItem("aca_subscription_id") ?? ""
  );
  const [mode, setMode] = useState<OnboardMode>("A");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const MODE_LABELS: Record<OnboardMode, { title: string; desc: string }> = {
    A: { title: t("pages.connect.modes.A.title"), desc: t("pages.connect.modes.A.desc") },
    B: { title: t("pages.connect.modes.B.title"), desc: t("pages.connect.modes.B.desc") },
    C: { title: t("pages.connect.modes.C.title"), desc: t("pages.connect.modes.C.desc") },
  };

  const handleConnect = async () => {
    if (!subscriptionId.trim()) {
      setError(t("pages.connect.validation.subscription_required"));
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      // Store subscription ID in session storage
      sessionStorage.setItem("aca_subscription_id", subscriptionId.trim());
      // Trigger collection
      await appApi.startCollection(subscriptionId.trim());
      navigate(`/app/status/${encodeURIComponent(subscriptionId.trim())}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("errors.generic"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 640 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 8 }}>
        {t("pages.connect.title")}
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 24 }}>
        {t("pages.connect.subtitle")}
      </Body1>

      {error && <ErrorState message={error} onRetry={() => setError(null)} />}

      <fieldset style={{ border: "none", margin: 0, padding: 0 }}>
        <legend style={{ fontWeight: 600, marginBottom: 12 }}>
          {t("pages.connect.step1_label")}
        </legend>
        <Field label={t("pages.connect.subscription_id_label")} required>
          <Input
            value={subscriptionId}
            onChange={(_, { value }) => setSubscriptionId(value)}
            placeholder={t("pages.connect.subscription_id_placeholder")}
            style={{ maxWidth: 420 }}
          />
        </Field>
      </fieldset>

      <fieldset style={{ border: "none", margin: "24px 0 0", padding: 0 }}>
        <legend style={{ fontWeight: 600, marginBottom: 12 }}>
          {t("pages.connect.step2_label")}
        </legend>
        <RadioGroup
          value={mode}
          onChange={(_, { value }) => setMode(value as OnboardMode)}
        >
          {(["A", "B", "C"] as OnboardMode[]).map((m) => (
            <Radio
              key={m}
              value={m}
              label={
                <>
                  <strong>{MODE_LABELS[m].title}</strong>
                  <div style={{ fontSize: 12, color: "#666", marginTop: 2 }}>
                    {MODE_LABELS[m].desc}
                  </div>
                </>
              }
            />
          ))}
        </RadioGroup>
      </fieldset>

      <Button
        appearance="primary"
        size="large"
        onClick={handleConnect}
        disabled={isLoading}
        aria-busy={isLoading}
        style={{ marginTop: 32 }}
      >
        {isLoading ? t("pages.connect.connecting") : t("pages.connect.start_scan")}
      </Button>
    </div>
  );
}
