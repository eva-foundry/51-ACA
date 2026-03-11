// EVA-STORY: ACA-05-020
/**
 * UpgradePage -- /app/upgrade/:subscriptionId
 * Shows Tier 2 vs Tier 3 options.
 * Calls POST /v1/billing/checkout and redirects to Stripe.
 */

import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import type { TFunction } from "i18next";
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

function getTiers(t: TFunction): TierOption[] {
  return [
    {
      tier: 2,
      title: t("pages.upgrade.tiers.tier2.title"),
      priceLabel: t("pages.upgrade.tiers.tier2.price"),
      mode: "one_time",
      benefits: t("pages.upgrade.tiers.tier2.benefits", { returnObjects: true }) as string[],
      cta: t("pages.upgrade.tiers.tier2.cta"),
    },
    {
      tier: 3,
      title: t("pages.upgrade.tiers.tier3.title"),
      priceLabel: t("pages.upgrade.tiers.tier3.price"),
      mode: "one_time",
      benefits: t("pages.upgrade.tiers.tier3.benefits", { returnObjects: true }) as string[],
      cta: t("pages.upgrade.tiers.tier3.cta"),
    },
  ];
}

export default function UpgradePage() {
  const { t } = useTranslation();
  const { subscriptionId } = useParams<{ subscriptionId: string }>();
  const [loadingTier, setLoadingTier] = useState<2 | 3 | null>(null);
  const [error, setError] = useState<string | null>(null);
  const tiers = getTiers(t);

  const handleCheckout = async (option: TierOption) => {
    if (!subscriptionId) return;
    setLoadingTier(option.tier);
    setError(null);
    try {
      const { redirectUrl } = await appApi.startCheckout(subscriptionId, option.tier, option.mode);
      window.location.href = redirectUrl;
    } catch (err) {
      setError(err instanceof Error ? err.message : t("errors.generic"));
    } finally {
      setLoadingTier(null);
    }
  };

  return (
    <div style={{ maxWidth: 800 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 8 }}>
        {t("pages.upgrade.title")}
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 8 }}>
        {t("pages.upgrade.subscription")} <code>{subscriptionId}</code>
      </Body1>
      <Link to={`/app/findings/${encodeURIComponent(subscriptionId!)}`} style={{ fontSize: 13 }}>
        &larr; {t("pages.upgrade.back")}
      </Link>

      {error && (
        <ErrorState message={t("pages.upgrade.checkout_failed")} detail={error} onRetry={() => setError(null)} />
      )}

      <div style={{ display: "flex", gap: 24, marginTop: 32, flexWrap: "wrap" }}>
        {tiers.map((tier) => (
          <div
            key={tier.tier}
            style={{
              flex: "1 1 300px",
              border: "2px solid #d0d0d0",
              borderRadius: 12,
              padding: 24,
              background: tier.tier === 3 ? "#f0f7ff" : "#fff",
            }}
          >
            <h2 style={{ margin: "0 0 8px", fontSize: 18 }}>{tier.title}</h2>
            <p style={{ fontSize: 14, color: "#0078d4", fontWeight: 600, margin: "0 0 16px" }}>
              {tier.priceLabel}
            </p>
            <Divider />
            <ul role="list" style={{ paddingLeft: 20, marginBlock: 16 }}>
              {tier.benefits.map((b) => (
                <li key={b} style={{ marginBottom: 8, fontSize: 14 }}>
                  {b}
                </li>
              ))}
            </ul>
            <Button
              appearance="primary"
              size="large"
              onClick={() => handleCheckout(tier)}
              disabled={loadingTier !== null}
              aria-busy={loadingTier === tier.tier}
              style={{ width: "100%" }}
            >
              {loadingTier === tier.tier ? t("pages.upgrade.redirecting") : tier.cta}
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
