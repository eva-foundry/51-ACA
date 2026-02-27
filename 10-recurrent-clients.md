\## #1 Stripe customer mapping + webhook-driven entitlement lifecycle



\### A) Create a mapping container (recommended)



Create a Cosmos container:



\* \*\*Name:\*\* `stripe\_customer\_map`

\* \*\*Partition key:\*\* `/stripeCustomerId`



This avoids cross-partition scans when Stripe sends `customer` IDs.



Add to `settings.py`:



```python

\# settings.py

COSMOS\_CONTAINER\_STRIPE\_CUSTOMER\_MAP: str = "stripe\_customer\_map"

```



---



\### B) `services/api/app/db/repos/stripe\_customer\_map\_repo.py`



```python

from typing import Optional, Dict, Any

from datetime import datetime, timezone



from app.db.cosmos import get\_container

from app.settings import settings





class StripeCustomerMapRepo:

&nbsp;   """

&nbsp;   Container: stripe\_customer\_map

&nbsp;   Partition key: /stripeCustomerId



&nbsp;   Doc:

&nbsp;     id: "cust::<stripeCustomerId>"

&nbsp;     stripeCustomerId: "cus\_..."

&nbsp;     subscriptionId: "<aca subscription boundary id>"

&nbsp;     updatedUtc: "..."

&nbsp;   """



&nbsp;   def \_\_init\_\_(self):

&nbsp;       self.container = get\_container(settings.COSMOS\_CONTAINER\_STRIPE\_CUSTOMER\_MAP)



&nbsp;   async def upsert\_map(self, \*, stripe\_customer\_id: str, subscription\_id: str) -> Dict\[str, Any]:

&nbsp;       now = datetime.now(timezone.utc).isoformat()

&nbsp;       doc = {

&nbsp;           "id": f"cust::{stripe\_customer\_id}",

&nbsp;           "stripeCustomerId": stripe\_customer\_id,

&nbsp;           "subscriptionId": subscription\_id,

&nbsp;           "updatedUtc": now,

&nbsp;       }

&nbsp;       return self.container.upsert\_item(doc)



&nbsp;   async def get\_subscription\_id(self, stripe\_customer\_id: str) -> Optional\[str]:

&nbsp;       doc\_id = f"cust::{stripe\_customer\_id}"

&nbsp;       try:

&nbsp;           doc = self.container.read\_item(item=doc\_id, partition\_key=stripe\_customer\_id)

&nbsp;           return doc.get("subscriptionId")

&nbsp;       except Exception:

&nbsp;           return None

```



---



\### C) Update webhook to use mapping + update entitlements



Replace your `webhooks\_stripe.py` with this hardened version (keeps your prior behavior, adds recurring lifecycle):



