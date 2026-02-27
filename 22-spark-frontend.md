Yes. Here’s a \*\*Spark-ready package\*\* (routes + page skeletons + admin OpenAPI + Cosmos schema) that matches the ACA plan (Tier 1 customer pages now, admin surface in same app, with clean separation).  



---



\## 1) Spark frontend folder layout (React)



```text

frontend/

&nbsp; src/

&nbsp;   app/

&nbsp;     AppShell.tsx

&nbsp;     auth/

&nbsp;       RequireAuth.tsx

&nbsp;       RequireRole.tsx

&nbsp;       useAuth.ts

&nbsp;       roles.ts

&nbsp;     layout/

&nbsp;       CustomerLayout.tsx

&nbsp;       AdminLayout.tsx

&nbsp;       NavCustomer.tsx

&nbsp;       NavAdmin.tsx

&nbsp;     routes/

&nbsp;       router.tsx

&nbsp;       app/

&nbsp;         LoginPage.tsx

&nbsp;         ConnectSubscriptionPage.tsx

&nbsp;         CollectionStatusPage.tsx

&nbsp;         FindingsTier1Page.tsx

&nbsp;         UpgradePage.tsx

&nbsp;       admin/

&nbsp;         AdminDashboardPage.tsx

&nbsp;         AdminCustomersPage.tsx

&nbsp;         AdminBillingPage.tsx

&nbsp;         AdminRunsPage.tsx

&nbsp;         AdminControlsPage.tsx

&nbsp;     components/

&nbsp;       Loading.tsx

&nbsp;       ErrorState.tsx

&nbsp;       DataTable.tsx

&nbsp;       MoneyRangeBar.tsx

&nbsp;       EffortBadge.tsx

&nbsp;       RiskBadge.tsx

&nbsp;     api/

&nbsp;       client.ts

&nbsp;       appApi.ts

&nbsp;       adminApi.ts

&nbsp;     types/

&nbsp;       models.ts

```



This directly supports the Phase 1 page list (Login, Connect Subscription, Collection Status, Findings Report Tier 1) and leaves Tier2/Tier3 behind CTA. 



---



\## 2) Route map + guards (customer vs admin)



\### `frontend/src/app/routes/router.tsx`



```tsx

import { createBrowserRouter } from "react-router-dom";

import { RequireAuth } from "../auth/RequireAuth";

import { RequireRole } from "../auth/RequireRole";

import { CustomerLayout } from "../layout/CustomerLayout";

import { AdminLayout } from "../layout/AdminLayout";



import { LoginPage } from "./app/LoginPage";

import { ConnectSubscriptionPage } from "./app/ConnectSubscriptionPage";

import { CollectionStatusPage } from "./app/CollectionStatusPage";

import { FindingsTier1Page } from "./app/FindingsTier1Page";

import { UpgradePage } from "./app/UpgradePage";



import { AdminDashboardPage } from "./admin/AdminDashboardPage";

import { AdminCustomersPage } from "./admin/AdminCustomersPage";

import { AdminBillingPage } from "./admin/AdminBillingPage";

import { AdminRunsPage } from "./admin/AdminRunsPage";

import { AdminControlsPage } from "./admin/AdminControlsPage";



export const router = createBrowserRouter(\[

&nbsp; { path: "/", element: <LoginPage /> },



&nbsp; {

&nbsp;   path: "/app",

&nbsp;   element: (

&nbsp;     <RequireAuth>

&nbsp;       <CustomerLayout />

&nbsp;     </RequireAuth>

&nbsp;   ),

&nbsp;   children: \[

&nbsp;     { path: "connect", element: <ConnectSubscriptionPage /> },

&nbsp;     { path: "status/:subscriptionId", element: <CollectionStatusPage /> },

&nbsp;     { path: "findings/:subscriptionId", element: <FindingsTier1Page /> },

&nbsp;     { path: "upgrade/:subscriptionId", element: <UpgradePage /> },

&nbsp;   ],

&nbsp; },



&nbsp; {

&nbsp;   path: "/admin",

&nbsp;   element: (

&nbsp;     <RequireAuth>

&nbsp;       <RequireRole anyOf={\["ACA\_Admin", "ACA\_Support", "ACA\_FinOps"]}>

&nbsp;         <AdminLayout />

&nbsp;       </RequireRole>

&nbsp;     </RequireAuth>

&nbsp;   ),

&nbsp;   children: \[

&nbsp;     { path: "dashboard", element: <AdminDashboardPage /> },

&nbsp;     { path: "customers", element: <AdminCustomersPage /> },

&nbsp;     { path: "billing", element: <AdminBillingPage /> },

&nbsp;     { path: "runs", element: <AdminRunsPage /> },

&nbsp;     { path: "controls", element: <AdminControlsPage /> },

&nbsp;   ],

&nbsp; },

]);

```



