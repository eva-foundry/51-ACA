Here is a \*\*Copilot-ready context summary\*\* you can drop into your repo or prompt file to guide implementation of the \*\*client subscription extraction and pre-flight automation\*\* for ACA.



---



\## ACA collector context for Copilot



ACA is a \*\*read-only Azure Cost Advisor SaaS\*\*. It connects to a client Azure subscription, runs \*\*pre-flight permission probes\*\*, then extracts \*\*inventory, cost, Advisor, policy, and optional activity/network signals\*\* into ACA-owned storage for later analysis and script generation. ACA \*\*never writes to the client subscription\*\*; clients review and deploy generated scripts themselves.



\### Product and technical intent



The client flow is:



1\. Client signs in with \*\*multi-tenant Microsoft identity\*\*

2\. ACA runs \*\*pre-flight validation\*\*

3\. ACA collects \*\*read-only subscription data\*\*

4\. ACA analyzes findings and generates prioritized recommendations

5\. ACA optionally packages \*\*IaC / scripts\*\* for the client to download

6\. The \*\*client\*\* decides when and how to implement changes; ACA remains advisory/read-only.



ACA Phase 1/2 collection scope is centered on:



\* \*\*Azure Resource Graph\*\* for inventory

\* \*\*Cost Management Query API\*\* for \*\*91 days\*\* of daily cost data

\* \*\*Azure Advisor API\*\* for recommendations

\* \*\*Azure Policy Insights\*\* for compliance summaries

\* \*\*ARM reads\*\* for network topology

\* \*\*Activity Logs / Log Analytics\*\* only if available and authorized, mainly for idle detection and stronger confidence scoring.



---



\## What Copilot should build



\### 1. Pre-flight authorization and capability probe



Build a \*\*pre-flight module\*\* that validates the client’s read-only access before any collection starts. The probe should be callable as:



\* API: `POST /v1/auth/preflight`

\* Collector CLI / job mode: `--preflight-only`



\### 2. Data extraction automation



Build a \*\*collector service / Container App Job\*\* that, after pre-flight success, pulls data from the client subscription and writes normalized results to ACA Cosmos containers. The collector should support:



\* inventory extraction

\* cost extraction

\* Advisor extraction

\* optional policy/network/activity extraction

\* progress reporting

\* retry / backoff for Azure API throttling

\* scan lifecycle state updates.



---



\## Pre-flight goals



The pre-flight step must determine, for a given client subscription:



1\. \*\*Can ACA authenticate and get an ARM token?\*\*

2\. \*\*What Azure roles / effective permissions does the user have?\*\*

3\. \*\*Which data sources are accessible?\*\*

4\. \*\*How deep can extraction go based on permissions and available services?\*\*

5\. \*\*Can ACA proceed, proceed with warnings, or must it stop?\*\*



\### Required baseline permissions



The minimum read-only posture for useful collection is:



\* \*\*Reader\*\* at subscription scope

\* \*\*Cost Management Reader\*\* at subscription scope

\* \*\*Advisor read access / Azure Advisor Reader\*\*

\* ability to query \*\*Resource Graph\*\*

\* availability of \*\*~90/91 days of cost data\*\*



\### Optional additional permissions / sources



If available, the collector should also detect and use:



\* \*\*Policy Insights Reader\*\* or equivalent ability to read policy compliance

\* \*\*Log Analytics Reader\*\* at workspace scope, if the client wants stronger activity / idle detection signals

\* ARM read permissions sufficient for topology reads such as NSGs, VNets, peerings, private DNS, public IPs.



---



\## Recommended pre-flight result model



Pre-flight should not return only pass/fail. It should return a \*\*capability matrix\*\* like:



\* `PASS`

\* `PASS\_WITH\_WARNINGS`

\* `FAIL`



for each probe, plus a top-level result. This matches the current plan and UX expectation. 



\### Suggested probe list



Copilot should implement at least these five baseline probes:



1\. \*\*ARM auth token acquired\*\*

2\. \*\*Resource Graph query works\*\*

3\. \*\*Subscription Reader / inventory read works\*\*

4\. \*\*Cost Management query works\*\*

5\. \*\*Advisor recommendations read works\*\*

6\. \*\*90/91-day cost window available\*\*

&nbsp;  Optional:

7\. \*\*Policy Insights available\*\*