```python

from fastapi import APIRouter, Header, HTTPException, Request



from app.services.stripe\_service import StripeService

from app.services.entitlement\_service import EntitlementService

from app.services.delivery\_service import DeliveryService

from app.db.repos.payments\_repo import PaymentsRepo

from app.db.repos.clients\_repo import ClientsRepo

from app.db.repos.stripe\_customer\_map\_repo import StripeCustomerMapRepo



router = APIRouter(tags=\["billing"])





def get\_stripe() -> StripeService:

&nbsp;   return StripeService()





@router.post("/v1/webhooks/stripe")

async def stripe\_webhook(

&nbsp;   request: Request,

&nbsp;   stripe\_signature: str = Header(default="", alias="Stripe-Signature"),

):

&nbsp;   payload = await request.body()

&nbsp;   if not stripe\_signature:

&nbsp;       raise HTTPException(status\_code=400, detail="Missing Stripe-Signature header")



&nbsp;   stripe\_svc = get\_stripe()

&nbsp;   entitlements = EntitlementService()

&nbsp;   delivery = DeliveryService()

&nbsp;   payments\_repo = PaymentsRepo()

&nbsp;   clients\_repo = ClientsRepo()

&nbsp;   cust\_map\_repo = StripeCustomerMapRepo()



&nbsp;   try:

&nbsp;       event = stripe\_svc.verify\_webhook(payload, stripe\_signature)

&nbsp;   except Exception:

&nbsp;       raise HTTPException(status\_code=400, detail="Invalid webhook signature")



&nbsp;   event\_type = event.get("type", "")

&nbsp;   data\_obj = (event.get("data") or {}).get("object") or {}



&nbsp;   # ---------------------------------------------------------------------

&nbsp;   # 1) Checkout completed (one-time or subscription created via Checkout)

&nbsp;   # ---------------------------------------------------------------------

&nbsp;   if event\_type == "checkout.session.completed":

&nbsp;       session = data\_obj

&nbsp;       metadata = session.get("metadata") or {}

&nbsp;       tier = metadata.get("aca\_tier")  # "tier2"|"tier3"

&nbsp;       subscription\_id = metadata.get("aca\_subscription\_id")

&nbsp;       analysis\_id = metadata.get("aca\_analysis\_id") or ""

&nbsp;       tier2\_mode = metadata.get("aca\_tier2\_mode") or ""



&nbsp;       if not tier or not subscription\_id:

&nbsp;           return {"received": True, "ignored": "missing\_metadata"}



&nbsp;       stripe\_session\_id = session.get("id", "")

&nbsp;       stripe\_customer\_id = session.get("customer", "") or ""

&nbsp;       stripe\_subscription\_id = session.get("subscription", "") or ""  # set for subscription mode

&nbsp;       amount\_total = session.get("amount\_total")

&nbsp;       currency = session.get("currency")



&nbsp;       # Persist payment record (minimal)

&nbsp;       await payments\_repo.record\_checkout\_completed(

&nbsp;           subscription\_id=subscription\_id,

&nbsp;           stripe\_event\_id=event.get("id", ""),

&nbsp;           stripe\_session\_id=stripe\_session\_id,

&nbsp;           stripe\_customer\_id=stripe\_customer\_id,

&nbsp;           amount\_total=amount\_total,

&nbsp;           currency=currency,

&nbsp;           tier=tier,

&nbsp;           analysis\_id=analysis\_id,

&nbsp;           mode=tier2\_mode or ("one\_time" if tier == "tier3" else ""),

&nbsp;       )



&nbsp;       # Persist customer mapping (Stripe -> ACA subscription boundary)

&nbsp;       if stripe\_customer\_id:

&nbsp;           await clients\_repo.upsert\_stripe\_customer(subscription\_id, stripe\_customer\_id)

&nbsp;           await cust\_map\_repo.upsert\_map(stripe\_customer\_id=stripe\_customer\_id, subscription\_id=subscription\_id)



&nbsp;       # Grant entitlements immediately

&nbsp;       if tier == "tier2":

&nbsp;           await entitlements.grant\_tier2(

&nbsp;               subscription\_id,

&nbsp;               payment\_status="active",

&nbsp;               stripe\_customer\_id=stripe\_customer\_id or None,

&nbsp;               stripe\_subscription\_id=stripe\_subscription\_id or None,

&nbsp;               source="stripe",

&nbsp;           )

&nbsp;           return {"received": True, "action": "tier2\_granted"}



&nbsp;       if tier == "tier3":

&nbsp;           await entitlements.grant\_tier3(

&nbsp;               subscription\_id,

&nbsp;               payment\_status="active",

&nbsp;               stripe\_customer\_id=stripe\_customer\_id or None,

&nbsp;               source="stripe",

&nbsp;           )

&nbsp;           if analysis\_id:

&nbsp;               deliverable\_id = await delivery.trigger\_delivery\_job(subscription\_id, analysis\_id)

&nbsp;               return {"received": True, "action": "tier3\_granted\_delivery\_triggered", "deliverableId": deliverable\_id}

&nbsp;           return {"received": True, "action": "tier3\_granted"}



&nbsp;       return {"received": True, "ignored": "unknown\_tier"}



&nbsp;   # ---------------------------------------------------------------------

&nbsp;   # 2) invoice.paid: keep Tier 2 active for subscription billing

&nbsp;   # ---------------------------------------------------------------------

&nbsp;   if event\_type == "invoice.paid":

&nbsp;       invoice = data\_obj

&nbsp;       stripe\_customer\_id = invoice.get("customer", "") or ""

&nbsp;       stripe\_subscription\_id = invoice.get("subscription", "") or ""

&nbsp;       billing\_reason = invoice.get("billing\_reason", "")  # subscription\_cycle, subscription\_create, etc.



&nbsp;       if not stripe\_customer\_id:

&nbsp;           return {"received": True, "ignored": "invoice\_missing\_customer"}



&nbsp;       subscription\_id = await cust\_map\_repo.get\_subscription\_id(stripe\_customer\_id)

&nbsp;       if not subscription\_id:

&nbsp;           return {"received": True, "ignored": "customer\_not\_mapped"}



&nbsp;       # Mark active

&nbsp;       await entitlements.grant\_tier2(

&nbsp;           subscription\_id,

&nbsp;           payment\_status="active",

&nbsp;           stripe\_customer\_id=stripe\_customer\_id,

&nbsp;           stripe\_subscription\_id=stripe\_subscription\_id or None,

&nbsp;           source="stripe",

&nbsp;       )

&nbsp;       return {"received": True, "action": f"tier2\_active\_invoice\_paid:{billing\_reason}"}



&nbsp;   # ---------------------------------------------------------------------

&nbsp;   # 3) customer.subscription.updated: active / past\_due / canceled transitions

&nbsp;   # ---------------------------------------------------------------------

&nbsp;   if event\_type == "customer.subscription.updated":

&nbsp;       sub = data\_obj

&nbsp;       stripe\_customer\_id = sub.get("customer", "") or ""

&nbsp;       stripe\_subscription\_id = sub.get("id", "") or ""

&nbsp;       status = sub.get("status", "")  # active, past\_due, canceled, unpaid, trialing...



&nbsp;       if not stripe\_customer\_id:

&nbsp;           return {"received": True, "ignored": "sub\_updated\_missing\_customer"}



&nbsp;       subscription\_id = await cust\_map\_repo.get\_subscription\_id(stripe\_customer\_id)

&nbsp;       if not subscription\_id:

&nbsp;           return {"received": True, "ignored": "customer\_not\_mapped"}



&nbsp;       # Normalize Stripe statuses to ACA paymentStatus

&nbsp;       if status in ("active", "trialing"):

&nbsp;           payment\_status = "active"

&nbsp;       elif status in ("past\_due", "unpaid"):

&nbsp;           payment\_status = "past\_due"

&nbsp;       elif status in ("canceled",):

&nbsp;           payment\_status = "canceled"

&nbsp;       else:

&nbsp;           payment\_status = "past\_due"



&nbsp;       await entitlements.set\_entitlement(

&nbsp;           subscription\_id=subscription\_id,

&nbsp;           tier=2,

&nbsp;           payment\_status=payment\_status,  # none|active|past\_due|canceled

&nbsp;           stripe\_customer\_id=stripe\_customer\_id,

&nbsp;           stripe\_subscription\_id=stripe\_subscription\_id,

&nbsp;           source="stripe",

&nbsp;       )

&nbsp;       return {"received": True, "action": f"tier2\_status\_updated:{status}"}



&nbsp;   # ---------------------------------------------------------------------

&nbsp;   # 4) customer.subscription.deleted: revoke Tier 2 (set canceled)

&nbsp;   # ---------------------------------------------------------------------

&nbsp;   if event\_type == "customer.subscription.deleted":

&nbsp;       sub = data\_obj

&nbsp;       stripe\_customer\_id = sub.get("customer", "") or ""

&nbsp;       stripe\_subscription\_id = sub.get("id", "") or ""



&nbsp;       if not stripe\_customer\_id:

&nbsp;           return {"received": True, "ignored": "sub\_deleted\_missing\_customer"}



&nbsp;       subscription\_id = await cust\_map\_repo.get\_subscription\_id(stripe\_customer\_id)

&nbsp;       if not subscription\_id:

&nbsp;           return {"received": True, "ignored": "customer\_not\_mapped"}



&nbsp;       await entitlements.set\_entitlement(

&nbsp;           subscription\_id=subscription\_id,

&nbsp;           tier=2,

&nbsp;           payment\_status="canceled",

&nbsp;           stripe\_customer\_id=stripe\_customer\_id,

&nbsp;           stripe\_subscription\_id=stripe\_subscription\_id,

&nbsp;           source="stripe",

&nbsp;       )

&nbsp;       return {"received": True, "action": "tier2\_canceled\_subscription\_deleted"}



&nbsp;   return {"received": True}

```



