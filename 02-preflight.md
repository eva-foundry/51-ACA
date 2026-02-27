Below is a \*\*ready-to-drop-in doc\*\* for ACA: \*\*Onboarding \& Permission Validation (Pre-Flight) Spec\*\*. It is aligned to your ACA collection scope, roles, and architecture plan.  



---



\# ACA Onboarding \& Permission Validation Spec



\*\*Document ID:\*\* ACA-SPEC-ONBOARD-001

\*\*Version:\*\* 0.1

\*\*Date:\*\* 2026-02-26

\*\*Applies to:\*\* Phase 1 (marco\*) + Phase 2 (private ACA subscription) 



\## 1. Purpose



Define the \*\*client onboarding flow\*\* and the \*\*pre-flight permission validation\*\* that ACA performs \*\*after login\*\* and \*\*before\*\* any data extraction. The pre-flight ensures:



\* The authenticated identity is valid for the intended Azure tenant/subscription

\* Required Azure permissions exist for \*\*all collection tasks\*\*

\* ACA can safely proceed with extraction, or provide an actionable \*\*“missing permissions”\*\* report



---



\## 2. Scope of Pre-Flight (What it validates)



ACA validates access for the following collection categories (read-only):



\* Subscription discovery \& selection

\* Resource inventory enumeration

\* Cost Management query (91 days daily)

\* Azure Advisor recommendations

\* Azure Policy compliance state

\* Network topology signals

\* (Optional) Log Analytics read (only if enabled)

\* (Optional) Activity/Audit logs (only if enabled)



These map directly to ACA’s collector scope.  



---



\## 3. Supported onboarding modes



ACA supports multiple “access patterns” so enterprises can choose what fits their governance.



\### Mode A — Delegated user sign-in (quick scan)



\* Client user signs in with Entra ID (MFA/CA applies)

\* ACA uses \*\*delegated\*\* Microsoft identity token

\* ACA performs pre-flight checks and runs collection



\*\*Notes:\*\* Some tenants disable user consent; in that case ACA must fall back to Mode B.



\### Mode B — Client-provisioned app identity (enterprise)



\* Client creates an \*\*App Registration / Service Principal\*\* in their tenant

\* Client assigns RBAC roles at subscription scope

\* ACA authenticates as the app (no user refresh token dependency)



\### Mode C — Azure Lighthouse (MSP pattern)



\* Client delegates subscription access to ACA’s tenant

\* ACA uses its own identities while access remains client-controlled



---



\## 4. Required permissions (minimum)



This section defines the minimum roles needed to successfully complete ACA’s collector tasks. 



\### 4.1 Mandatory roles (baseline)



\*\*At subscription scope:\*\*



\* \*\*Reader\*\*

\* \*\*Cost Management Reader\*\*



\### 4.2 Conditional roles (feature-dependent)



\* \*\*Log Analytics Reader\*\*

&nbsp; Required only if ACA is configured to query workspaces for usage/idle signals.



\### 4.3 Notes on “Reader”



Reader is sufficient for:



\* Azure Advisor recommendations (commonly available through ARM)

\* Resource inventory enumeration

\* Network resource enumeration

\* Policy assignments listing (but Policy \*\*state\*\* often needs Policy Insights calls; pre-flight verifies)



---



\## 5. Pre-Flight workflow (high level)



\### Step 0 — Start pre-flight session



\* Generate `preflightId`

\* Record an \*\*audit event\*\*: `preflight.started`



\### Step 1 — Acquire token \& validate identity



\* Confirm token is valid for Azure Resource Manager (ARM)

\* Resolve:



&nbsp; \* `tenantId`

&nbsp; \* `principalId` (user/object id or service principal id)

&nbsp; \* `principalType` (User | ServicePrincipal)



\### Step 2 — Enumerate accessible subscriptions



\* List subscriptions visible to the principal

\* If the client entered a subscriptionId, verify it appears in the list



