Great — \*\*GA4 + Microsoft Clarity\*\* is a clean combo, and since you have accounts on both, you can wire this in quickly (ideally via \*\*Google Tag Manager\*\* so you only ship one tag).



Below are the \*\*ACA-ready specs + the exact places to integrate\*\*.



---



\## `docs/analytics-spec.md` (GA4 + Clarity)



```markdown

\# ACA Analytics \& Product Telemetry Spec (GA4 + Microsoft Clarity)

===============================================================



Version: 0.1

Updated: 2026-02-26



Goal

----

Instrument ACA with:

\- Google Analytics 4 (GA4): product usage + funnel + conversions

\- Microsoft Clarity: session replay + heatmaps for UX improvements



Principles

----------

1\) Privacy-first: no sensitive Azure data in analytics

2\) Minimal identifiers: use ACA opaque IDs only

3\) Consent-aware: analytics/replay run only after consent (where required)



Tooling

-------

Preferred deployment:

\- Google Tag Manager (GTM) container

&nbsp; - loads GA4 tag

&nbsp; - loads Clarity tag



Data safety rules (HARD)

------------------------

Do NOT send any of:

\- Azure subscriptionId, tenantId, resource names, tags, meter names, costs by resource

\- user principal IDs, emails, names

\- raw error messages containing Azure identifiers



Allowed properties (SAFE)

-------------------------

\- event\_id: UUID (client-generated)

\- client\_id\_hash: stable hash (server-generated or client-generated) - optional

\- scanId, analysisId, deliverableId (opaque ACA ids)

\- tier: 1|2|3

\- feature flags: booleans

\- error\_category: enum only

\- durations, counts (numeric), page names



Event taxonomy

--------------



Onboarding

\- login\_success

\- subscription\_selected

&nbsp; props: { mode: "delegated"|"service\_principal"|"lighthouse" }

\- preflight\_started

&nbsp; props: { subscription\_selected: true }

\- preflight\_pass

&nbsp; props: { probe\_count, duration\_ms }

\- preflight\_fail

&nbsp; props: { error\_category: "missing\_permission"|"auth\_failed"|"api\_error"|"rate\_limited" }



Core usage

\- scan\_started

&nbsp; props: { window\_days: 91, tier: 1 }

\- scan\_completed

&nbsp; props: { duration\_ms, inventory\_count, cost\_rows }

\- analysis\_started

&nbsp; props: { mode: "tier1"|"tier2" }

\- analysis\_completed

&nbsp; props: { duration\_ms, finding\_count, total\_saving\_low, total\_saving\_high }



Tier gating / conversion funnel

\- findings\_viewed\_tier1

&nbsp; props: { analysisId, finding\_count }

\- unlock\_cta\_clicked

&nbsp; props: { target\_tier: 2|3, location: "report\_header"|"finding\_row" }

\- checkout\_started

&nbsp; props: { tier: 2|3, price\_cad }

\- checkout\_completed

&nbsp; props: { tier: 2|3 }

\- deliverable\_ready

&nbsp; props: { deliverableId }

\- deliverable\_downloaded

&nbsp; props: { deliverableId }



Clarity UX markers (optional)

-----------------------------

In addition to Clarity replay, consider tagging key actions as "custom events"

via clarity("event", "name") for:

\- preflight\_fail

\- unlock\_cta\_clicked

\- checkout\_started

\- checkout\_completed



Consent model

-------------

Recommended:

\- Show a lightweight consent banner on first visit

\- Options:

&nbsp; - Accept analytics + clarity

&nbsp; - Reject non-essential (disable both)

\- Store consent in localStorage/cookie



Default:

\- analytics disabled until consent recorded (safe default)



Masking

-------

\- Enable Clarity masking for text input fields

\- Ensure no secrets are displayed in UI fields (client secrets must never be visible after entry)



End

---

```



---



\## Update to `docs/api-spec.md` (add 2 endpoints you’ll want)



Add these sections under Public API:



```markdown

\### Billing portal (Stripe)

GET /v1/billing/portal?returnUrl={url}

Response:

{

&nbsp; "redirectUrl": "https://billing.stripe.com/session/..."

}



Rules:

\- Requires authenticated user

\- Opens Stripe customer portal for subscription management (Tier 2 monthly)



\### Entitlements status

GET /v1/entitlements?subscriptionId={id}

Response:

{

&nbsp; "subscriptionId": "...",

&nbsp; "tier": "tier1|tier2|tier3",

&nbsp; "paymentStatus": "none|active|past\_due|canceled",

&nbsp; "canViewTier2": true,

&nbsp; "canGenerateTier3": false

}

```



This keeps the frontend simple and prevents relying on Stripe-only state.



---



\## Frontend integration (recommended approach)



\### 1) Add \*\*one\*\* GTM script



\* Put GTM snippet in `frontend/index.html` (or Next/React equivalent)

\* Then configure GA4 + Clarity in GTM



\### 2) Create a single tracking wrapper



`frontend/src/telemetry/analytics.ts`:



\* `track(eventName, props)` pushes to `dataLayer`

\* GA4 listens to events via GTM

\* Clarity events can be called directly (optional)



\### 3) Consent gating



`frontend/src/telemetry/consent.ts`:



\* `isTelemetryEnabled()`

\* `setTelemetryEnabled(true|false)`

\* if disabled: don’t load GTM (or block tags via GTM consent mode)



\*\*Fastest implementation\*\*: always load GTM, but block tags until consent.



---



\## Clarity-specific best practices for ACA



\* Turn on masking (default is good, verify)

\* Add “sensitive zones” CSS class masking for:



&nbsp; \* service principal secret field

&nbsp; \* any token-like fields

\* Avoid rendering subscription IDs anywhere (even if masked)



---



\## What I can generate next (copy/paste-ready)



If you say “generate the stubs”, I’ll output \*\*actual files\*\* for:



1\. `frontend/src/telemetry/analytics.ts` (dataLayer + optional clarity events)

2\. `frontend/src/telemetry/consent.ts` (banner + storage)

3\. `frontend/src/components/ConsentBanner.tsx` (Fluent UI v9 style)

4\. Backend: `routers/billing.py` + `routers/entitlements.py` + repo stubs



Just tell me whether your frontend is \*\*plain React\*\* or \*\*Next.js\*\* (either works; I’ll default to plain React if you don’t specify).



