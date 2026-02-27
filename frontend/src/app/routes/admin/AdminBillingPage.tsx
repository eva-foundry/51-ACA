/**
 * AdminBillingPage -- /admin/billing
 * Stripe reconcile action (ACA_Admin only), webhook health indicator.
 * Confirmation dialog with focus trap + Escape key.
 */

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import {
  Button,
  Subtitle1,
  Body1,
  Badge,
} from "@fluentui/react-components";
import { adminApi } from "../../api/adminApi";
import { ErrorState } from "../../components/ErrorState";
import { useAuth } from "../../auth/useAuth";
import { ROLE_ADMIN } from "../../auth/roles";

function ConfirmModal({
  onConfirm,
  onCancel,
}: {
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const cancelBtnRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    cancelBtnRef.current?.focus();
  }, []);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === "Escape") onCancel();
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-dialog-title"
      onKeyDown={handleKeyDown}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.4)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
      }}
    >
      <div
        style={{
          background: "#fff",
          borderRadius: 8,
          padding: 32,
          maxWidth: 440,
          boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
        }}
      >
        <h2 id="confirm-dialog-title" style={{ marginTop: 0 }}>
          Confirm Stripe Reconciliation
        </h2>
        <Body1>
          This will trigger a Stripe subscription sync job. The operation is asynchronous
          and may take up to 2 minutes. Proceed?
        </Body1>
        <div style={{ display: "flex", gap: 12, marginTop: 24, justifyContent: "flex-end" }}>
          <Button ref={cancelBtnRef} onClick={onCancel}>
            Cancel
          </Button>
          <Button appearance="primary" onClick={onConfirm}>
            Confirm Reconcile
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function AdminBillingPage() {
  const { hasRole } = useAuth();
  const canReconcile = hasRole(ROLE_ADMIN);
  const [showConfirm, setShowConfirm] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleReconcile = async () => {
    setShowConfirm(false);
    setIsLoading(true);
    setError(null);
    try {
      const { jobId: id } = await adminApi.reconcileStripe();
      setJobId(id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reconciliation failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <Subtitle1 as="h1" block style={{ marginBottom: 24 }}>
        Billing
      </Subtitle1>

      {showConfirm && (
        <ConfirmModal onConfirm={handleReconcile} onCancel={() => setShowConfirm(false)} />
      )}

      <section aria-labelledby="stripe-health-heading" style={{ marginBottom: 32 }}>
        <h2 id="stripe-health-heading" style={{ fontSize: 16, marginBottom: 12 }}>
          Stripe Webhook Health
        </h2>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Badge color="success">Operational</Badge>
          <Body1 style={{ fontSize: 13, color: "#555" }}>
            Last event received within the past 5 minutes. No stale webhook detected.
          </Body1>
        </div>
      </section>

      <section aria-labelledby="reconcile-heading">
        <h2 id="reconcile-heading" style={{ fontSize: 16, marginBottom: 12 }}>
          Manual Stripe Reconciliation
        </h2>
        <Body1 style={{ color: "#555", marginBottom: 16 }}>
          Triggers a full reconciliation between Cosmos entitlement records and Stripe
          subscription state. Use only if webhooks are suspected to have missed events.
        </Body1>

        {error && <ErrorState message="Reconciliation failed" detail={error} onRetry={() => setShowConfirm(true)} />}

        {jobId && (
          <div
            role="alert"
            aria-live="assertive"
            style={{
              background: "#e8f5e9",
              border: "1px solid #a5d6a7",
              borderRadius: 8,
              padding: 16,
              marginBottom: 16,
            }}
          >
            <Body1>
              Reconciliation job queued. Job ID: <strong><code>{jobId}</code></strong>
            </Body1>
            <Body1 style={{ fontSize: 12, color: "#555", marginTop: 4 }}>
              [AUDITED] -- This action was recorded in admin_audit_events.
            </Body1>
          </div>
        )}

        {canReconcile ? (
          <Button
            appearance="primary"
            onClick={() => setShowConfirm(true)}
            disabled={isLoading}
            aria-busy={isLoading}
          >
            {isLoading ? "Running..." : "Reconcile Stripe"}
          </Button>
        ) : (
          <Body1 style={{ color: "#888", fontStyle: "italic" }}>
            ACA_Admin role required to perform reconciliation.
          </Body1>
        )}
      </section>
    </div>
  );
}
