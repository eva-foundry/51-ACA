/**
 * UpgradePage -- /app/upgrade/:subscriptionId
 * Shows Tier 2 vs Tier 3 options.
 * Calls POST /v1/billing/checkout and redirects to Stripe.
 */

import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Button,
  Subtitle1,
  Body1,
  Divider,
} from "@fluentui/react-components";
import { appApi } from "../../api/appApi";
import { ErrorState } from "../../components/ErrorState";

type CheckoutMode = "one_time" | "subscription";

interface TierOption {
  tier: 2 | 3;
  title: string;
  priceLabel: string;
  mode: CheckoutMode;
  benefits: string[];
  cta: string;
}

const TIERS: TierOption[] = [
  {
    tier: 2,
    title: "Tier 2 -- Advisory Report",
    priceLabel: "CAD $499 one-time  OR  CAD $150/month",
    mode: "one_time",
    benefits: [
      "Full findings with narrative",
      "Effort and risk classification",
      "Beyond-cost signals (SKU, network, policy)",
      "Interactive dashboard + PDF export",
    ],
    cta: "Get Full Report",
  },
  {
    tier: 3,
    title: "Tier 3 -- Deliverable Package",
    priceLabel: "CAD $1,499",
    mode: "one_time",
    benefits: [
      "Everything in Tier 2",
      "Terraform + Bicep templates (parameterized for YOUR subscription)",
      "PowerShell / Bash automation scripts",
      "Implementation guide PDF + rollback instructions",
      "24-hour SAS URL download link",
    ],
    cta: "Get Full Package",
  },
];

export default function UpgradePage() {
  const { subscriptionId } = useParams<{ subscriptionId: string }>();
  const [loadingTier, setLoadingTier] = useState<2 | 3 | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheckout = async (option: TierOption) => {
    if (!subscriptionId) return;
    setLoadingTier(option.tier);
    setError(null);
    try {
      const { redirectUrl } = await appApi.startCheckout(subscriptionId, option.tier, option.mode);
      window.location.href = redirectUrl;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Checkout failed. Please try again.");
    } finally {
      setLoadingTier(null);
    }
  };

  return (
    <div style={{ maxWidth: 800 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 8 }}>
        Upgrade Your Report
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 8 }}>
        Subscription: <code>{subscriptionId}</code>
      </Body1>
      <Link to={`/app/findings/${encodeURIComponent(subscriptionId!)}`} style={{ fontSize: 13 }}>
        &larr; Back to free summary
      </Link>

      {error && (
        <ErrorState message="Checkout failed" detail={error} onRetry={() => setError(null)} />
      )}

      <div style={{ display: "flex", gap: 24, marginTop: 32, flexWrap: "wrap" }}>
        {TIERS.map((t) => (
          <div
            key={t.tier}
            style={{
              flex: "1 1 300px",
              border: "2px solid #d0d0d0",
              borderRadius: 12,
              padding: 24,
              background: t.tier === 3 ? "#f0f7ff" : "#fff",
            }}
          >
            <h2 style={{ margin: "0 0 8px", fontSize: 18 }}>{t.title}</h2>
            <p style={{ fontSize: 14, color: "#0078d4", fontWeight: 600, margin: "0 0 16px" }}>
              {t.priceLabel}
            </p>
            <Divider />
            <ul role="list" style={{ paddingLeft: 20, marginBlock: 16 }}>
              {t.benefits.map((b) => (
                <li key={b} style={{ marginBottom: 8, fontSize: 14 }}>
                  {b}
                </li>
              ))}
            </ul>
            <Button
              appearance="primary"
              size="large"
              onClick={() => handleCheckout(t)}
              disabled={loadingTier !== null}
              aria-busy={loadingTier === t.tier}
              style={{ width: "100%" }}
            >
              {loadingTier === t.tier ? "Redirecting to Stripe..." : t.cta}
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
