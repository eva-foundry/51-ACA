Below are \*\*FastAPI Stripe backend stubs\*\* you can drop into `services/api/app/`. They implement:



\* `POST /v1/checkout/tier2`

\* `POST /v1/checkout/tier3`

\* `POST /v1/webhooks/stripe`

\* `GET /v1/billing/portal`

\* `GET /v1/entitlements?subscriptionId=...`



…and follow your planned “Stripe + webhook unlock + Tier 3 delivery trigger” flow.  



---



\## 0) Install deps



```bash

pip install stripe pydantic-settings

```



---



\## 1) `services/api/app/settings.py`



```python

from pydantic\_settings import BaseSettings, SettingsConfigDict

from pydantic import Field





class Settings(BaseSettings):

&nbsp;   model\_config = SettingsConfigDict(env\_file=".env", extra="ignore")



&nbsp;   # Stripe

&nbsp;   STRIPE\_SECRET\_KEY: str = Field(..., description="Stripe secret key (sk\_...)")

&nbsp;   STRIPE\_WEBHOOK\_SECRET: str = Field(..., description="Stripe webhook signing secret (whsec\_...)")



&nbsp;   # Stripe Price IDs (create these in Stripe)

&nbsp;   STRIPE\_PRICE\_TIER2\_ONE\_TIME: str = Field(..., description="price\_... for Tier 2 one-time")

&nbsp;   STRIPE\_PRICE\_TIER2\_SUBSCRIPTION: str = Field(..., description="price\_... for Tier 2 subscription")

&nbsp;   STRIPE\_PRICE\_TIER3\_ONE\_TIME: str = Field(..., description="price\_... for Tier 3 one-time")



&nbsp;   # URLs

&nbsp;   PUBLIC\_APP\_URL: str = Field(..., description="https://app.aca.example.com")

&nbsp;   PUBLIC\_API\_URL: str = Field(..., description="https://api.aca.example.com")



&nbsp;   # Feature flags

&nbsp;   STRIPE\_ENABLE\_SUBSCRIPTIONS: bool = True





settings = Settings()

```



---



\## 2) `services/api/app/models/dtos\_billing.py`



```python

from pydantic import BaseModel, Field

from typing import Literal, Optional





Tier = Literal\[1, 2, 3]

CheckoutTier = Literal\["tier2", "tier3"]

Tier2BillingMode = Literal\["one\_time", "subscription"]





class CheckoutRequest(BaseModel):

&nbsp;   subscriptionId: str = Field(..., min\_length=1)

&nbsp;   analysisId: str = Field(..., min\_length=1)





class CheckoutTier2Request(CheckoutRequest):

&nbsp;   mode: Tier2BillingMode = "one\_time"





class CheckoutResponse(BaseModel):

&nbsp;   checkoutSessionId: str

&nbsp;   redirectUrl: str





class BillingPortalResponse(BaseModel):

&nbsp;   redirectUrl: str





class EntitlementsResponse(BaseModel):

&nbsp;   subscriptionId: str

&nbsp;   tier: Tier

&nbsp;   paymentStatus: Literal\["none", "active", "past\_due", "canceled"]

&nbsp;   canViewTier2: bool

&nbsp;   canGenerateTier3: bool

&nbsp;   # Optional: expiresUtc, planName, etc.

&nbsp;   expiresUtc: Optional\[str] = None

```



---



\## 3) `services/api/app/services/entitlement\_service.py`