\### Step 3 — Validate RBAC at subscription scope



\* Verify principal has required roles (Reader + Cost Management Reader, plus optional roles if enabled)



\### Step 4 — Capability probes (per collection surface)



Run fast, low-cost “can I read this?” probes for each collector feature. If a probe fails, capture:



\* failing API surface

\* required role / permission hint

\* error code \& message

\* remediation text



\### Step 5 — Pre-flight verdict



Return:



\* `PASS` (collector can run)

\* `PASS\_WITH\_WARNINGS` (some optional signals unavailable)

\* `FAIL` (mandatory capability missing)



Record `preflight.completed` audit event.



---



\## 6. Capability probes (the core of validation)



Each probe is a \*\*real API call\*\* that closely matches actual extraction so we don’t “green-check” based on assumptions.



\### 6.1 Probe: Subscription discovery (mandatory)



\*\*Goal:\*\* confirm the identity can list subscriptions.



\* Call: `GET /subscriptions?api-version=2020-01-01`

\* Pass condition: HTTP 200 and includes target subscriptionId



Fail → \*\*cannot proceed\*\*.



---



\### 6.2 Probe: Resource inventory via Azure Resource Graph (mandatory)



\*\*Goal:\*\* confirm ACA can enumerate resources quickly at scale.



\* Call: Resource Graph query at subscription scope (e.g., “resources | project … | take 1”)

\* Pass: HTTP 200, returns any record or empty (empty is still pass)



Fail → \*\*cannot proceed\*\* (inventory is mandatory).



---



\### 6.3 Probe: Cost Management query (mandatory)



\*\*Goal:\*\* confirm ACA can pull daily costs.



\* Call: Cost query for last 7 days daily granularity (fast probe)

\* Pass: HTTP 200 and returns rows (or empty if truly zero)



Fail → \*\*cannot proceed\*\*.



---



\### 6.4 Probe: Advisor recommendations (mandatory)



\*\*Goal:\*\* confirm ACA can pull advisor recs.



\* Call: Advisor recommendations list for subscription

\* Pass: HTTP 200 (empty list still pass)



Fail → treat as \*\*FAIL\*\* (because ACA relies on Advisor + rules). 



---



\### 6.5 Probe: Policy compliance (mandatory)



\*\*Goal:\*\* confirm ACA can read policy state summary.



\* Call: Policy Insights summary/state (subscription scope)

\* Pass: HTTP 200 (empty is pass)



Fail → depending on product tier:



\* Tier 1 may continue with warning (if you want)

\* Tier 2/3 should likely treat as mandatory (recommended)



(Your plan expects policy state to be present; default is \*\*mandatory\*\*.) 



---



\### 6.6 Probe: Network topology signals (mandatory)



\*\*Goal:\*\* confirm ACA can read key network resources.



Minimum probe set:



\* List NSGs

\* List Public IPs

\* List VNets

\* List Private DNS zones (if used)



Pass: HTTP 200 across probes (empty lists are pass)



Fail → default to \*\*PASS\_WITH\_WARNINGS\*\* if only some network signals fail, unless you require red-team signals for Tier 2+. 



---



\### 6.7 Probe: Log Analytics queries (optional)



Only executed when ACA feature flag `enableLogAnalyticsSignals=true`.



\* Call: list workspaces + run a tiny query

\* Pass: HTTP 200



Fail → \*\*PASS\_WITH\_WARNINGS\*\*.



---



\## 7. Pre-Flight output contract (JSON)



\### 7.1 Response schema (from `/onboarding/preflight`)



