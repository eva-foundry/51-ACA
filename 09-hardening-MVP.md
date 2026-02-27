Below is the “Phase-2 hardening” continuation:



1\. \*\*Cosmos-backed\*\* `EntitlementService` + `PaymentsRepo` (PK = `subscriptionId`)

2\. Webhook handling for \*\*recurring billing lifecycle\*\* (`invoice.paid`, `customer.subscription.updated`, `customer.subscription.deleted`)

3\. \*\*Safer billing portal\*\* endpoint (derives `stripeCustomerId` from the authenticated client record instead of taking it from the browser)



This matches your multi-tenant, subscription-scoped isolation approach. 



---



\## 0) Dependencies



```bash

pip install azure-cosmos

```



---



\## 1) `services/api/app/settings.py` (add Cosmos + container names)



```python

from pydantic\_settings import BaseSettings, SettingsConfigDict

from pydantic import Field





class Settings(BaseSettings):

&nbsp;   model\_config = SettingsConfigDict(env\_file=".env", extra="ignore")



&nbsp;   # Stripe

&nbsp;   STRIPE\_SECRET\_KEY: str = Field(...)

&nbsp;   STRIPE\_WEBHOOK\_SECRET: str = Field(...)

&nbsp;   STRIPE\_PRICE\_TIER2\_ONE\_TIME: str = Field(...)

&nbsp;   STRIPE\_PRICE\_TIER2\_SUBSCRIPTION: str = Field(...)

&nbsp;   STRIPE\_PRICE\_TIER3\_ONE\_TIME: str = Field(...)

&nbsp;   PUBLIC\_APP\_URL: str = Field(...)

&nbsp;   PUBLIC\_API\_URL: str = Field(...)

&nbsp;   STRIPE\_ENABLE\_SUBSCRIPTIONS: bool = True



&nbsp;   # Cosmos

&nbsp;   COSMOS\_ENDPOINT: str = Field(..., description="https://<acct>.documents.azure.com:443/")

&nbsp;   COSMOS\_KEY: str = Field(..., description="Cosmos account key")

&nbsp;   COSMOS\_DB\_NAME: str = Field("aca", description="Database name")



&nbsp;   # Containers (PK = /subscriptionId for all tenant-scoped data)

&nbsp;   COSMOS\_CONTAINER\_ENTITLEMENTS: str = "entitlements"

&nbsp;   COSMOS\_CONTAINER\_PAYMENTS: str = "payments"

&nbsp;   COSMOS\_CONTAINER\_CLIENTS: str = "clients"



settings = Settings()

```



---



\## 2) `services/api/app/db/cosmos.py` (Cosmos client + container helper)



```python

from azure.cosmos import CosmosClient

from app.settings import settings





\_client = None





def get\_cosmos\_client() -> CosmosClient:

&nbsp;   global \_client

&nbsp;   if \_client is None:

&nbsp;       \_client = CosmosClient(settings.COSMOS\_ENDPOINT, credential=settings.COSMOS\_KEY)

&nbsp;   return \_client





def get\_container(container\_name: str):

&nbsp;   client = get\_cosmos\_client()

&nbsp;   db = client.get\_database\_client(settings.COSMOS\_DB\_NAME)

&nbsp;   return db.get\_container\_client(container\_name)

```



---



\## 3) `services/api/app/db/repos/entitlements\_repo.py`