```python

from dataclasses import dataclass

from typing import Literal, Optional





PaymentStatus = Literal\["none", "active", "past\_due", "canceled"]

Tier = Literal\[1, 2, 3]





@dataclass

class Entitlement:

&nbsp;   tier: Tier

&nbsp;   payment\_status: PaymentStatus

&nbsp;   expires\_utc: Optional\[str] = None





class EntitlementService:

&nbsp;   """

&nbsp;   Stub implementation.

&nbsp;   Replace with Cosmos-backed storage:

&nbsp;     - entitlements container keyed by subscriptionId (partition key = subscriptionId)

&nbsp;     - optionally map stripeCustomerId / stripeSubscriptionId

&nbsp;   """



&nbsp;   async def get\_entitlement(self, subscription\_id: str) -> Entitlement:

&nbsp;       # TODO: load from DB

&nbsp;       return Entitlement(tier=1, payment\_status="none")



&nbsp;   async def grant\_tier2(self, subscription\_id: str, payment\_status: PaymentStatus = "active"):

&nbsp;       # TODO: upsert entitlement in DB (tier=2)

&nbsp;       return



&nbsp;   async def grant\_tier3(self, subscription\_id: str, payment\_status: PaymentStatus = "active"):

&nbsp;       # TODO: upsert entitlement in DB (tier=3)

&nbsp;       return

```



---



\## 4) `services/api/app/services/delivery\_service.py`



```python

class DeliveryService:

&nbsp;   """

&nbsp;   Stub implementation.

&nbsp;   In Phase 2, this should trigger the Container Apps 'delivery' job that generates

&nbsp;   the Tier 3 ZIP and stores it in blob storage, then updates the deliverables record.

&nbsp;   """



&nbsp;   async def trigger\_delivery\_job(self, subscription\_id: str, analysis\_id: str) -> str:

&nbsp;       # TODO: enqueue/trigger Container Apps Job (delivery) and return deliverableId

&nbsp;       # Return an opaque deliverable ID for now.

&nbsp;       return f"deliv\_{subscription\_id\[:6]}\_{analysis\_id\[:6]}"

```



---



\## 5) `services/api/app/services/stripe\_service.py`



```python

import stripe

from typing import Literal, Optional



from app.settings import settings





class StripeService:

&nbsp;   def \_\_init\_\_(self):

&nbsp;       stripe.api\_key = settings.STRIPE\_SECRET\_KEY



&nbsp;   def \_price\_for\_tier2(self, mode: Literal\["one\_time", "subscription"]) -> str:

&nbsp;       if mode == "subscription":

&nbsp;           return settings.STRIPE\_PRICE\_TIER2\_SUBSCRIPTION

&nbsp;       return settings.STRIPE\_PRICE\_TIER2\_ONE\_TIME



&nbsp;   def \_price\_for\_tier3(self) -> str:

&nbsp;       return settings.STRIPE\_PRICE\_TIER3\_ONE\_TIME



&nbsp;   def create\_checkout\_session(

&nbsp;       self,

&nbsp;       \*,

&nbsp;       tier: Literal\["tier2", "tier3"],

&nbsp;       subscription\_id: str,

&nbsp;       analysis\_id: str,

&nbsp;       success\_path: str,

&nbsp;       cancel\_path: str,

&nbsp;       tier2\_mode: Optional\[Literal\["one\_time", "subscription"]] = None,

&nbsp;       customer\_email: Optional\[str] = None,

&nbsp;   ) -> stripe.checkout.Session:

&nbsp;       """

&nbsp;       Creates a Stripe Checkout session.

&nbsp;       - Stores only opaque ACA identifiers in metadata.

&nbsp;       - Never store Azure subscription/tenant details beyond ACA subscription\_id token.

&nbsp;       """

&nbsp;       if tier == "tier2":

&nbsp;           assert tier2\_mode in ("one\_time", "subscription")

&nbsp;           price\_id = self.\_price\_for\_tier2(tier2\_mode)

&nbsp;           mode = "subscription" if tier2\_mode == "subscription" else "payment"

&nbsp;       else:

&nbsp;           price\_id = self.\_price\_for\_tier3()

&nbsp;           mode = "payment"



&nbsp;       success\_url = f"{settings.PUBLIC\_APP\_URL}{success\_path}?session\_id={{CHECKOUT\_SESSION\_ID}}"

&nbsp;       cancel\_url = f"{settings.PUBLIC\_APP\_URL}{cancel\_path}"



&nbsp;       params = {

&nbsp;           "mode": mode,

&nbsp;           "line\_items": \[{"price": price\_id, "quantity": 1}],

&nbsp;           "success\_url": success\_url,

&nbsp;           "cancel\_url": cancel\_url,

&nbsp;           "metadata": {

&nbsp;               "aca\_tier": tier,

&nbsp;               "aca\_subscription\_id": subscription\_id,

&nbsp;               "aca\_analysis\_id": analysis\_id,

&nbsp;               "aca\_tier2\_mode": tier2\_mode or "",

&nbsp;           },

&nbsp;       }



&nbsp;       # Optional: prefill email (don’t store it yourself if you can avoid it)

&nbsp;       if customer\_email:

&nbsp;           params\["customer\_email"] = customer\_email



&nbsp;       return stripe.checkout.Session.create(\*\*params)



&nbsp;   def create\_billing\_portal\_session(self, \*, stripe\_customer\_id: str, return\_path: str) -> stripe.billing\_portal.Session:

&nbsp;       return\_url = f"{settings.PUBLIC\_APP\_URL}{return\_path}"

&nbsp;       return stripe.billing\_portal.Session.create(customer=stripe\_customer\_id, return\_url=return\_url)



&nbsp;   def verify\_webhook(self, payload: bytes, sig\_header: str) -> stripe.Event:

&nbsp;       return stripe.Webhook.construct\_event(payload, sig\_header, settings.STRIPE\_WEBHOOK\_SECRET)

```