\### Roles



\* `ACA\_Admin`: full access (grant tier, lock/unlock, reconcile, rerun jobs)

\* `ACA\_Support`: read + grant trial + lock/unlock

\* `ACA\_FinOps`: read-only billing + usage KPIs



---



\## 3) Page skeletons (Spark/Fluent UI v9 style)



Below are minimal “compiles today” stubs you can drop in and iteratively flesh out.



\### `FindingsTier1Page.tsx` (Tier 1 report)



```tsx

import { useEffect, useState } from "react";

import { useParams, Link } from "react-router-dom";

import { Spinner } from "@fluentui/react-components";

import { appApi } from "../../api/appApi";

import { Tier1Report } from "../../types/models";

import { MoneyRangeBar } from "../../components/MoneyRangeBar";

import { EffortBadge } from "../../components/EffortBadge";



export function FindingsTier1Page() {

&nbsp; const { subscriptionId } = useParams();

&nbsp; const \[data, setData] = useState<Tier1Report | null>(null);

&nbsp; const \[loading, setLoading] = useState(true);



&nbsp; useEffect(() => {

&nbsp;   (async () => {

&nbsp;     setLoading(true);

&nbsp;     const r = await appApi.getTier1Report(subscriptionId!);

&nbsp;     setData(r);

&nbsp;     setLoading(false);

&nbsp;   })();

&nbsp; }, \[subscriptionId]);



&nbsp; if (loading) return <Spinner />;

&nbsp; if (!data) return <div>Report not available.</div>;



&nbsp; return (

&nbsp;   <div style={{ maxWidth: 1100 }}>

&nbsp;     <h1>Free Scan Summary</h1>

&nbsp;     <p>Subscription: {subscriptionId}</p>



&nbsp;     <div style={{ marginTop: 16 }}>

&nbsp;       {data.findings.map(f => (

&nbsp;         <div key={f.id} style={{ padding: 12, border: "1px solid #ddd", marginBottom: 10 }}>

&nbsp;           <div style={{ fontWeight: 600 }}>{f.title}</div>

&nbsp;           <div style={{ opacity: 0.8 }}>{f.category}</div>

&nbsp;           <MoneyRangeBar low={f.estimatedSavingLow} high={f.estimatedSavingHigh} currency={data.currency} />

&nbsp;           <EffortBadge effort={f.effortClass} />

&nbsp;         </div>

&nbsp;       ))}

&nbsp;     </div>



&nbsp;     <div style={{ marginTop: 24 }}>

&nbsp;       <Link to={`/app/upgrade/${subscriptionId}`}>Unlock Full Report</Link>

&nbsp;     </div>

&nbsp;   </div>

&nbsp; );

}

```



\### `AdminCustomersPage.tsx` (support + operations)



```tsx

import { useState } from "react";

import { adminApi } from "../../api/adminApi";



export function AdminCustomersPage() {

&nbsp; const \[q, setQ] = useState("");

&nbsp; const \[rows, setRows] = useState<any\[]>(\[]);



&nbsp; async function search() {

&nbsp;   const r = await adminApi.searchCustomers(q);

&nbsp;   setRows(r.items);

&nbsp; }



&nbsp; return (

&nbsp;   <div style={{ maxWidth: 1200 }}>

&nbsp;     <h1>Customers</h1>

&nbsp;     <div style={{ display: "flex", gap: 8 }}>

&nbsp;       <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search subscriptionId / stripeCustomerId / email" />

&nbsp;       <button onClick={search}>Search</button>

&nbsp;     </div>



&nbsp;     <div style={{ marginTop: 16 }}>

&nbsp;       {rows.map(r => (

&nbsp;         <div key={r.subscriptionId} style={{ padding: 12, border: "1px solid #ddd", marginBottom: 10 }}>

&nbsp;           <div style={{ fontWeight: 600 }}>{r.subscriptionId}</div>

&nbsp;           <div>Tier: {r.tier} • Status: {r.paymentStatus}</div>

&nbsp;           <div>Last activity: {r.lastActivityUtc ?? "—"}</div>

&nbsp;         </div>

&nbsp;       ))}

&nbsp;     </div>

&nbsp;   </div>

&nbsp; );

}

```



---



\## 4) Frontend API clients (customer + admin)



\### `frontend/src/app/api/client.ts`



```ts

export const apiBase = import.meta.env.VITE\_API\_BASE\_URL || "/api";



async function http<T>(path: string, init?: RequestInit): Promise<T> {

&nbsp; const res = await fetch(`${apiBase}${path}`, {

&nbsp;   ...init,

&nbsp;   headers: {

&nbsp;     "Content-Type": "application/json",

&nbsp;     ...(init?.headers || {})

&nbsp;   },

&nbsp;   credentials: "include" // or bearer token if you do SPA token flow

&nbsp; });

&nbsp; if (!res.ok) throw new Error(await res.text());

&nbsp; return res.json() as Promise<T>;

}



export const client = { http };

```