```python

from typing import Optional, Literal, Dict, Any

from datetime import datetime, timezone

from app.db.cosmos import get\_container

from app.settings import settings



PaymentStatus = Literal\["none", "active", "past\_due", "canceled"]

Tier = Literal\[1, 2, 3]





class EntitlementsRepo:

&nbsp;   """

&nbsp;   Container: entitlements

&nbsp;   Partition key: /subscriptionId



&nbsp;   Recommended id strategy:

&nbsp;     id = f"entitlement::{subscriptionId}"

&nbsp;   """



&nbsp;   def \_\_init\_\_(self):

&nbsp;       self.container = get\_container(settings.COSMOS\_CONTAINER\_ENTITLEMENTS)



&nbsp;   async def get(self, subscription\_id: str) -> Optional\[Dict\[str, Any]]:

&nbsp;       doc\_id = f"entitlement::{subscription\_id}"

&nbsp;       try:

&nbsp;           return self.container.read\_item(item=doc\_id, partition\_key=subscription\_id)

&nbsp;       except Exception:

&nbsp;           return None



&nbsp;   async def upsert(

&nbsp;       self,

&nbsp;       \*,

&nbsp;       subscription\_id: str,

&nbsp;       tier: Tier,

&nbsp;       payment\_status: PaymentStatus,

&nbsp;       source: str,

&nbsp;       stripe\_customer\_id: Optional\[str] = None,

&nbsp;       stripe\_subscription\_id: Optional\[str] = None,

&nbsp;       expires\_utc: Optional\[str] = None,

&nbsp;   ) -> Dict\[str, Any]:

&nbsp;       now = datetime.now(timezone.utc).isoformat()

&nbsp;       doc = {

&nbsp;           "id": f"entitlement::{subscription\_id}",

&nbsp;           "subscriptionId": subscription\_id,

&nbsp;           "tier": tier,

&nbsp;           "paymentStatus": payment\_status,

&nbsp;           "source": source,  # "stripe"

&nbsp;           "stripeCustomerId": stripe\_customer\_id or "",

&nbsp;           "stripeSubscriptionId": stripe\_subscription\_id or "",

&nbsp;           "expiresUtc": expires\_utc or "",

&nbsp;           "updatedUtc": now,

&nbsp;       }

&nbsp;       return self.container.upsert\_item(doc)

```



---



\## 4) `services/api/app/db/repos/payments\_repo.py`



```python

from typing import Dict, Any, Optional

from datetime import datetime, timezone

from app.db.cosmos import get\_container

from app.settings import settings





class PaymentsRepo:

&nbsp;   """

&nbsp;   Container: payments

&nbsp;   Partition key: /subscriptionId



&nbsp;   Stores minimal payment facts for audit and entitlement derivation.

&nbsp;   Avoid storing PII; keep Stripe IDs and opaque ACA IDs only.

&nbsp;   """



&nbsp;   def \_\_init\_\_(self):

&nbsp;       self.container = get\_container(settings.COSMOS\_CONTAINER\_PAYMENTS)



&nbsp;   async def record\_checkout\_completed(

&nbsp;       self,

&nbsp;       \*,

&nbsp;       subscription\_id: str,

&nbsp;       stripe\_event\_id: str,

&nbsp;       stripe\_session\_id: str,

&nbsp;       stripe\_customer\_id: str,

&nbsp;       amount\_total: Optional\[int],

&nbsp;       currency: Optional\[str],

&nbsp;       tier: str,

&nbsp;       analysis\_id: str,

&nbsp;       mode: str,

&nbsp;   ) -> Dict\[str, Any]:

&nbsp;       now = datetime.now(timezone.utc).isoformat()

&nbsp;       doc = {

&nbsp;           "id": f"payment::{stripe\_event\_id}",

&nbsp;           "subscriptionId": subscription\_id,

&nbsp;           "stripeEventId": stripe\_event\_id,

&nbsp;           "stripeSessionId": stripe\_session\_id,

&nbsp;           "stripeCustomerId": stripe\_customer\_id,

&nbsp;           "amountTotal": amount\_total or 0,     # in smallest currency unit

&nbsp;           "currency": currency or "",

&nbsp;           "tier": tier,                          # "tier2"|"tier3"

&nbsp;           "analysisId": analysis\_id,

&nbsp;           "billingMode": mode,                   # "one\_time"|"subscription"|...

&nbsp;           "status": "completed",

&nbsp;           "createdUtc": now,

&nbsp;       }

&nbsp;       return self.container.upsert\_item(doc)

```