---



\## 6) `services/api/app/routers/checkout.py`



```python

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.dtos\_billing import CheckoutTier2Request, CheckoutRequest, CheckoutResponse

from app.services.stripe\_service import StripeService

from app.services.entitlement\_service import EntitlementService



router = APIRouter(tags=\["billing"])





def get\_stripe() -> StripeService:

&nbsp;   return StripeService()





def get\_entitlements() -> EntitlementService:

&nbsp;   return EntitlementService()





@router.post("/v1/checkout/tier2", response\_model=CheckoutResponse)

async def checkout\_tier2(

&nbsp;   req: CheckoutTier2Request,

&nbsp;   stripe\_svc: StripeService = Depends(get\_stripe),

&nbsp;   entitlements: EntitlementService = Depends(get\_entitlements),

):

&nbsp;   # Gate: you can optionally require analysis exists, etc.

&nbsp;   # Also consider: if already tier2+, return early.

&nbsp;   ent = await entitlements.get\_entitlement(req.subscriptionId)

&nbsp;   if ent.tier >= 2 and ent.payment\_status == "active":

&nbsp;       raise HTTPException(status\_code=status.HTTP\_409\_CONFLICT, detail="Tier 2 already active for this subscription")



&nbsp;   try:

&nbsp;       session = stripe\_svc.create\_checkout\_session(

&nbsp;           tier="tier2",

&nbsp;           tier2\_mode=req.mode,

&nbsp;           subscription\_id=req.subscriptionId,

&nbsp;           analysis\_id=req.analysisId,

&nbsp;           success\_path="/billing/success",

&nbsp;           cancel\_path="/billing/canceled",

&nbsp;       )

&nbsp;       return CheckoutResponse(checkoutSessionId=session.id, redirectUrl=session.url)

&nbsp;   except Exception as e:

&nbsp;       raise HTTPException(status\_code=500, detail=f"Stripe checkout init failed: {type(e).\_\_name\_\_}") from e





@router.post("/v1/checkout/tier3", response\_model=CheckoutResponse)

async def checkout\_tier3(

&nbsp;   req: CheckoutRequest,

&nbsp;   stripe\_svc: StripeService = Depends(get\_stripe),

):

&nbsp;   try:

&nbsp;       session = stripe\_svc.create\_checkout\_session(

&nbsp;           tier="tier3",

&nbsp;           subscription\_id=req.subscriptionId,

&nbsp;           analysis\_id=req.analysisId,

&nbsp;           success\_path="/billing/success",

&nbsp;           cancel\_path="/billing/canceled",

&nbsp;       )

&nbsp;       return CheckoutResponse(checkoutSessionId=session.id, redirectUrl=session.url)

&nbsp;   except Exception as e:

&nbsp;       raise HTTPException(status\_code=500, detail=f"Stripe checkout init failed: {type(e).\_\_name\_\_}") from e

```



