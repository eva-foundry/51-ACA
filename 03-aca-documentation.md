Perfect -- let's keep building your \*\*ACA documentation pack\*\* so you can move fast and stay consistent.



Below are \*\*two ready-to-drop files\*\*:



1\. \*\*Client-Facing Role Assignment Guide (one-pager)\*\*

2\. \*\*ACCEPTANCE.md - Pre-Flight Section (Phase 1 \& 2 gates)\*\*



These align directly with your ACA plan and onboarding model.  



---



\# ?? FILE 1 -- `docs/client-access-guide.md`



```markdown

\# ACA -- Client Access Setup Guide

==================================



Version: 1.0

Audience: Client Azure administrators / cloud platform teams



Purpose

---------

This guide explains how to grant ACA read-only access to your Azure subscription

to perform a cost and optimization analysis.



ACA uses read-only access only. No resources are modified.



=============================================================================

OPTION 1 -- QUICK START (USER SIGN-IN)

=============================================================================



Best for:

\- Trial / free scan (Tier 1)

\- Small teams

\- Fast onboarding



Steps:

1\. Click "Connect Subscription" in ACA.

2\. Sign in with your Azure (Entra ID) account.

3\. Select your subscription.

4\. Click "Run Pre-Flight Check".



Requirements:

\- Your account must have at least:

&nbsp; - Reader role on the subscription

&nbsp; - Cost Management Reader role



Notes:

\- Some organizations disable user consent.

\- If sign-in fails, use Option 2.



=============================================================================

OPTION 2 -- SERVICE PRINCIPAL (RECOMMENDED)

=============================================================================



Best for:

\- Enterprise clients

\- Production subscriptions

\- Recurring scans



This creates a dedicated application identity for ACA.



-----------------------------------------

Step 1 -- Create App Registration

-----------------------------------------



Azure Portal -> Microsoft Entra ID -> App registrations -> New registration



Name: ACA-Reader

Supported account types: Single tenant



Save:

\- Application (client) ID

\- Directory (tenant) ID



-----------------------------------------

Step 2 -- Create Client Secret

-----------------------------------------



Certificates \& secrets -> New client secret



Copy the value immediately.



-----------------------------------------

Step 3 -- Assign Roles (Subscription)

-----------------------------------------



Azure Portal -> Subscriptions -> Your Subscription -> Access Control (IAM)



Add role assignments:



Role 1: Reader

Role 2: Cost Management Reader



Assign access to:

\- The ACA-Reader application



Optional (only if Log Analytics enabled):

\- Log Analytics Reader



-----------------------------------------

Step 4 -- Provide Credentials to ACA

-----------------------------------------



You will enter:



\- Tenant ID

\- Client ID

\- Client Secret

\- Subscription ID



ACA will validate access before running any scan.



=============================================================================

OPTION 3 -- AZURE LIGHTHOUSE (ADVANCED)

=============================================================================



Best for:

\- Managed service providers

\- Multi-subscription environments



Your organization delegates access to ACA's tenant using Azure Lighthouse.



Contact ACA support for onboarding templates.



=============================================================================

REQUIRED PERMISSIONS

=============================================================================



Minimum required roles (subscription scope):



\- Reader

\- Cost Management Reader



Optional:

\- Log Analytics Reader (only if log-based insights are enabled)



ACA does NOT require:

\- Contributor

\- Owner

\- Write permissions



=============================================================================

WHAT ACA COLLECTS

=============================================================================



ACA collects read-only metadata:



\- Resource inventory (types, tags, SKUs, regions)

\- Cost data (last 91 days, daily granularity)

\- Azure Advisor recommendations

\- Policy compliance summaries

\- Network topology signals (NSG, VNet, DNS)

\- Optional: Log Analytics metrics



No secrets or application data are accessed.



=============================================================================

SECURITY \& DATA HANDLING

=============================================================================



\- Read-only access only

\- Data encrypted in transit and at rest

\- Data retained for 90 days (configurable)

\- Data can be deleted on request

\- No cross-client data sharing



=============================================================================

TROUBLESHOOTING

=============================================================================



Error: "Missing permissions"

-> Ensure Reader and Cost Management Reader roles are assigned



Error: "Subscription not visible"

-> Ensure access is assigned at the correct subscription scope



Error: "Cost data unavailable"

-> Confirm Cost Management Reader role is assigned



=============================================================================

SUPPORT

=============================================================================



Contact ACA support for assistance with setup.

```



---



\# ?? FILE 2 -- `ACCEPTANCE.md` (Pre-Flight Section)



This plugs directly into your Phase 1 / Phase 2 acceptance gates.



