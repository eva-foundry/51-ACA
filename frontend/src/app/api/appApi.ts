/**
 * Customer API client -- all /app/* page API calls.
 * Corresponds to the customer surface endpoints in docs/22-spark-frontend.md.
 */

import { http } from "./client";
import type {
  Tier1Report,
  CollectionStatus,
  Entitlement,
  CheckoutResponse,
  BillingPortalResponse,
} from "../types/models";

export const appApi = {
  /** GET /v1/reports/tier1?subscriptionId= */
  getTier1Report: (subscriptionId: string): Promise<Tier1Report> =>
    http<Tier1Report>(
      `/v1/reports/tier1?subscriptionId=${encodeURIComponent(subscriptionId)}`
    ),

  /** POST /v1/collect/start -- trigger collection job */
  startCollection: (subscriptionId: string): Promise<{ scanId: string; status: string }> =>
    http(`/v1/collect/start`, {
      method: "POST",
      body: JSON.stringify({ subscriptionId }),
    }),

  /** GET /v1/collect/status?subscriptionId= -- poll collection progress */
  getCollectionStatus: (subscriptionId: string): Promise<CollectionStatus> =>
    http<CollectionStatus>(
      `/v1/collect/status?subscriptionId=${encodeURIComponent(subscriptionId)}`
    ),

  /** GET /v1/entitlements?subscriptionId= -- current tier */
  getEntitlement: (subscriptionId: string): Promise<Entitlement> =>
    http<Entitlement>(
      `/v1/entitlements?subscriptionId=${encodeURIComponent(subscriptionId)}`
    ),

  /** POST /v1/billing/checkout -- create Stripe checkout session */
  startCheckout: (
    subscriptionId: string,
    tier: 2 | 3,
    mode: "one_time" | "subscription"
  ): Promise<CheckoutResponse> =>
    http<CheckoutResponse>(`/v1/billing/checkout`, {
      method: "POST",
      body: JSON.stringify({ subscriptionId, tier, mode }),
    }),

  /** GET /v1/billing/portal -- Stripe billing portal URL */
  getBillingPortalUrl: (subscriptionId: string): Promise<BillingPortalResponse> =>
    http<BillingPortalResponse>(
      `/v1/billing/portal?subscriptionId=${encodeURIComponent(subscriptionId)}`
    ),
};
