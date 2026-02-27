```text

You are Spark, operating in the ACA repo. Build a single React (TypeScript) web app that contains BOTH the Customer pages and the Admin pages in the SAME app, with strict route isolation and RBAC. Use everything already defined in this project (docs/, api-spec.md, architecture notes, tier model, Cosmos schemas, Stripe entitlements, and the "marco\* dev sandbox first -> new subscription later" infrastructure approach).



GOALS

1\) Customer surface under /app/\*

2\) Admin surface under /admin/\*

3\) Same deployment, but admin is gated by roles and has an audit trail for privileged actions.

4\) Integrate with the existing FastAPI backend endpoints we already defined:

&nbsp;  - Customer APIs: /v1/reports/tier1, /v1/collect/start, /v1/collect/status, /v1/entitlements, /v1/billing/checkout, /v1/billing/portal, /v1/webhooks/stripe

&nbsp;  - Admin APIs: /v1/admin/kpis, /v1/admin/customers, /v1/admin/entitlements/grant, /v1/admin/subscriptions/{subscriptionId}/lock, /v1/admin/stripe/reconcile, /v1/admin/runs

5\) Use Fluent UI (React) components and keep pages WCAG-friendly (semantic headings, focus order, aria labels).

6\) Add lightweight telemetry hooks for GA4 + Microsoft Clarity (both accounts exist). Implement as:

&nbsp;  - a single `TelemetryProvider` that can be enabled/disabled via env vars

&nbsp;  - consent-friendly (no PII; do not send subscriptionId)

7\) Use a clean folder structure. Provide complete, runnable code, not stubs.



INPUTS YOU MUST READ FIRST (do not ask me for them; they are in the repo)

\- README.md

\- PLAN.md

\- docs/api-spec.md (or openapi files)

\- Any existing docs in docs/ that define: tier model, entitlement logic, Stripe mapping, Cosmos containers, and routing requirements.

\- Any existing frontend skeleton if present.



OUTPUT REQUIREMENTS

A) Create/Update these files (create if missing):

\- frontend/package.json (Vite + React + TS)

\- frontend/vite.config.ts

\- frontend/.env.example (document required env vars)

\- frontend/src/main.tsx

\- frontend/src/app/AppShell.tsx

\- frontend/src/app/routes/router.tsx

\- frontend/src/app/auth/useAuth.ts

\- frontend/src/app/auth/RequireAuth.tsx

\- frontend/src/app/auth/RequireRole.tsx

\- frontend/src/app/auth/roles.ts

\- frontend/src/app/layout/CustomerLayout.tsx

\- frontend/src/app/layout/AdminLayout.tsx

\- frontend/src/app/layout/NavCustomer.tsx

\- frontend/src/app/layout/NavAdmin.tsx

\- frontend/src/app/api/client.ts

\- frontend/src/app/api/appApi.ts

\- frontend/src/app/api/adminApi.ts

\- frontend/src/app/telemetry/TelemetryProvider.tsx

\- frontend/src/app/telemetry/ga4.ts

\- frontend/src/app/telemetry/clarity.ts

\- frontend/src/app/types/models.ts

\- frontend/src/app/components/Loading.tsx

\- frontend/src/app/components/ErrorState.tsx

\- frontend/src/app/components/DataTable.tsx

\- frontend/src/app/components/MoneyRangeBar.tsx

\- frontend/src/app/components/EffortBadge.tsx



B) Create Customer pages:

\- frontend/src/app/routes/app/LoginPage.tsx

\- frontend/src/app/routes/app/ConnectSubscriptionPage.tsx

\- frontend/src/app/routes/app/CollectionStatusPage.tsx

\- frontend/src/app/routes/app/FindingsTier1Page.tsx

\- frontend/src/app/routes/app/UpgradePage.tsx



C) Create Admin pages:

\- frontend/src/app/routes/admin/AdminDashboardPage.tsx

\- frontend/src/app/routes/admin/AdminCustomersPage.tsx

\- frontend/src/app/routes/admin/AdminBillingPage.tsx

\- frontend/src/app/routes/admin/AdminRunsPage.tsx

\- frontend/src/app/routes/admin/AdminControlsPage.tsx



D) Implement behaviors (must be working, not placeholder):

Customer

\- LoginPage: supports your chosen auth approach, but at minimum implement a "dev auth" mode (env var) that simulates a signed-in user with roles and a subscriptionId for local dev.

\- ConnectSubscriptionPage: collects and stores subscriptionId (local storage) and calls POST /v1/collect/start

\- CollectionStatusPage: polls GET /v1/collect/status?subscriptionId=... with backoff; shows steps + progress; links to Tier1 report when ready

\- FindingsTier1Page: renders Tier1 report (list of findings with money range + effort class); includes CTA to upgrade

\- UpgradePage: shows Tier2 vs Tier3; calls POST /v1/billing/checkout and handles redirectUrl; includes link to billing portal if active



Admin

\- AdminDashboardPage: calls GET /v1/admin/kpis and shows KPIs

\- AdminCustomersPage: searches /v1/admin/customers?query=... and shows tier/status; deep link to customer's runs

\- AdminBillingPage: surfaces Stripe webhook health, and provides "Reconcile Stripe" action (POST /v1/admin/stripe/reconcile)

\- AdminRunsPage: lists runs (scan/analysis/delivery) from /v1/admin/runs; supports filter by subscriptionId and type

\- AdminControlsPage: lock/unlock subscription; grant entitlements (tier + days + reason) with confirmation; writes an Admin Audit Event via backend call (the backend already records; UI should still show "audited" message)



Security/RBAC

\- Admin routes only accessible if user has any of: ACA\_Admin, ACA\_Support, ACA\_FinOps.

\- Destructive actions (grant/lock/reconcile) require ACA\_Admin OR ACA\_Support, and show a confirmation modal.

\- Never display Stripe secret values; never log PII; do not send subscriptionId to telemetry.



Styling \& Accessibility

\- Use Fluent UI components where practical.

\- Add skip-to-content link, consistent headings, and keyboard navigable nav.



Telemetry

\- `VITE\_ENABLE\_TELEMETRY=true|false`

\- `VITE\_GA4\_MEASUREMENT\_ID=G-XXXX`

\- `VITE\_CLARITY\_PROJECT\_ID=XXXX`

\- TelemetryProvider should load scripts only when enabled and consent is granted (simple local toggle is fine for MVP).



E) Deliverables

\- Code compiles and runs with:

&nbsp; - `cd frontend \&\& npm install \&\& npm run dev`

\- Provide a short `frontend/README.md` explaining env vars and how to run.

\- Do NOT change backend code in this task. Assume backend exists at VITE\_API\_BASE\_URL.



QUALITY BAR

\- No TODO placeholders for core flows.

\- TypeScript types for API DTOs.

\- Error handling: show friendly ErrorState with retry.

\- Keep the UI minimal but production-lean (clean navigation, sensible layouts).



Now implement. Output the full file tree with content (or a patch-style output) so I can paste it into the repo.

```



