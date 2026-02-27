// EVA-STORY: ACA-08-004
/**
 * Analytics event taxonomy for ACA.
 * All events go through GTM -> GA4.
 * No Azure subscription IDs or tenant IDs in any parameter.
 */

import { pushEvent } from "./gtm";

export type AnalyticsEventName =
  | "page_view"
  | "session_started"
  | "connect_flow_started"
  | "connect_mode_selected"
  | "preflight_success"
  | "preflight_failed"
  | "scan_started"
  | "scan_completed"
  | "tier_viewed"
  | "checkout_started"
  | "purchase"
  | "download_initiated"
  | "finding_expanded"
  | "finding_deepdive_clicked"
  | "language_changed"
  | "consent_updated";

/** Track a page view -- call on every route change */
export function trackPageView(path: string, title: string): void {
  pushEvent("page_view", {
    page_path: path,
    page_title: title,
  });
}

/** Track a generic analytics event */
export function trackEvent(
  name: AnalyticsEventName,
  params?: Record<string, string | number | boolean>
): void {
  // Strip any PII or Azure identifiers before pushing
  const sanitized = sanitizeParams(params ?? {});
  pushEvent(name, sanitized);
}

/** Never send subscription IDs, tenant IDs, or email addresses to analytics */
function sanitizeParams(params: Record<string, unknown>): Record<string, unknown> {
  const BLOCKED_KEYS = [
    "subscriptionId",
    "tenantId",
    "email",
    "primaryEmail",
    "clientId",
    "stripeCustomerId",
  ];
  const clean: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(params)) {
    if (!BLOCKED_KEYS.includes(k)) {
      clean[k] = v;
    }
  }
  return clean;
}