---



\## 5) `services/api/app/db/repos/clients\_repo.py` (minimal Stripe customer mapping)



```python

from typing import Optional, Dict, Any

from app.db.cosmos import get\_container

from app.settings import settings





class ClientsRepo:

&nbsp;   """

&nbsp;   Container: clients

&nbsp;   Partition key: /subscriptionId  (keep it tenant-scoped for simplicity)



&nbsp;   Minimal record used to map an ACA user/client -> stripeCustomerId per subscription.

&nbsp;   """



&nbsp;   def \_\_init\_\_(self):

&nbsp;       self.container = get\_container(settings.COSMOS\_CONTAINER\_CLIENTS)



&nbsp;   async def get(self, subscription\_id: str) -> Optional\[Dict\[str, Any]]:

&nbsp;       doc\_id = f"client::{subscription\_id}"

&nbsp;       try:

&nbsp;           return self.container.read\_item(item=doc\_id, partition\_key=subscription\_id)

&nbsp;       except Exception:

&nbsp;           return None



&nbsp;   async def upsert\_stripe\_customer(self, subscription\_id: str, stripe\_customer\_id: str) -> Dict\[str, Any]:

&nbsp;       existing = await self.get(subscription\_id) or {

&nbsp;           "id": f"client::{subscription\_id}",

&nbsp;           "subscriptionId": subscription\_id,

&nbsp;       }

&nbsp;       existing\["stripeCustomerId"] = stripe\_customer\_id

&nbsp;       return self.container.upsert\_item(existing)

```



---



\## 6) Update `services/api/app/services/entitlement\_service.py` (Cosmos-backed)



```python

from dataclasses import dataclass

from typing import Literal, Optional



from app.db.repos.entitlements\_repo import EntitlementsRepo



PaymentStatus = Literal\["none", "active", "past\_due", "canceled"]

Tier = Literal\[1, 2, 3]





@dataclass

class Entitlement:

&nbsp;   tier: Tier

&nbsp;   payment\_status: PaymentStatus

&nbsp;   expires\_utc: Optional\[str] = None

&nbsp;   stripe\_customer\_id: Optional\[str] = None

&nbsp;   stripe\_subscription\_id: Optional\[str] = None





class EntitlementService:

&nbsp;   def \_\_init\_\_(self, repo: Optional\[EntitlementsRepo] = None):

&nbsp;       self.repo = repo or EntitlementsRepo()



&nbsp;   async def get\_entitlement(self, subscription\_id: str) -> Entitlement:

&nbsp;       doc = await self.repo.get(subscription\_id)

&nbsp;       if not doc:

&nbsp;           return Entitlement(tier=1, payment\_status="none")

&nbsp;       return Entitlement(

&nbsp;           tier=doc.get("tier", 1),

&nbsp;           payment\_status=doc.get("paymentStatus", "none"),

&nbsp;           expires\_utc=doc.get("expiresUtc") or None,

&nbsp;           stripe\_customer\_id=doc.get("stripeCustomerId") or None,

&nbsp;           stripe\_subscription\_id=doc.get("stripeSubscriptionId") or None,

&nbsp;       )



&nbsp;   async def set\_entitlement(

&nbsp;       self,

&nbsp;       \*,

&nbsp;       subscription\_id: str,

&nbsp;       tier: Tier,

&nbsp;       payment\_status: PaymentStatus,

&nbsp;       stripe\_customer\_id: Optional\[str] = None,

&nbsp;       stripe\_subscription\_id: Optional\[str] = None,

&nbsp;       expires\_utc: Optional\[str] = None,

&nbsp;       source: str = "stripe",

&nbsp;   ):

&nbsp;       await self.repo.upsert(

&nbsp;           subscription\_id=subscription\_id,

&nbsp;           tier=tier,

&nbsp;           payment\_status=payment\_status,

&nbsp;           source=source,

&nbsp;           stripe\_customer\_id=stripe\_customer\_id,

&nbsp;           stripe\_subscription\_id=stripe\_subscription\_id,

&nbsp;           expires\_utc=expires\_utc,

&nbsp;       )



&nbsp;   async def grant\_tier2(self, subscription\_id: str, payment\_status: PaymentStatus = "active", \*\*kwargs):

&nbsp;       await self.set\_entitlement(subscription\_id=subscription\_id, tier=2, payment\_status=payment\_status, \*\*kwargs)



&nbsp;   async def grant\_tier3(self, subscription\_id: str, payment\_status: PaymentStatus = "active", \*\*kwargs):

&nbsp;       await self.set\_entitlement(subscription\_id=subscription\_id, tier=3, payment\_status=payment\_status, \*\*kwargs)

```



