from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

Tier = Literal[1, 2, 3]
PaymentStatus = Literal["none", "active", "past_due", "canceled"]
RunType = Literal["scan", "analysis", "delivery"]

class AdminKpisResponse(BaseModel):
    revenueMtd: float
    activeSubscriptions: int
    churnMtd: int
    scans24h: int
    analyses24h: int
    deliveries24h: int
    failureRate24h: float
    webhookLagSecondsP95: float

class CustomerEntitlement(BaseModel):
    subscriptionId: str
    tier: Tier
    paymentStatus: PaymentStatus
    expiresUtc: Optional[str] = None
    locked: bool = False

class CustomerSearchItem(BaseModel):
    subscriptionId: str
    tier: Tier
    paymentStatus: PaymentStatus
    locked: bool
    lastSeenUtc: Optional[str] = None

class CustomerSearchResponse(BaseModel):
    items: List[CustomerSearchItem]

class CustomerDetailResponse(BaseModel):
    entitlement: CustomerEntitlement
    stripeCustomerId: Optional[str] = None
    lastScanUtc: Optional[str] = None
    lastAnalysisUtc: Optional[str] = None
    lastDeliveryUtc: Optional[str] = None

class GrantEntitlementRequest(BaseModel):
    subscriptionId: str = Field(..., min_length=1)
    tier: Literal[2, 3]
    durationDays: int = Field(7, ge=1, le=90)
    reason: str = Field(..., min_length=3, max_length=500)

class LockSubscriptionRequest(BaseModel):
    subscriptionId: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=3, max_length=500)

class UnlockSubscriptionRequest(BaseModel):
    subscriptionId: str = Field(..., min_length=1)
    reason: str = Field(..., min_length=3, max_length=500)

class ReconcileStripeRequest(BaseModel):
    subscriptionId: Optional[str] = None

class ReconcileStripeResponse(BaseModel):
    reconciled: int
    updated: int
    warnings: List[str]

class AdminRunItem(BaseModel):
    runId: str
    subscriptionId: str
    type: RunType
    status: str
    startedUtc: str
    finishedUtc: Optional[str] = None
    durationSeconds: Optional[float] = None
    correlationId: Optional[str] = None

class AdminRunsResponse(BaseModel):
    items: List[AdminRunItem]

class AdminAuditEvent(BaseModel):
    id: str
    occurredUtc: str
    actorId: str
    actorRoles: List[str]
    action: str
    subscriptionId: Optional[str] = None
    payload: Dict[str, Any] = {}

class AdminAuditResponse(BaseModel):
    items: List[AdminAuditEvent]
