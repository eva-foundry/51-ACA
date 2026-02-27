/**
 * ConnectSubscriptionPage -- /app/connect
 * Collects Azure subscription ID, selects onboarding mode (A/B/C),
 * calls POST /v1/auth/connect then POST /v1/collect/start.
 */

import { useState } from "react";
import { useNavigate } from "react-router-dom";
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

const MODE_LABELS: Record<OnboardMode, { title: string; desc: string }> = {
  A: {
    title: "Mode A -- Delegated user sign-in (recommended)",
    desc: "Quick scan using your own Azure credentials. Ideal for trial access.",
  },
  B: {
    title: "Mode B -- Service principal",
    desc: "Enterprise governance-friendly. You create an SP with Reader role.",
  },
  C: {
    title: "Mode C -- Azure Lighthouse delegation",
    desc: "MSP-grade. Multi-subscription support via Lighthouse.",
  },
};

export default function ConnectSubscriptionPage() {
  const navigate = useNavigate();
  const [subscriptionId, setSubscriptionId] = useState(
    sessionStorage.getItem("aca_subscription_id") ?? ""
  );
  const [mode, setMode] = useState<OnboardMode>("A");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleConnect = async () => {
    if (!subscriptionId.trim()) {
      setError("Please enter your Azure subscription ID.");
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
      setError(err instanceof Error ? err.message : "Connection failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 640 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 8 }}>
        Connect Azure Subscription
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 24 }}>
        ACA needs read-only access to your Azure subscription to run the cost analysis.
        No resources are modified.
      </Body1>

      {error && <ErrorState message={error} onRetry={() => setError(null)} />}

      <fieldset style={{ border: "none", margin: 0, padding: 0 }}>
        <legend style={{ fontWeight: 600, marginBottom: 12 }}>
          Step 1: Enter your Azure Subscription ID
        </legend>
        <Field label="Azure Subscription ID" required>
          <Input
            value={subscriptionId}
            onChange={(_, { value }) => setSubscriptionId(value)}
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            style={{ maxWidth: 420 }}
          />
        </Field>
      </fieldset>

      <fieldset style={{ border: "none", margin: "24px 0 0", padding: 0 }}>
        <legend style={{ fontWeight: 600, marginBottom: 12 }}>
          Step 2: Choose access mode
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
        {isLoading ? "Connecting..." : "Start Free Scan"}
      </Button>
    </div>
  );
}