```json

{

&nbsp; "preflightId": "pf\_20260226\_001",

&nbsp; "timestampUtc": "2026-02-26T18:12:01Z",

&nbsp; "principal": {

&nbsp;   "tenantId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",

&nbsp;   "principalId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",

&nbsp;   "principalType": "User",

&nbsp;   "displayName": "Jane Doe"

&nbsp; },

&nbsp; "subscription": {

&nbsp;   "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",

&nbsp;   "displayName": "Client Dev Subscription",

&nbsp;   "state": "Enabled"

&nbsp; },

&nbsp; "requiredRoles": \[

&nbsp;   { "scope": "subscription", "roleName": "Reader", "mandatory": true },

&nbsp;   { "scope": "subscription", "roleName": "Cost Management Reader", "mandatory": true },

&nbsp;   { "scope": "subscription", "roleName": "Log Analytics Reader", "mandatory": false }

&nbsp; ],

&nbsp; "roleValidation": {

&nbsp;   "status": "PASS",

&nbsp;   "evidence": \[

&nbsp;     { "roleName": "Reader", "scope": "/subscriptions/...", "verified": true },

&nbsp;     { "roleName": "Cost Management Reader", "scope": "/subscriptions/...", "verified": true }

&nbsp;   ]

&nbsp; },

&nbsp; "capabilityProbes": \[

&nbsp;   {

&nbsp;     "name": "subscriptions.list",

&nbsp;     "mandatory": true,

&nbsp;     "status": "PASS",

&nbsp;     "httpStatus": 200,

&nbsp;     "latencyMs": 120,

&nbsp;     "evidenceRef": "ev\_01"

&nbsp;   },

&nbsp;   {

&nbsp;     "name": "resourcegraph.query",

&nbsp;     "mandatory": true,

&nbsp;     "status": "PASS",

&nbsp;     "httpStatus": 200,

&nbsp;     "latencyMs": 310,

&nbsp;     "evidenceRef": "ev\_02"

&nbsp;   },

&nbsp;   {

&nbsp;     "name": "cost.query.7d.daily",

&nbsp;     "mandatory": true,

&nbsp;     "status": "PASS",

&nbsp;     "httpStatus": 200,

&nbsp;     "latencyMs": 680,

&nbsp;     "evidenceRef": "ev\_03"

&nbsp;   },

&nbsp;   {

&nbsp;     "name": "advisor.recommendations.list",

&nbsp;     "mandatory": true,

&nbsp;     "status": "PASS",

&nbsp;     "httpStatus": 200,

&nbsp;     "latencyMs": 240,

&nbsp;     "evidenceRef": "ev\_04"

&nbsp;   },

&nbsp;   {

&nbsp;     "name": "policyinsights.summary",

&nbsp;     "mandatory": true,

&nbsp;     "status": "PASS",

&nbsp;     "httpStatus": 200,

&nbsp;     "latencyMs": 260,

&nbsp;     "evidenceRef": "ev\_05"

&nbsp;   },

&nbsp;   {

&nbsp;     "name": "network.nsg.list",

&nbsp;     "mandatory": true,

&nbsp;     "status": "PASS",

&nbsp;     "httpStatus": 200,

&nbsp;     "latencyMs": 190,

&nbsp;     "evidenceRef": "ev\_06"

&nbsp;   }

&nbsp; ],

&nbsp; "verdict": {

&nbsp;   "status": "PASS",

&nbsp;   "canRunCollector": true,

&nbsp;   "warnings": \[],

&nbsp;   "blockers": \[]

&nbsp; },

&nbsp; "nextActions": \[

&nbsp;   { "action": "RUN\_COLLECTOR", "endpoint": "POST /collector/run", "recommended": true }

&nbsp; ]

}

```



\### 7.2 Failure example (missing Cost Management Reader)



```json

{

&nbsp; "preflightId": "pf\_20260226\_009",

&nbsp; "verdict": {

&nbsp;   "status": "FAIL",

&nbsp;   "canRunCollector": false,

&nbsp;   "warnings": \[],

&nbsp;   "blockers": \[

&nbsp;     {

&nbsp;       "code": "MISSING\_PERMISSION",

&nbsp;       "capability": "cost.query.7d.daily",

&nbsp;       "requiredRole": "Cost Management Reader",

&nbsp;       "scope": "/subscriptions/xxx",

&nbsp;       "message": "Cost Management query access denied.",

&nbsp;       "remediation": "Assign 'Cost Management Reader' at subscription scope, then re-run pre-flight."

&nbsp;     }

&nbsp;   ]

&nbsp; }

}

```