8\. \*\*Log Analytics / activity source available\*\*

9\. \*\*Network topology reads available\*\*



\### Suggested pre-flight output shape



For each probe, return:



\* `probe\_name`

\* `status`

\* `scope\_tested`

\* `required\_role\_or\_permission`

\* `actual\_result`

\* `error\_code`

\* `human\_guidance`

\* `can\_continue\_without\_this`

\* `collection\_impact`



Also persist `preflight\_result` into the `scans` container. The frontend should be able to show green/red/yellow checks to the client.



---



\## Determine user Azure roles and effective permission depth



Copilot should implement a \*\*permission-depth assessment\*\*, not just role-name lookup.



\### Why



Role names alone are not enough. ACA needs to know \*\*what can actually be extracted\*\*. For example:



\* a user may have \*\*Reader\*\* but not \*\*Cost Management Reader\*\*

\* a user may see the subscription but not policy insights

\* a user may have activity visibility only in some workspaces

\* some sources may exist technically but be empty or unavailable. This is already reflected in the design where ACA may proceed with warnings instead of failing outright.



\### Recommended depth levels



Have the pre-flight produce a computed extraction depth such as:



\* `DEPTH\_0\_NONE`

&nbsp; No usable extraction possible

\* `DEPTH\_1\_INVENTORY\_ONLY`

&nbsp; Reader/Resource Graph works, but no cost or Advisor

\* `DEPTH\_2\_INVENTORY\_COST`

&nbsp; Inventory + Cost Management available

\* `DEPTH\_3\_STANDARD`

&nbsp; Inventory + Cost + Advisor available

\* `DEPTH\_4\_ENHANCED`

&nbsp; Standard + Policy + Network signals

\* `DEPTH\_5\_ACTIVITY\_ENHANCED`

&nbsp; Enhanced + Activity / Log Analytics idle signals



This depth should drive the UI messaging and rule-engine coverage. It also lets ACA explain clearly what the scan includes and what it cannot assess. This aligns with the current scoped collection model.



---



\## Data that should be extracted



\### A. Resource inventory



Use \*\*Azure Resource Graph\*\* to extract all resources in the subscription. Minimum normalized fields:



\* subscriptionId

\* resourceId

\* type

\* name

\* resourceGroup

\* location / region

\* SKU / size where applicable

\* tags

\* kind / properties as needed by rules



Target performance in the plan is inventory collection in under 60s for subscriptions up to ~500 resources. 



\### B. Cost data



Use \*\*Cost Management Query API\*\* to pull \*\*91 days\*\* of \*\*daily\*\* cost rows, handling pagination and throttling. Minimum normalized fields planned are:



\* date

\* MeterCategory

\* MeterName

\* resourceGroup

\* resourceId (hashed if needed for privacy)

\* PreTaxCost

\* subscription currency



The collector should include exponential backoff for `429` rate limits. 



\### C. Advisor recommendations



Pull all \*\*Azure Advisor\*\* recommendations across categories and store both normalized fields and raw JSON for traceability.



\### D. Policy signals



If available, collect policy compliance summaries:



\* compliant counts

\* non-compliant counts

\* important policy gaps if accessible.



\### E. Network topology signals



If permitted, collect:



\* NSG rule counts

\* public IP count

\* VNet peering map

\* private DNS zones

\* other lightweight topology indicators that support findings like stale environments, network sprawl, or governance gaps.



\### F. Activity / usage signals



If Log Analytics / Activity Logs are enabled and readable, collect enough to strengthen:



\* idle resource detection

\* “ghost resource” confidence

\* night/weekend inactivity patterns

\* dev environment shutdown opportunity detection.

&nbsp; This source is optional and should never block the standard scan. 



---



\## Cosmos write model



The collector writes only to \*\*ACA-owned storage\*\*, never to the client subscription. Current container layout already expects:



\* `scans`

\* `inventories`

\* `cost-data`

\* `advisor`

\* later `findings`, `deliverables`, etc.



All tenant reads/writes must use `partition\_key = subscriptionId`, with no cross-tenant queries.



\### Minimum collector write expectations



During collection:



\* create / update scan lifecycle in `scans`

\* write inventory snapshot rows to `inventories`

\* write daily cost rows to `cost-data`

\* write raw/normalized Advisor data to `advisor`