\*\*What this gives you\*\*



\* One-time payments: unlock Tier2/Tier3 immediately.

\* Subscriptions: Tier2 status stays accurate via Stripe events.

\* No cross-tenant scans: Stripe customer ID → subscriptionId lookup is O(1).



---



\## #2 APIM tier-gating policies (Tier 1/2/3) + rate limits



Below are \*\*APIM policy patterns\*\* you can paste into API Management. They assume:



\* Backend has `/v1/entitlements?subscriptionId=...`

\* Requests include `subscriptionId` (query or body)

\* You can set products per tier (Tier1, Tier2, Tier3) with different rate limits



\### A) Global: correlation id + basic rate limit



\*\*Inbound (API-level policy):\*\*



```xml

<policies>

&nbsp; <inbound>

&nbsp;   <base />



&nbsp;   <!-- Correlation ID -->

&nbsp;   <set-header name="X-Correlation-Id" exists-action="override">

&nbsp;     <value>@(context.RequestId)</value>

&nbsp;   </set-header>



&nbsp;   <!-- Basic per-subscription rate limit (soft guard) -->

&nbsp;   <rate-limit-by-key calls="60" renewal-period="60"

&nbsp;     counter-key="@(context.Request.IpAddress)" />



&nbsp; </inbound>

&nbsp; <backend><base /></backend>

&nbsp; <outbound><base /></outbound>

&nbsp; <on-error><base /></on-error>

</policies>

```