---



\## 8. Pre-Flight audit \& evidence (evidence-first)



ACA records:



\* `preflight.started`

\* `preflight.probe.executed` (one per probe)

\* `preflight.completed`



Each probe stores:



\* request metadata (no secrets)

\* response code

\* minimal response proof (hash or row count)

\* latency



This matches the “audit log: every pull timestamped and recorded” intent in your plan. 



---



\## 9. Pre-flight tasks (what to do immediately after login)



Once the app is logged in, ACA should execute these in order:



\### 9.1 Tenant \& subscription resolution



\* Detect tenantId

\* List subscriptions available

\* Let user select subscription (or validate pre-entered subscriptionId)



\### 9.2 Environment classification (optional but useful)



\* Detect if subscription name/tags indicate `dev/test/prod`

\* Record classification hint (used later for heuristics like log retention thresholds)



\### 9.3 Permissions check (RBAC)



\* Validate roles at subscription scope

\* Return role evidence



\### 9.4 Capability probes



\* Run the probe list as per Section 6



\### 9.5 “Data minimization” check (policy)



\* Confirm ACA collection policy settings:



&nbsp; \* retention window (default 90 days)

&nbsp; \* deletion on request

&nbsp; \* scope boundaries (partition key enforcement by subscriptionId) 



\### 9.6 Readiness decision



\* PASS → enable “Run Scan” CTA

\* FAIL → show “Fix permissions” with exact remediation text



---



\## 10. API endpoints (suggested)



\### 10.1 Onboarding endpoints



\* `POST /onboarding/preflight`



&nbsp; \* Input: subscriptionId (optional), feature flags

&nbsp; \* Output: PreFlight JSON response



\* `GET /onboarding/preflight/{preflightId}`



&nbsp; \* Returns stored preflight report



\### 10.2 Collector trigger (only if preflight PASS)



\* `POST /collector/run`



&nbsp; \* Input: subscriptionId, preflightId

&nbsp; \* Output: jobId, status URL



---



\## 11. UI requirements (minimal)



\### Pages / states



1\. \*\*Login\*\*

2\. \*\*Connect Subscription\*\*



&nbsp;  \* subscription dropdown from discovery

&nbsp;  \* “Run Pre-Flight” button

3\. \*\*Pre-Flight Results\*\*



&nbsp;  \* status badge: PASS / WARN / FAIL

&nbsp;  \* table of probes with pass/fail

&nbsp;  \* “Fix permissions” block with copy-paste role instructions

4\. \*\*Run Scan\*\*



&nbsp;  \* enabled only after PASS



---



\## 12. Implementation notes (guardrails)



\* \*\*No extraction\*\* before preflight PASS

\* If any mandatory probe fails → stop immediately

\* Pre-flight must be \*\*fast\*\* (target < 5 seconds typical)

\* Never store raw tokens in Cosmos; store in Key Vault / managed identity patterns (per your plan) 

\* Keep probe payloads minimal (row counts + hashes) to avoid sensitive data persistence



---



\## 13. Mapping to ACA roadmap



This spec implements the “delegated consent flow + inventory + cost + advisor + policy + network + audit log” collector readiness gate described in Phase 1 Milestone 1.2. 

It also supports Phase 2 enterprise hardening and multi-tenancy enforcement. 



---



If you want the next artifact in the same “documentation sprint” style, I can generate \*\*Role Assignment Instructions (Client-Facing)\*\* as a one-pager for:



\* Mode A (user delegated)

\* Mode B (service principal)

\* Mode C (Lighthouse)



…and a matching \*\*`ACCEPTANCE.md` preflight checklist\*\* section aligned to your Phase 1 sign-off gates. 



