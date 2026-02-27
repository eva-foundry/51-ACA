# ACA Analytics & Product Telemetry Spec (GA4 + Microsoft Clarity)
===============================================================

Version: 0.2
Updated: 2026-02-26

## Goal

Instrument ACA with:
- Google Analytics 4 (GA4): product usage + funnel + conversion tracking
- Microsoft Clarity: session replay + heatmaps for UX research

## Principles

1. Privacy-first: no sensitive Azure data in analytics payloads
2. Minimal identifiers: opaque ACA IDs only (no subscriptionId, no UPN)
3. Consent-aware: analytics and replay run only after user consent
4. GTM-deployed: GA4 and Clarity tags managed via Google Tag Manager container

## Data Safety Rules (HARD RULES -- non-negotiable)

Do NOT send any of the following to GA4, Clarity, or dataLayer:
- Azure subscriptionId, tenantId, resource names, tags, meter names
- Costs by resource (only aggregated ranges are permitted)
- User principal names, emails, display names, object IDs
- Raw error messages containing Azure identifiers
- Service principal credentials or tokens

Allowed properties (SAFE LIST):
- event_id: UUID (client-generated per event)
- sessionId: opaque ACA session ID (from server)
- tier: 1 | 2 | 3
- feature flags: boolean values only
- error_category: enum string only (see below)
- duration_ms, count values (numeric)
- page_name: route path (e.g. "/app/findings", "/admin/billing")

## Tooling

Preferred deployment stack:
- Google Tag Manager (GTM) container
  - GA4 Configuration Tag
  - GA4 Event Tags (one per event type)
  - Microsoft Clarity Tag
  - Consent Mode integration

Frontend wiring:
- `frontend/src/telemetry/gtm.ts` -- GTM loader, pushEvent()
- `frontend/src/telemetry/analytics.ts` -- typed event taxonomy
- `frontend/src/telemetry/consent.ts` -- GTM Consent Mode v2 adapter

## Event Taxonomy

### Onboarding Funnel

| Event Name | Properties |
|---|---|
| `login_success` | (none) |
| `subscription_selected` | `{ mode: "delegated" \| "service_principal" \| "lighthouse" }` |
| `preflight_started` | `{ subscription_selected: true }` |
| `preflight_pass` | `{ probe_count: number, duration_ms: number }` |
| `preflight_fail` | `{ error_category: "missing_permission" \| "auth_failed" \| "api_error" \| "rate_limited" }` |

### Core Usage

| Event Name | Properties |
|---|---|
| `scan_started` | `{ window_days: 91, tier: 1 }` |
| `scan_step_completed` | `{ step: "inventory" \| "cost_data" \| "advisor" \| "policy" \| "analysis" }` |
| `scan_completed` | `{ duration_ms: number, inventory_count: number, cost_rows: number }` |
| `analysis_started` | `{ mode: "tier1" \| "tier2" }` |
| `analysis_completed` | `{ duration_ms: number, finding_count: number, total_saving_low: number, total_saving_high: number }` |

Note: `total_saving_low` and `total_saving_high` are aggregate numbers, not per-resource amounts.

### Tier Gating & Conversion Funnel

| Event Name | Properties |
|---|---|
| `findings_viewed_tier1` | `{ finding_count: number }` |
| `unlock_cta_clicked` | `{ target_tier: 2 \| 3, location: "report_header" \| "finding_row" \| "upgrade_page" }` |
| `checkout_started` | `{ tier: 2 \| 3, price_cad: number }` |
| `checkout_completed` | `{ tier: 2 \| 3 }` |
| `deliverable_ready` | (no properties -- event fires when SAS URL is generated) |
| `deliverable_downloaded` | (no properties) |

### Admin Events (exclude from GA4 -- internal only)

Admin events may be tracked via Application Insights custom events only.
Do NOT send admin actions to GA4 or Clarity.

### Error Taxonomy (enum values only)

```
missing_permission
auth_failed
api_error
rate_limited
scan_timeout
analysis_failed
delivery_failed
stripe_error
unknown
```

## Consent Model

Behavior on first visit:
- GTM loads immediately (required for correct Consent Mode v2 initialization)
- All analytics tags are blocked until consent is recorded
- ConsentBanner.tsx is shown with two options:
  1. "Accept analytics & replay" -- enables analytics_storage + clarity
  2. "Reject non-essential" -- disables both

Storage key: `aca_consent` in localStorage
Values: `"granted"` | `"denied"` | not set (default = denied)

GTM Consent Mode v2 mapping:
```
analytics_storage: "granted" | "denied"
```

Code reference: `frontend/src/telemetry/consent.ts`

## Microsoft Clarity Configuration

Required settings:
- Enable text masking on all input fields (default Clarity masking ON)
- Mark "sensitive zones" via CSS class: `clarity-mask`
- Apply `clarity-mask` to:
  - SP credential/secret input fields
  - Any field that might render a subscriptionId
- Custom event triggers for key funnel steps:
  - `clarity("event", "preflight_fail")`
  - `clarity("event", "unlock_cta_clicked")`
  - `clarity("event", "checkout_started")`
  - `clarity("event", "checkout_completed")`

## GA4 Conversion Goals

Mark the following events as conversions in GA4 console:
- `checkout_completed`
- `deliverable_downloaded`

Recommended GA4 funnels:
1. Acquisition: `login_success` -> `subscription_selected` -> `preflight_pass` -> `scan_completed`
2. Monetization: `findings_viewed_tier1` -> `unlock_cta_clicked` -> `checkout_completed`

## Frontend Code Reference

```
frontend/src/telemetry/
  consent.ts     -- consent state + GTM Consent Mode v2
  gtm.ts         -- GTM snippet loader, pushEvent(name, props)
  analytics.ts   -- typed AnalyticsEventName enum + trackEvent()
```

`trackEvent()` must:
1. Check `isTelemetryEnabled()` before pushing to dataLayer
2. Sanitize props to remove any Azure identifiers
3. Push `{ event: name, ...props }` to `window.dataLayer`

## API Reference

Entitlements endpoint (used by APIM and frontend tier gating):
```
GET /v1/entitlements?subscriptionId={id}
Response: { subscriptionId, tier, paymentStatus, canViewTier2, canGenerateTier3 }
```

Billing portal (Stripe):
```
GET /v1/billing/portal?returnUrl={url}
Response: { redirectUrl: "https://billing.stripe.com/session/..." }
```