\* record counts and stats back to the scan record, such as `inventoryCount`, `costRows`, `advisorRecs`



---



\## Collection lifecycle and status model



Implement scan statuses at minimum as:



\* `queued`

\* `running`

\* `succeeded`

\* `failed`

\* optionally `preflight\_failed`, `preflight\_warn`, `collected`



The API should expose collection status so the frontend can poll and show progress. The current plan already calls for scan status transitions and a status endpoint. 



---



\## Error handling expectations



Copilot should build the collector to fail \*\*gracefully and informatively\*\*.



\### Rules



\* Missing mandatory permissions → fail pre-flight with actionable guidance

\* Missing optional permissions → proceed with warning and reduced extraction depth

\* Azure throttling (`429`) → retry with exponential backoff

\* Empty cost window → fail or downgrade depending on whether insufficient data invalidates value

\* Partial-source failures → capture warnings in scan record and continue where safe.



\### Guidance output



Errors should be phrased for customers, e.g.:



\* “Missing Cost Management Reader role at subscription scope”

\* “Policy Insights not accessible; policy-based findings will be skipped”

\* “Activity-based idle detection unavailable because Log Analytics Reader is not granted”



---



\## Security and posture requirements



ACA must remain \*\*strictly read-only\*\*:



\* no write calls into client subscriptions

\* no IAM changes

\* no deployment of agents into client tenants

\* no mutation of resources

\* clients retain control and implement changes themselves.



All secrets belong in \*\*Key Vault\*\* and production access should use managed identity patterns where applicable. 



---



\## Recommended implementation modules for Copilot



\### `auth/preflight.py`



Responsibilities:



\* exchange delegated auth / validate token

\* run RBAC and capability probes

\* compute extraction depth

\* persist preflight result

\* return client-facing checklist result



\### `collector/resource\_graph.py`



Responsibilities:



\* query full resource inventory

\* normalize resource rows



\### `collector/cost\_management.py`



Responsibilities:



\* pull 91-day daily cost rows

\* paginate

\* retry on throttling

\* normalize for Cosmos



\### `collector/advisor.py`



Responsibilities:



\* pull all Advisor recommendations

\* normalize and preserve raw payload



\### `collector/policy.py`



Responsibilities:



\* pull compliance summary where available



\### `collector/network.py`



Responsibilities:



\* derive topology indicators from ARM read calls



\### `collector/activity.py`



Responsibilities:



\* optional usage/idle/activity signals when permissions and data sources exist



\### `collector/orchestrator.py`



Responsibilities:



\* manage scan lifecycle

\* invoke source collectors

\* aggregate stats

\* write status updates

\* support `--preflight-only`



\### `api/routes/preflight.py`



Expose:



\* `POST /v1/auth/preflight`

\* `GET /v1/preflight/{scan\_id}`



\### `api/routes/collect.py`



Expose:



\* `POST /v1/collect/start`

\* `GET /v1/collect/status/{scan\_id}`



These align with the current architecture and flow already described in the docs.



---



\## Copilot implementation guidance



Copilot should optimize for:



\* \*\*read-only access only\*\*

\* \*\*clear customer guidance\*\*

\* \*\*partial capability tolerance\*\*

\* \*\*strong normalization\*\*

\* \*\*multi-tenant isolation by subscriptionId\*\*

\* \*\*future compatibility with analysis rules and Pareto scoring\*\*



The pre-flight is not just an auth check; it is a \*\*capability and extraction-depth probe\*\* that decides how valuable the scan can be before collection starts. That is the key design principle to keep.



---



\## Short version for Copilot header



ACA needs a \*\*pre-flight + collector subsystem\*\* for client Azure subscriptions. It must:



\* authenticate with \*\*read-only delegated access\*\*

\* probe the client’s \*\*effective Azure access\*\*

\* determine \*\*what data can be extracted\*\* and at what \*\*depth\*\*

\* collect \*\*inventory, 91-day cost, Advisor, and optional policy/network/activity signals\*\*

\* write normalized results to \*\*ACA Cosmos containers\*\*

\* provide \*\*clear PASS / WARN / FAIL guidance\*\* to the client

\* never write to the client subscription

\* support later analysis and script generation.



If you want, I can turn this into a \*\*single `COPILOT\_CONTEXT\_ACA\_COLLECTOR.md` file\*\* format next.