---



\## 7) `services/api/app/routers/webhooks\_stripe.py`



```python

from fastapi import APIRouter, Header, HTTPException, Request

from app.services.stripe\_service import StripeService

from app.services.entitlement\_service import EntitlementService

from app.services.delivery\_service import DeliveryService



router = APIRouter(tags=\["billing"])





def get\_stripe() -> StripeService:

&nbsp;   return StripeService()





def get\_entitlements() -> EntitlementService:

&nbsp;   return EntitlementService()





def get\_delivery() -> DeliveryService:

&nbsp;   return DeliveryService()





@router.post("/v1/webhooks/stripe")

async def stripe\_webhook(

&nbsp;   request: Request,

&nbsp;   stripe\_signature: str = Header(default="", alias="Stripe-Signature"),

):

&nbsp;   payload = await request.body()

&nbsp;   if not stripe\_signature:

&nbsp;       raise HTTPException(status\_code=400, detail="Missing Stripe-Signature header")



&nbsp;   stripe\_svc = get\_stripe()

&nbsp;   entitlements = get\_entitlements()

&nbsp;   delivery = get\_delivery()



&nbsp;   try:

&nbsp;       event = stripe\_svc.verify\_webhook(payload, stripe\_signature)

&nbsp;   except Exception:

&nbsp;       raise HTTPException(status\_code=400, detail="Invalid webhook signature")



&nbsp;   # Minimal handling: only act on successful checkout completion.

&nbsp;   # You can add invoice.paid, customer.subscription.updated, etc. later.

&nbsp;   if event\["type"] == "checkout.session.completed":

&nbsp;       session = event\["data"]\["object"]



&nbsp;       metadata = session.get("metadata") or {}

&nbsp;       tier = metadata.get("aca\_tier")

&nbsp;       subscription\_id = metadata.get("aca\_subscription\_id")

&nbsp;       analysis\_id = metadata.get("aca\_analysis\_id")



&nbsp;       if not tier or not subscription\_id:

&nbsp;           # Ignore unknown payloads

&nbsp;           return {"received": True, "ignored": "missing\_metadata"}



&nbsp;       # Grant entitlements

&nbsp;       if tier == "tier2":

&nbsp;           await entitlements.grant\_tier2(subscription\_id, payment\_status="active")

&nbsp;           return {"received": True, "action": "tier2\_granted"}



&nbsp;       if tier == "tier3":

&nbsp;           # Grant Tier 3 + trigger delivery generation job

&nbsp;           await entitlements.grant\_tier3(subscription\_id, payment\_status="active")

&nbsp;           if analysis\_id:

&nbsp;               deliverable\_id = await delivery.trigger\_delivery\_job(subscription\_id, analysis\_id)

&nbsp;               return {"received": True, "action": "tier3\_granted\_delivery\_triggered", "deliverableId": deliverable\_id}

&nbsp;           return {"received": True, "action": "tier3\_granted"}



&nbsp;   return {"received": True}

```



---



\## 8) `services/api/app/routers/billing.py`