\### `frontend/src/app/api/appApi.ts`



```ts

import { client } from "./client";

import type { Tier1Report } from "../types/models";



export const appApi = {

&nbsp; getTier1Report: (subscriptionId: string) =>

&nbsp;   client.http<Tier1Report>(`/v1/reports/tier1?subscriptionId=${encodeURIComponent(subscriptionId)}`),



&nbsp; startCollection: (subscriptionId: string) =>

&nbsp;   client.http(`/v1/collect/start`, { method: "POST", body: JSON.stringify({ subscriptionId }) }),



&nbsp; getStatus: (subscriptionId: string) =>

&nbsp;   client.http(`/v1/collect/status?subscriptionId=${encodeURIComponent(subscriptionId)}`)

};

```



\### `frontend/src/app/api/adminApi.ts`



```ts

import { client } from "./client";



export const adminApi = {

&nbsp; kpis: () => client.http(`/v1/admin/kpis`),



&nbsp; searchCustomers: (query: string) =>

&nbsp;   client.http(`/v1/admin/customers?query=${encodeURIComponent(query)}`),



&nbsp; lockSubscription: (subscriptionId: string, reason: string) =>

&nbsp;   client.http(`/v1/admin/subscriptions/${encodeURIComponent(subscriptionId)}/lock`,

&nbsp;     { method: "POST", body: JSON.stringify({ reason }) }),



&nbsp; grantEntitlement: (subscriptionId: string, tier: number, days: number, reason: string) =>

&nbsp;   client.http(`/v1/admin/entitlements/grant`,

&nbsp;     { method: "POST", body: JSON.stringify({ subscriptionId, tier, days, reason }) }),



&nbsp; reconcileStripe: () =>

&nbsp;   client.http(`/v1/admin/stripe/reconcile`, { method: "POST" }),

};

```



---



\## 5) OpenAPI additions for `/v1/admin/\*` (drop into `docs/api-spec.md` or your OpenAPI file)



```yaml

paths:

&nbsp; /v1/admin/kpis:

&nbsp;   get:

&nbsp;     summary: Admin KPIs

&nbsp;     security: \[{ bearerAuth: \[] }]

&nbsp;     responses:

&nbsp;       "200":

&nbsp;         description: KPI snapshot

&nbsp;         content:

&nbsp;           application/json:

&nbsp;             schema:

&nbsp;               $ref: "#/components/schemas/AdminKpis"



&nbsp; /v1/admin/customers:

&nbsp;   get:

&nbsp;     summary: Search customers and subscriptions

&nbsp;     security: \[{ bearerAuth: \[] }]

&nbsp;     parameters:

&nbsp;       - in: query

&nbsp;         name: query

&nbsp;         schema: { type: string }

&nbsp;         required: true

&nbsp;     responses:

&nbsp;       "200":

&nbsp;         description: Customer search results

&nbsp;         content:

&nbsp;           application/json:

&nbsp;             schema:

&nbsp;               $ref: "#/components/schemas/AdminCustomerSearchResponse"



&nbsp; /v1/admin/entitlements/grant:

&nbsp;   post:

&nbsp;     summary: Grant entitlement (trial or manual override)

&nbsp;     security: \[{ bearerAuth: \[] }]

&nbsp;     requestBody:

&nbsp;       required: true

&nbsp;       content:

&nbsp;         application/json:

&nbsp;           schema: { $ref: "#/components/schemas/AdminGrantEntitlementRequest" }

&nbsp;     responses:

&nbsp;       "200":

&nbsp;         description: Updated entitlement

&nbsp;         content:

&nbsp;           application/json:

&nbsp;             schema: { $ref: "#/components/schemas/Entitlement" }



&nbsp; /v1/admin/subscriptions/{subscriptionId}/lock:

&nbsp;   post:

&nbsp;     summary: Lock subscription (abuse/chargeback prevention)

&nbsp;     security: \[{ bearerAuth: \[] }]

&nbsp;     parameters:

&nbsp;       - in: path

&nbsp;         name: subscriptionId

&nbsp;         required: true

&nbsp;         schema: { type: string }

&nbsp;     requestBody:

&nbsp;       required: true

&nbsp;       content:

&nbsp;         application/json:

&nbsp;           schema: { $ref: "#/components/schemas/AdminLockRequest" }

&nbsp;     responses:

&nbsp;       "204": { description: Locked }



&nbsp; /v1/admin/stripe/reconcile:

&nbsp;   post:

&nbsp;     summary: Reconcile Stripe subscriptions to entitlements (repair job)

&nbsp;     security: \[{ bearerAuth: \[] }]

&nbsp;     responses:

&nbsp;       "202":

&nbsp;         description: Reconcile started

&nbsp;         content:

&nbsp;           application/json:

&nbsp;             schema: { $ref: "#/components/schemas/AdminJobAccepted" }



components:

&nbsp; schemas:

&nbsp;   AdminKpis:

&nbsp;     type: object

&nbsp;     properties:

&nbsp;       utc:

&nbsp;         type: string

&nbsp;         format: date-time

&nbsp;       mrrCad:

&nbsp;         type: number

&nbsp;       activeSubscriptions:

&nbsp;         type: integer

&nbsp;       scansLast24h:

&nbsp;         type: integer

&nbsp;       analysesLast24h:

&nbsp;         type: integer

&nbsp;       deliveriesLast24h:

&nbsp;         type: integer

&nbsp;       failureRatePctLast24h:

&nbsp;         type: number

&nbsp;     required: \[utc, activeSubscriptions]



&nbsp;   AdminCustomerSearchResponse:

&nbsp;     type: object

&nbsp;     properties:

&nbsp;       items:

&nbsp;         type: array

&nbsp;         items:

&nbsp;           $ref: "#/components/schemas/AdminCustomerRow"

&nbsp;     required: \[items]



&nbsp;   AdminCustomerRow:

&nbsp;     type: object

&nbsp;     properties:

&nbsp;       subscriptionId: { type: string }

&nbsp;       stripeCustomerId: { type: string, nullable: true }

&nbsp;       tier: { type: integer }

&nbsp;       paymentStatus: { type: string }

&nbsp;       lastActivityUtc: { type: string, format: date-time, nullable: true }

&nbsp;       isLocked: { type: boolean }

&nbsp;     required: \[subscriptionId, tier, paymentStatus, isLocked]



&nbsp;   AdminGrantEntitlementRequest:

&nbsp;     type: object

&nbsp;     properties:

&nbsp;       subscriptionId: { type: string }

&nbsp;       tier: { type: integer, enum: \[1, 2, 3] }

&nbsp;       days: { type: integer, minimum: 1, maximum: 365 }

&nbsp;       reason: { type: string }

&nbsp;     required: \[subscriptionId, tier, days, reason]



&nbsp;   AdminLockRequest:

&nbsp;     type: object

&nbsp;     properties:

&nbsp;       reason: { type: string }

&nbsp;     required: \[reason]



&nbsp;   AdminJobAccepted:

&nbsp;     type: object

&nbsp;     properties:

&nbsp;       jobId: { type: string }

&nbsp;       acceptedUtc: { type: string, format: date-time }

&nbsp;     required: \[jobId, acceptedUtc]

```



