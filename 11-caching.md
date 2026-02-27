\## APIM caching (entitlements + preflight) + Cosmos schema notes



\### 1) APIM: cache \*\*entitlements\*\* lookup for 60s



You're calling `/v1/entitlements?subscriptionId=...` inside gating policies. Cache that response to avoid hammering your API.



\*\*Drop-in pattern (operation-level policy that needs Tier checks):\*\*



```xml

<policies>

&nbsp; <inbound>

&nbsp;   <base />



&nbsp;   <!-- Resolve subscriptionId -->

&nbsp;   <set-variable name="subId" value="@(

&nbsp;       context.Request.Url.Query.GetValueOrDefault("subscriptionId", "")

&nbsp;   )" />

&nbsp;   <choose>

&nbsp;     <when condition="@((string)context.Variables\["subId"] == "" \&\& context.Request.Body != null)">

&nbsp;       <set-variable name="subId" value="@((string)(context.Request.Body.As<JObject>(preserveContent: true)?\["subscriptionId"] ?? ""))" />

&nbsp;     </when>

&nbsp;   </choose>



&nbsp;   <choose>

&nbsp;     <when condition="@((string)context.Variables\["subId"] == "")">

&nbsp;       <return-response>

&nbsp;         <set-status code="400" reason="Bad Request" />

&nbsp;         <set-body>{"error":{"code":"VALIDATION\_FAILED","message":"subscriptionId is required"}} </set-body>

&nbsp;       </return-response>

&nbsp;     </when>

&nbsp;   </choose>



&nbsp;   <!-- Cache key (per subscription) -->

&nbsp;   <set-variable name="entCacheKey" value="@($"entitlements::{(string)context.Variables\["subId"]}")" />



&nbsp;   <!-- Try cache first -->

&nbsp;   <cache-lookup-value key="@((string)context.Variables\["entCacheKey"])" variable-name="entCached" />



&nbsp;   <choose>

&nbsp;     <when condition="@((string)context.Variables\["entCached"] == "")">

&nbsp;       <!-- Cache miss: call backend -->

&nbsp;       <send-request mode="new" response-variable-name="entResp" timeout="10" ignore-error="false">

&nbsp;         <set-url>@($"https://api.aca.example.com/v1/entitlements?subscriptionId={(string)context.Variables\["subId"]}")</set-url>

&nbsp;         <set-method>GET</set-method>

&nbsp;       </send-request>



&nbsp;       <set-variable name="entJsonStr" value="@(((IResponse)context.Variables\["entResp"]).Body.As<string>())" />



&nbsp;       <!-- Store in cache for 60s -->

&nbsp;       <cache-store-value key="@((string)context.Variables\["entCacheKey"])" value="@((string)context.Variables\["entJsonStr"])" duration="60" />



&nbsp;       <set-variable name="entJson" value="@(((string)context.Variables\["entJsonStr"]).As<JObject>())" />

&nbsp;     </when>

&nbsp;     <otherwise>

&nbsp;       <!-- Cache hit -->

&nbsp;       <set-variable name="entJson" value="@(((string)context.Variables\["entCached"]).As<JObject>())" />

&nbsp;     </otherwise>

&nbsp;   </choose>



&nbsp;   <!-- Use entJson for gating -->

&nbsp;   <set-variable name="canTier2" value="@((bool)((JObject)context.Variables\["entJson"])\["canViewTier2"])" />



&nbsp;   <choose>

&nbsp;     <when condition="@(!(bool)context.Variables\["canTier2"])">

&nbsp;       <return-response>

&nbsp;         <set-status code="402" reason="Payment Required" />

&nbsp;         <set-body>{"error":{"code":"TIER\_LOCKED","message":"Tier 2 access requires an active entitlement"}} </set-body>

&nbsp;       </return-response>

&nbsp;     </when>

&nbsp;   </choose>

&nbsp; </inbound>



&nbsp; <backend><base /></backend>

&nbsp; <outbound><base /></outbound>

&nbsp; <on-error><base /></on-error>

</policies>

```



\*\*Tip:\*\* For Tier3 download operations, reuse the same block but check `canGenerateTier3`.



---



\### 2) APIM: cache \*\*preflight PASS\*\* status for 5 minutes (optional)



If you have repeated "Start scan" attempts, cache the preflight verdict response (or a lightweight `GET /v1/onboarding/preflight/latest?subscriptionId=...` if you add it).



Simple caching approach:



\* cache key: `preflight.latest::{subscriptionId}`

\* duration: 300 seconds