```python

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.dtos\_billing import BillingPortalResponse

from app.services.stripe\_service import StripeService



router = APIRouter(tags=\["billing"])





def get\_stripe() -> StripeService:

&nbsp;   return StripeService()





@router.get("/v1/billing/portal", response\_model=BillingPortalResponse)

async def billing\_portal(

&nbsp;   # In real implementation, derive stripeCustomerId from authenticated client record.

&nbsp;   stripeCustomerId: str = Query(..., min\_length=1),

&nbsp;   returnPath: str = Query("/settings/billing", min\_length=1),

&nbsp;   stripe\_svc: StripeService = Depends(get\_stripe),

):

&nbsp;   try:

&nbsp;       session = stripe\_svc.create\_billing\_portal\_session(stripe\_customer\_id=stripeCustomerId, return\_path=returnPath)

&nbsp;       return BillingPortalResponse(redirectUrl=session.url)

&nbsp;   except Exception as e:

&nbsp;       raise HTTPException(status\_code=500, detail=f"Stripe billing portal init failed: {type(e).\_\_name\_\_}") from e

```



> Note: for security, you’ll typically \*\*not\*\* accept `stripeCustomerId` from the client. You’ll look it up from your `clients` record after Entra auth.



---



\## 9) `services/api/app/routers/entitlements.py`



```python

from fastapi import APIRouter, Depends, Query

from app.models.dtos\_billing import EntitlementsResponse

from app.services.entitlement\_service import EntitlementService



router = APIRouter(tags=\["entitlements"])





def get\_entitlements() -> EntitlementService:

&nbsp;   return EntitlementService()





@router.get("/v1/entitlements", response\_model=EntitlementsResponse)

async def get\_entitlements(

&nbsp;   subscriptionId: str = Query(..., min\_length=1),

&nbsp;   entitlements: EntitlementService = Depends(get\_entitlements),

):

&nbsp;   ent = await entitlements.get\_entitlement(subscriptionId)

&nbsp;   return EntitlementsResponse(

&nbsp;       subscriptionId=subscriptionId,

&nbsp;       tier=ent.tier,

&nbsp;       paymentStatus=ent.payment\_status,

&nbsp;       canViewTier2=(ent.tier >= 2 and ent.payment\_status == "active"),

&nbsp;       canGenerateTier3=(ent.tier >= 3 and ent.payment\_status == "active"),

&nbsp;       expiresUtc=ent.expires\_utc,

&nbsp;   )

```



---



\## 10) Wire routers in `services/api/app/main.py`



```python

from fastapi import FastAPI



from app.routers import checkout, webhooks\_stripe, billing, entitlements



app = FastAPI(title="ACA API", version="0.1")



app.include\_router(checkout.router)

app.include\_router(webhooks\_stripe.router)

app.include\_router(billing.router)

app.include\_router(entitlements.router)

```



---



\## 11) `.env` example (DO NOT COMMIT)



```env

STRIPE\_SECRET\_KEY=sk\_live\_...

STRIPE\_WEBHOOK\_SECRET=whsec\_...



STRIPE\_PRICE\_TIER2\_ONE\_TIME=price\_...

STRIPE\_PRICE\_TIER2\_SUBSCRIPTION=price\_...

STRIPE\_PRICE\_TIER3\_ONE\_TIME=price\_...



PUBLIC\_APP\_URL=https://app.aca.example.com

PUBLIC\_API\_URL=https://api.aca.example.com

STRIPE\_ENABLE\_SUBSCRIPTIONS=true

```



---



\## What you’ll want next (still “stubs”, but critical)



If you say “continue”, I’ll generate:



1\. A \*\*Cosmos-backed\*\* `EntitlementService` (partition key = `subscriptionId`) and a `PaymentsRepo`

2\. Webhook handling for recurring billing:



&nbsp;  \* `invoice.paid`

&nbsp;  \* `customer.subscription.updated`

&nbsp;  \* `customer.subscription.deleted`

3\. A safer billing portal endpoint that derives `stripeCustomerId` from `/v1/me` (Entra-authenticated user) rather than taking it as input



(Those harden this toward Phase 2 commercial MVP.) 