---



\## 7) Expand Stripe webhook handling (`services/api/app/routers/webhooks\_stripe.py`)



This version:



\* Records `checkout.session.completed` into `payments`

\* Saves `stripeCustomerId` on `clients`

\* Grants tier2/tier3

\* Triggers delivery for tier3

\* Handles subscription lifecycle updates



```python

from fastapi import APIRouter, Header, HTTPException, Request



from app.services.stripe\_service import StripeService

from app.services.entitlement\_service import EntitlementService

from app.services.delivery\_service import DeliveryService

from app.db.repos.payments\_repo import PaymentsRepo

from app.db.repos.clients\_repo import ClientsRepo



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



&nbsp;   try:

&nbsp;       event = stripe\_svc.verify\_webhook(payload, stripe\_signature)

&nbsp;   except Exception:

&nbsp;       raise HTTPException(status\_code=400, detail="Invalid webhook signature")



&nbsp;   event\_type = event.get("type", "")

&nbsp;   data\_obj = (event.get("data") or {}).get("object") or {}



&nbsp;   # 1) Checkout completed (one-time or subscription created via Checkout)

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

&nbsp;       amount\_total = session.get("amount\_total")  # int cents

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



&nbsp;       # Map subscription -> stripe customer

&nbsp;       if stripe\_customer\_id:

&nbsp;           await clients\_repo.upsert\_stripe\_customer(subscription\_id, stripe\_customer\_id)



&nbsp;       # Grant entitlements

&nbsp;       if tier == "tier2":

&nbsp;           # If subscription mode, we’ll also receive subscription events later.

&nbsp;           await entitlements.grant\_tier2(

&nbsp;               subscription\_id,

&nbsp;               payment\_status="active",

&nbsp;               stripe\_customer\_id=stripe\_customer\_id or None,

&nbsp;               stripe\_subscription\_id=session.get("subscription") or None,

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



&nbsp;   # 2) Recurring billing: invoice paid (keeps tier2 active)

&nbsp;   if event\_type == "invoice.paid":

&nbsp;       invoice = data\_obj

&nbsp;       stripe\_customer\_id = invoice.get("customer", "") or ""

&nbsp;       stripe\_subscription\_id = invoice.get("subscription", "") or ""



&nbsp;       # If you can map customer->subscriptionId, do it here.

&nbsp;       # In this scaffold, we rely on entitlements containing stripe IDs (or clients\_repo mapping per subscriptionId).

&nbsp;       # TODO: implement reverse mapping by indexing stripeCustomerId in a container.

&nbsp;       return {"received": True, "action": "invoice\_paid\_ignored\_until\_mapping"}



&nbsp;   # 3) Subscription updated: mark active/past\_due/canceled appropriately

&nbsp;   if event\_type == "customer.subscription.updated":

&nbsp;       sub = data\_obj

&nbsp;       status = sub.get("status", "")  # active, past\_due, canceled, unpaid, trialing...

&nbsp;       stripe\_customer\_id = sub.get("customer", "") or ""

&nbsp;       stripe\_subscription\_id = sub.get("id", "") or ""



&nbsp;       # TODO: implement mapping from stripe\_customer\_id to subscriptionId(s).

&nbsp;       # For now, ignore until mapping is implemented.

&nbsp;       return {"received": True, "action": f"subscription\_updated\_ignored\_until\_mapping:{status}"}



&nbsp;   # 4) Subscription deleted: revoke tier2 (or set canceled)

&nbsp;   if event\_type == "customer.subscription.deleted":

&nbsp;       sub = data\_obj

&nbsp;       status = sub.get("status", "")  # likely canceled

&nbsp;       # TODO mapping required as above.

&nbsp;       return {"received": True, "action": f"subscription\_deleted\_ignored\_until\_mapping:{status}"}



&nbsp;   return {"received": True}

```



