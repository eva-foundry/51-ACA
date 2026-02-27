// EVA-STORY: ACA-05-028
/**
 * Admin API client -- all /admin/* page API calls.
 * Corresponds to the admin surface endpoints in docs/22-spark-frontend.md and docs/21-managing-buz.md.
 */

import { http } from "./client";
import type {
  AdminKpis,
  AdminCustomerSearchResponse,
  AdminGrantEntitlementRequest,
  AdminLockRequest,
  AdminJobAccepted,
  AdminRunsResponse,
  Entitlement,
} from "../types/models";

export const adminApi = {
  /** GET /v1/admin/kpis */
  kpis: (): Promise<AdminKpis> =>
    http<AdminKpis>(`/v1/admin/kpis`),

  /** GET /v1/admin/customers?query= */
  searchCustomers: (query: string): Promise<AdminCustomerSearchResponse> =>
    http<AdminCustomerSearchResponse>(
      `/v1/admin/customers?query=${encodeURIComponent(query)}`
    ),

  /** POST /v1/admin/entitlements/grant */
  grantEntitlement: (req: AdminGrantEntitlementRequest): Promise<Entitlement> =>
    http<Entitlement>(`/v1/admin/entitlements/grant`, {
      method: "POST",
      body: JSON.stringify(req),
    }),

  /** POST /v1/admin/subscriptions/:subscriptionId/lock */
  lockSubscription: (subscriptionId: string, req: AdminLockRequest): Promise<void> =>
    http<void>(
      `/v1/admin/subscriptions/${encodeURIComponent(subscriptionId)}/lock`,
      { method: "POST", body: JSON.stringify(req) }
    ),

  /** POST /v1/admin/stripe/reconcile */
  reconcileStripe: (): Promise<AdminJobAccepted> =>
    http<AdminJobAccepted>(`/v1/admin/stripe/reconcile`, { method: "POST" }),

  /** GET /v1/admin/runs?type=&subscriptionId= */
  getRuns: (params?: {
    type?: "scan" | "analysis" | "delivery";
    subscriptionId?: string;
  }): Promise<AdminRunsResponse> => {
    const qs = new URLSearchParams();
    if (params?.type) qs.set("type", params.type);
    if (params?.subscriptionId) qs.set("subscriptionId", params.subscriptionId);
    const q = qs.toString();
    return http<AdminRunsResponse>(`/v1/admin/runs${q ? `?${q}` : ""}`);
  },
};