```markdown

=============================================================================

ACA ACCEPTANCE CRITERIA

=============================================================================



Section: Pre-Flight Validation

Version: 1.0



This section defines the acceptance criteria for onboarding and permission validation.



Pre-flight MUST pass before any data collection is executed.



=============================================================================

PHASE 1 -- INTERNAL (marco\* sandbox)

=============================================================================



Objective:

Validate end-to-end onboarding, permission checks, and readiness for collection.



-----------------------------------------

ACCEPTANCE CHECKLIST

-----------------------------------------



\[ ] User successfully signs in via delegated flow

\[ ] Token acquired and valid for Azure Resource Manager



\[ ] Subscriptions list retrieved successfully

\[ ] Target subscription selectable in UI



-----------------------------------------

RBAC VALIDATION

-----------------------------------------



\[ ] Reader role verified at subscription scope

\[ ] Cost Management Reader role verified



-----------------------------------------

CAPABILITY PROBES

-----------------------------------------



\[ ] Probe: subscriptions.list -> PASS

\[ ] Probe: resourcegraph.query -> PASS

\[ ] Probe: cost.query (7-day daily) -> PASS

\[ ] Probe: advisor.recommendations -> PASS

\[ ] Probe: policyinsights.summary -> PASS

\[ ] Probe: network resources (NSG, VNet, IP) -> PASS



-----------------------------------------

OUTPUT VALIDATION

-----------------------------------------



\[ ] Pre-flight JSON generated and stored in Cosmos

\[ ] preflightId returned to UI

\[ ] All probe results recorded with status and latency



-----------------------------------------

VERDICT

-----------------------------------------



\[ ] Pre-flight verdict = PASS

\[ ] "Run Scan" CTA enabled in UI



-----------------------------------------

AUDIT LOGGING

-----------------------------------------



\[ ] preflight.started event logged

\[ ] preflight.probe.executed events logged

\[ ] preflight.completed event logged



-----------------------------------------

FAILURE SCENARIO

-----------------------------------------



\[ ] Missing permission produces FAIL verdict

\[ ] UI displays remediation instructions

\[ ] Collector is blocked when FAIL



-----------------------------------------

PHASE 1 SIGN-OFF

-----------------------------------------



\[ ] One successful pre-flight execution on marco\* sandbox

\[ ] Pre-flight completes in < 5 seconds

\[ ] All mandatory probes PASS



=============================================================================

PHASE 2 -- COMMERCIAL MVP

=============================================================================



Objective:

Ensure onboarding works for external clients and enforces security boundaries.



-----------------------------------------

MULTI-TENANCY

-----------------------------------------



\[ ] subscriptionId required for all operations

\[ ] Cosmos partition key enforced (subscriptionId)

\[ ] No cross-tenant data access possible



-----------------------------------------

SECURITY VALIDATION

-----------------------------------------



\[ ] No data extraction before pre-flight PASS

\[ ] API enforces preflightId requirement for collector

\[ ] Tokens stored securely (Key Vault / managed identity)



-----------------------------------------

ROLE VALIDATION

-----------------------------------------



\[ ] Missing roles produce actionable remediation message

\[ ] Required roles displayed to client before onboarding



-----------------------------------------

CAPABILITY VALIDATION

-----------------------------------------



\[ ] All mandatory probes PASS for client subscription

\[ ] Optional probes produce WARN (not FAIL)



-----------------------------------------

PERFORMANCE

-----------------------------------------



\[ ] Pre-flight execution < 5 seconds (target)

\[ ] API response time < 2 seconds for validation calls



-----------------------------------------

AUDIT \& COMPLIANCE

-----------------------------------------



\[ ] All pre-flight events stored in audit logs

\[ ] Evidence references stored for probes

\[ ] Client can request audit trail



-----------------------------------------

FAILURE HANDLING

-----------------------------------------



\[ ] Pre-flight FAIL blocks collector execution

\[ ] Errors are categorized:

&nbsp;     - MissingPermission

&nbsp;     - AuthFailure

&nbsp;     - APIError



-----------------------------------------

PHASE 2 SIGN-OFF

-----------------------------------------



\[ ] First external client completes pre-flight successfully

\[ ] Pre-flight results are auditable and reproducible

\[ ] Collector runs only after PASS

```



---



\# ?? What you just built (important)



With these two documents + your previous spec, you now have:



\### ? Technical onboarding spec



\### ? Client-facing setup guide



\### ? Acceptance criteria



?? That's already \*\*production-grade SaaS onboarding design\*\*



---



\# ?? Suggested next doc (high value)



To keep momentum, the next best document is:



\### ?? `ACA Security \& Data Handling Policy`



Why:



\* Clients will ask about data handling immediately

\* Required for enterprise sales

\* Aligns with your EVA governance mindset



It would include:



\* Data classification

\* Retention

\* Encryption

\* Isolation model

\* Audit logs

\* Compliance alignment (ITSG-33, etc.)



---



If you want, I can generate that next -- \*\*enterprise-grade, ready for clients and security review\*\*.



