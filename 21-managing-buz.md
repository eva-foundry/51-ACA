You can do this in \*\*one app\*\* at first (admin pages inside the same React app + a few admin APIs), and only split into a separate “management app” once you hit \*\*real scaling / separation-of-duties / multi-operator\*\* needs.



\### Start with: Admin pages in the same app (recommended MVP)



\*\*Why this works early\*\*



\* One deployment, one auth model, one UI shell.

\* You already have the key entities (clients/subscriptions, scans, entitlements, payments, deliverables).

\* Most “business ops” is just \*\*views + actions\*\* on those entities.



\*\*What you build\*\*



\* `/admin` route in React (hidden unless admin role)

\* `Admin` API endpoints in FastAPI behind strict authorization



\*\*Minimum admin pages\*\*



1\. \*\*Dashboard\*\*



&nbsp;  \* MRR / revenue (from Stripe)

&nbsp;  \* Active subscriptions / churn (from Stripe)

&nbsp;  \* Scans/day, analyses/day, Tier3 deliveries/day (from Cosmos)

&nbsp;  \* Failure rates (preflight / scan / analysis / delivery)



2\. \*\*Customers / Subscriptions\*\*



&nbsp;  \* Search by customer name or ACA subscriptionId

&nbsp;  \* Current entitlement tier + paymentStatus

&nbsp;  \* Last scan, last analysis, last delivery

&nbsp;  \* Button: “Grant Tier2/Tier3 for 7 days” (support / goodwill)

&nbsp;  \* Button: “Lock subscription” (abuse)



3\. \*\*Billing\*\*



&nbsp;  \* Link to Stripe customer portal

&nbsp;  \* Webhook health: last N webhook events processed

&nbsp;  \* “Reconcile entitlements” job (repair if webhook missed)



4\. \*\*Runs\*\*



&nbsp;  \* List scans / analyses / deliveries with status + timestamps

&nbsp;  \* Drilldown to logs + correlation id



5\. \*\*Operational controls\*\*



&nbsp;  \* Rate limit overrides (per subscription)

&nbsp;  \* Feature flags (enable/disable Tier3 delivery)

&nbsp;  \* Incident banner text (if you want a public status message in app)



\*\*Role model\*\*



\* Use Entra groups/roles:



&nbsp; \* `ACA\_Admin` (full)

&nbsp; \* `ACA\_Support` (view + grant trial + lock)

&nbsp; \* `ACA\_FinOps` (read billing + usage only)



This is usually enough for the first real customers.



---



\### When you DO want a separate Management App



Split when \*\*any\*\* of these become true:



1\. \*\*Separation of duties\*\*

&nbsp;  You want finance/support to access admin without access to the main product UI or customer data flows.



2\. \*\*Different security posture\*\*

&nbsp;  Admin requires stronger controls (IP allowlist, MFA enforcement, conditional access), while customer app remains accessible.



3\. \*\*Multiple operators + audit needs\*\*

&nbsp;  You need an “admin audit trail” for every manual action (grant, lock, refund assist, override).



4\. \*\*Partner / reseller operations\*\*

&nbsp;  If you onboard channel partners who manage customers.



5\. \*\*You move to multi-product\*\*

&nbsp;  When ACA becomes one product among several.



If you split, keep the same backend — the “Management App” is mostly a different frontend + tighter access controls.



---



\### A clean compromise: same app, but “admin surface” is isolated



Even in one React app, you can make admin effectively a separate product surface:



\* Admin routes under `/admin/\*`

\* Separate navigation shell + theme (optional)

\* Separate API prefix `/v1/admin/\*`

\* Strong policy layer (RBAC + audit logging)

\* Optional: require re-auth / step-up auth for dangerous actions



This gives 80% of the benefits without the operational overhead of a second app.



---



\### What I’d do for ACA specifically



\*\*MVP path\*\*



1\. \*\*Same app\*\* with `/admin` + Entra RBAC

2\. Admin APIs:



&nbsp;  \* `GET /v1/admin/kpis`

&nbsp;  \* `GET /v1/admin/customers?query=`

&nbsp;  \* `POST /v1/admin/entitlements/grant`

&nbsp;  \* `POST /v1/admin/subscriptions/lock`

&nbsp;  \* `POST /v1/admin/reconcile/stripe`

&nbsp;  \* `GET /v1/admin/runs?type=scan|analysis|delivery`



\*\*Split later\*\* if you end up needing a support team, finance workflows, or stricter security isolation.



---



If you say \*\*“generate the admin pages + admin API spec”\*\*, I’ll produce:



\* React route map + page skeletons (Dashboard, Customers, Billing, Runs)

\* FastAPI `/v1/admin/\*` endpoints + RBAC guards

\* Cosmos schemas needed for admin KPIs + admin audit events