\### B) Tier gating: block Tier2 endpoints if entitlement not active



Apply this policy to Tier2-only endpoints like:



\* `GET /v1/analyses/{id}/findings?tier=2`

\* `POST /v1/analyses` with `mode=tier2`

\* `POST /v1/deliverables` (or keep Tier3 separate)



\*\*Inbound (operation-level policy):\*\*



```xml

<policies>

&nbsp; <inbound>

&nbsp;   <base />



&nbsp;   <!-- Extract subscriptionId from query OR header -->

&nbsp;   <set-variable name="subId" value="@(

&nbsp;       context.Request.Url.Query.GetValueOrDefault("subscriptionId", "")

&nbsp;   )" />



&nbsp;   <!-- If not in query, try JSON body -->

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



&nbsp;   <!-- Call ACA entitlements endpoint (internal) -->

&nbsp;   <send-request mode="new" response-variable-name="entResp" timeout="10" ignore-error="false">

&nbsp;     <set-url>@($"https://api.aca.example.com/v1/entitlements?subscriptionId={(string)context.Variables\["subId"]}")</set-url>

&nbsp;     <set-method>GET</set-method>

&nbsp;     <!-- Forward auth if needed; or use APIM managed identity to call backend -->

&nbsp;   </send-request>



&nbsp;   <set-variable name="entJson" value="@(((IResponse)context.Variables\["entResp"]).Body.As<JObject>())" />

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



\### C) Tier3 gating: deliverable download requires Tier3 + deliverable ready



Apply to:



\* `POST /v1/deliverables/{deliverableId}/download`



\*\*Inbound (operation policy):\*\*



```xml

<policies>

&nbsp; <inbound>

&nbsp;   <base />



&nbsp;   <set-variable name="subId" value="@(

&nbsp;       context.Request.Url.Query.GetValueOrDefault("subscriptionId", "")

&nbsp;   )" />



&nbsp;   <choose>

&nbsp;     <when condition="@((string)context.Variables\["subId"] == "")">

&nbsp;       <return-response>

&nbsp;         <set-status code="400" reason="Bad Request" />

&nbsp;         <set-body>{"error":{"code":"VALIDATION\_FAILED","message":"subscriptionId is required"}} </set-body>

&nbsp;       </return-response>

&nbsp;     </when>

&nbsp;   </choose>



&nbsp;   <send-request mode="new" response-variable-name="entResp" timeout="10">

&nbsp;     <set-url>@($"https://api.aca.example.com/v1/entitlements?subscriptionId={(string)context.Variables\["subId"]}")</set-url>

&nbsp;     <set-method>GET</set-method>

&nbsp;   </send-request>



&nbsp;   <set-variable name="entJson" value="@(((IResponse)context.Variables\["entResp"]).Body.As<JObject>())" />

&nbsp;   <set-variable name="canTier3" value="@((bool)((JObject)context.Variables\["entJson"])\["canGenerateTier3"])" />



&nbsp;   <choose>

&nbsp;     <when condition="@(!(bool)context.Variables\["canTier3"])">

&nbsp;       <return-response>

&nbsp;         <set-status code="402" reason="Payment Required" />

&nbsp;         <set-body>{"error":{"code":"TIER\_LOCKED","message":"Tier 3 access requires an active entitlement"}} </set-body>

&nbsp;       </return-response>

&nbsp;     </when>

&nbsp;   </choose>



&nbsp; </inbound>

&nbsp; <backend><base /></backend>

&nbsp; <outbound><base /></outbound>

&nbsp; <on-error><base /></on-error>

</policies>

```



\### D) Product-based throttles (recommended)



Create APIM \*\*Products\*\*:



\* `aca-tier1` (free): low rate limits (e.g., 10 scans/month, 30 req/min)

\* `aca-tier2`: higher limits

\* `aca-tier3`: highest limits



Then apply per-product policies like:



```xml

<rate-limit-by-key calls="120" renewal-period="60"

&nbsp; counter-key="@(context.Subscription.Id)" />

<quota-by-key calls="20000" renewal-period="2592000"

&nbsp; counter-key="@(context.Subscription.Id)" />

```



---



\## Next fast win (optional but high value)



If you want, I can generate:



\* `stripe\_customer\_map` container schema notes + indexing

\* a small `EntitlementsRepo` query to fetch by `stripeCustomerId` (if you decide not to create a mapping container)

\* APIM “cache entitlements for 60s” policy to reduce backend calls



Just say “add caching + schema notes”.



