// ACA frontend TypeScript DTOs -- aligned with API response schemas

// ---------------------------------------------------------------------------
// Customer surface types
// ---------------------------------------------------------------------------

export interface Finding {
  id: string;
  category: string;
  title: string;
  estimatedSavingLow: number;
  estimatedSavingHigh: number;
  effortClass: string;
  /** Tier 2+ only */
  narrative?: string;
  /** Tier 2+ only */
  riskClass?: string;
  /** Tier 3+ only */
  deliverableTemplateId?: string;
}

export interface Tier1Report {
  subscriptionId: string;
  scanId: string;
  currency: string;
  findings: Finding[];
  totalSavingLow: number;
  totalSavingHigh: number;
  generatedUtc: string;
}

export type CollectionStepStatus = "pending" | "running" | "done" | "error";

export interface CollectionStep {
  name: string;
  status: CollectionStepStatus;
  message?: string;
}

export interface CollectionStatus {
  scanId: string;
  subscriptionId: string;
  status: "queued" | "collecting" | "analyzing" | "complete" | "failed";
  progress: number; // 0-100
  steps: CollectionStep[];
  startedUtc: string;
  completedUtc?: string;
  error?: string;
}

export interface Entitlement {
  subscriptionId: string;
  tier: 1 | 2 | 3;
  validUntil: string | null;
  features: string[];
}

export interface CheckoutResponse {
  redirectUrl: string;
}

export interface BillingPortalResponse {
  portalUrl: string;
}

// ---------------------------------------------------------------------------
// Admin surface types
// ---------------------------------------------------------------------------

export interface AdminKpis {
  utc: string;
  mrrCad: number;
  activeSubscriptions: number;
  scansLast24h: number;
  analysesLast24h: number;
  deliveriesLast24h: number;
  failureRatePctLast24h: number;
}

export interface AdminCustomerRow {
  subscriptionId: string;
  stripeCustomerId: string | null;
  tier: 1 | 2 | 3;
  paymentStatus: string;
  lastActivityUtc: string | null;
  isLocked: boolean;
}

export interface AdminCustomerSearchResponse {
  items: AdminCustomerRow[];
}

export interface AdminGrantEntitlementRequest {
  subscriptionId: string;
  tier: 1 | 2 | 3;
  days: number;
  reason: string;
}

export interface AdminLockRequest {
  reason: string;
}

export interface AdminJobAccepted {
  jobId: string;
  acceptedUtc: string;
}

export interface AdminRunRecord {
  runId: string;
  subscriptionId: string;
  type: "scan" | "analysis" | "delivery";
  status: "queued" | "running" | "succeeded" | "failed";
  startedUtc: string;
  durationMs?: number;
  correlationId?: string;
  error?: string;
}

export interface AdminRunsResponse {
  items: AdminRunRecord[];
  nextPage?: string;
}