\* invalidate naturally (short TTL)



---



\## Cosmos schema notes + indexing (Phase 2 ready)



\### General design rules (your multi-tenant boundary)



\* \*\*All tenant-scoped containers use `PK = /subscriptionId`\*\* except the Stripe customer map, which should use `/stripeCustomerId` for fast webhook lookups.

\* Use \*\*deterministic `id`\*\* patterns to avoid duplicates and simplify updates.

\* Keep documents small and "append-only" where possible (audit, payments).



---



\### A) Container: `entitlements`



\*\*Partition key:\*\* `/subscriptionId`

\*\*Document ID:\*\* `entitlement::{subscriptionId}` (single doc per subscription)



\*\*Schema (recommended):\*\*



```json

{

&nbsp; "id": "entitlement::<subscriptionId>",

&nbsp; "subscriptionId": "<subscriptionId>",

&nbsp; "tier": 1,

&nbsp; "paymentStatus": "none",

&nbsp; "source": "stripe",

&nbsp; "stripeCustomerId": "cus\_...",

&nbsp; "stripeSubscriptionId": "sub\_...",

&nbsp; "expiresUtc": "",

&nbsp; "updatedUtc": "2026-02-26T..."

}

```



\*\*Indexing suggestions\*\*



\* Default indexing OK (point reads by `id` + `PK`).

\* If you need queries by status/tier (admin dashboards), add \*\*included paths\*\* for:



&nbsp; \* `/tier/?`, `/paymentStatus/?`, `/updatedUtc/?`

\* Otherwise, keep it minimal.



---



\### B) Container: `payments`



\*\*Partition key:\*\* `/subscriptionId`

\*\*Document ID:\*\* `payment::{stripeEventId}` (idempotent per webhook event)



\*\*Schema (recommended minimal):\*\*



```json

{

&nbsp; "id": "payment::<stripeEventId>",

&nbsp; "subscriptionId": "<subscriptionId>",

&nbsp; "stripeEventId": "evt\_...",

&nbsp; "stripeSessionId": "cs\_...",

&nbsp; "stripeCustomerId": "cus\_...",

&nbsp; "amountTotal": 12900,

&nbsp; "currency": "cad",

&nbsp; "tier": "tier2",

&nbsp; "analysisId": "ana\_...",

&nbsp; "billingMode": "subscription",

&nbsp; "status": "completed",

&nbsp; "createdUtc": "2026-02-26T..."

}

```



\*\*Indexing suggestions\*\*



\* Keep default.

\* If you plan "billing history" views, index:



&nbsp; \* `/createdUtc/?`, `/tier/?`, `/status/?`



---



\### C) Container: `clients`



\*\*Partition key:\*\* `/subscriptionId`

\*\*Document ID:\*\* `client::{subscriptionId}`



\*\*Schema (minimal):\*\*



```json

{

&nbsp; "id": "client::<subscriptionId>",

&nbsp; "subscriptionId": "<subscriptionId>",

&nbsp; "tenantId": "<entraTenantIdOptional>",

&nbsp; "stripeCustomerId": "cus\_...",

&nbsp; "createdUtc": "...",

&nbsp; "updatedUtc": "..."

}

```



\*\*Indexing suggestions\*\*



\* Default (point read).

\* Avoid heavy querying here; it's a lookup table.



---



\### D) Container: `stripe\_customer\_map` (critical for webhooks)



\*\*Partition key:\*\* `/stripeCustomerId`

\*\*Document ID:\*\* `cust::{stripeCustomerId}`



\*\*Schema:\*\*



```json

{

&nbsp; "id": "cust::<stripeCustomerId>",

&nbsp; "stripeCustomerId": "cus\_...",

&nbsp; "subscriptionId": "<subscriptionId>",

&nbsp; "updatedUtc": "..."

}

```



\*\*Why separate PK?\*\*

Stripe webhook events give you \*\*customer IDs\*\*, not subscriptionIds. This lets you do an O(1) point read:



\* `read\_item(id="cust::cus\_...", pk="cus\_...")`



\*\*Indexing\*\*



\* Default is fine (point reads).



---



\## APIM cache invalidation note



When Stripe webhooks change entitlements (tier activated/canceled), APIM cache might still serve old values for up to 60 seconds. That's usually acceptable. If you want near-instant, use \*\*short TTL (15s)\*\* or add an admin-only "purge" strategy (more complexity).



---



If you want, I can also generate a \*\*Cosmos container provisioning snippet\*\* (Terraform or az cli) reflecting these PKs and names, so your infra is reproducible.