\### Important next hardening step (mapping)



To fully support recurring billing events, add an index/mapping:



\* container: `stripe\_customer\_map`

\* docs: `{ id: "cust::<stripeCustomerId>", subscriptionId: "...", stripeCustomerId: "...", updatedUtc: "..." }`

\* PK: `/stripeCustomerId` (or `/id`)



That lets you map `invoice.paid` → subscriptionId instantly.



If you want, I’ll generate that container/repo + wire it into the webhook so it can \*\*activate/past\_due/cancel\*\* Tier 2 automatically.



---



\## 8) Safer billing portal endpoint (derive customerId from DB)



Replace the earlier `billing.py` with this version:



```python

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.dtos\_billing import BillingPortalResponse

from app.services.stripe\_service import StripeService

from app.db.repos.clients\_repo import ClientsRepo



router = APIRouter(tags=\["billing"])





def get\_stripe() -> StripeService:

&nbsp;   return StripeService()





def get\_clients() -> ClientsRepo:

&nbsp;   return ClientsRepo()





@router.get("/v1/billing/portal", response\_model=BillingPortalResponse)

async def billing\_portal(

&nbsp;   subscriptionId: str = Query(..., min\_length=1),

&nbsp;   returnPath: str = Query("/settings/billing", min\_length=1),

&nbsp;   stripe\_svc: StripeService = Depends(get\_stripe),

&nbsp;   clients: ClientsRepo = Depends(get\_clients),

):

&nbsp;   client = await clients.get(subscriptionId)

&nbsp;   if not client:

&nbsp;       raise HTTPException(status\_code=404, detail="Client record not found for subscription")



&nbsp;   stripe\_customer\_id = client.get("stripeCustomerId") or ""

&nbsp;   if not stripe\_customer\_id:

&nbsp;       raise HTTPException(status\_code=409, detail="No Stripe customer on file for this subscription")



&nbsp;   try:

&nbsp;       session = stripe\_svc.create\_billing\_portal\_session(

&nbsp;           stripe\_customer\_id=stripe\_customer\_id,

&nbsp;           return\_path=returnPath,

&nbsp;       )

&nbsp;       return BillingPortalResponse(redirectUrl=session.url)

&nbsp;   except Exception as e:

&nbsp;       raise HTTPException(status\_code=500, detail=f"Stripe billing portal init failed: {type(e).\_\_name\_\_}") from e

```



---



\## 9) `.env` additions



```env

COSMOS\_ENDPOINT=https://<acct>.documents.azure.com:443/

COSMOS\_KEY=<cosmos-key>

COSMOS\_DB\_NAME=aca

```



---



\## What to do next (two high-impact continuations)



1\. \*\*Stripe customer mapping repo + webhook activation logic\*\* (so recurring billing actually updates entitlements)

2\. \*\*APIM tier-gating\*\* patterns:



&nbsp;  \* Tier 1 findings redaction

&nbsp;  \* Tier 2 endpoints require entitlement “active”

&nbsp;  \* Tier 3 download requires entitlement + deliverable ready



Say: \*\*“do #1”\*\* or \*\*“do #2”\*\* (or both) and I’ll generate the exact files.