---



\## 6) Cosmos: add `admin\_audit\_events` container (schema + PK)



Add one more container (recommended) to support “same app, but admin is safe.”



\*\*Container\*\*



\* name: `admin\_audit\_events`

\* PK: `/subscriptionId` (or `/actorTenantId` if you prefer ops-centric queries; I recommend `/subscriptionId`)



\*\*Document schema\*\*



```json

{

&nbsp; "id": "aae::<uuid>",

&nbsp; "subscriptionId": "<clientSubscriptionIdOrInternal>",

&nbsp; "utc": "2026-02-26T18:12:34Z",

&nbsp; "actor": {

&nbsp;   "userId": "<entra-oid>",

&nbsp;   "upn": "user@domain",

&nbsp;   "roles": \["ACA\_Support"]

&nbsp; },

&nbsp; "action": "ENTITLEMENT\_GRANTED",

&nbsp; "target": {

&nbsp;   "type": "entitlement",

&nbsp;   "id": "entitlement::<subscriptionId>"

&nbsp; },

&nbsp; "request": {

&nbsp;   "tier": 2,

&nbsp;   "days": 7,

&nbsp;   "reason": "Pilot goodwill"

&nbsp; },

&nbsp; "result": {

&nbsp;   "status": "success",

&nbsp;   "message": "Granted tier 2 until 2026-03-04"

&nbsp; },

&nbsp; "correlationId": "<trace-id>",

&nbsp; "ip": "<optional>",

&nbsp; "userAgent": "<optional>"

}

```



And create the container with your existing az cli pattern (same as others):



\* PK `/subscriptionId`

\* RU same as others (400 for dev)



---



\## 7) Next concrete step I can generate



If you want the \*\*next commit-ready bundle\*\*, say:

\*\*“generate the exact Spark files for these stubs”\*\* and I’ll output:



\* `router.tsx`, layouts, role guards, and all 9 page files

\* `appApi/adminApi/client.ts`

\* type models for Tier1 report + admin rows

\* the OpenAPI yaml fragment as a standalone `docs/openapi.admin.yaml`



All of this stays aligned with your Phase 1/2 plan and the existing marco\* sandbox inventory you’re reusing. 



