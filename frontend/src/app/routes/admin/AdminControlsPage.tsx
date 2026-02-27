// EVA-STORY: ACA-05-025
/**
 * AdminControlsPage -- /admin/controls
 * Grant entitlement + lock subscription forms.
 * All destructive actions require confirmation modal.
 * Audited notice shown after success.
 */

import { useState, useRef, useEffect, KeyboardEvent } from "react";
import {
  Button,
  Field,
  Input,
  Select,
  Subtitle1,
  Body1,
  Divider,
} from "@fluentui/react-components";
import { adminApi } from "../../api/adminApi";
import { ErrorState } from "../../components/ErrorState";
import { useAuth } from "../../auth/useAuth";
import { ROLE_ADMIN, ROLE_SUPPORT } from "../../auth/roles";

function ConfirmModal({
  title,
  detail,
  onConfirm,
  onCancel,
}: {
  title: string;
  detail: string;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  const cancelRef = useRef<HTMLButtonElement>(null);
  useEffect(() => { cancelRef.current?.focus(); }, []);

  const handleKey = (e: KeyboardEvent) => { if (e.key === "Escape") onCancel(); };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="ctrl-dialog-title"
      onKeyDown={handleKey}
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
      <div style={{ background: "#fff", borderRadius: 8, padding: 32, maxWidth: 440, boxShadow: "0 8px 32px rgba(0,0,0,.18)" }}>
        <h2 id="ctrl-dialog-title" style={{ marginTop: 0, fontSize: 18 }}>{title}</h2>
        <Body1>{detail}</Body1>
        <div style={{ display: "flex", gap: 12, marginTop: 24, justifyContent: "flex-end" }}>
          <Button ref={cancelRef} onClick={onCancel}>Cancel</Button>
          <Button appearance="primary" onClick={onConfirm}>Confirm</Button>
        </div>
      </div>
    </div>
  );
}

function AuditedBanner({ message }: { message: string }) {
  return (
    <div
      role="alert"
      aria-live="assertive"
      style={{
        background: "#e8f5e9",
        border: "1px solid #a5d6a7",
        borderRadius: 8,
        padding: "12px 16px",
        marginTop: 12,
      }}
    >
      <Body1>{message} -- <strong>[AUDITED]</strong></Body1>
    </div>
  );
}

export default function AdminControlsPage() {
  const { hasRole } = useAuth();
  const canAct = hasRole(ROLE_ADMIN) || hasRole(ROLE_SUPPORT);

  // Grant entitlement form
  const [grantSubId, setGrantSubId] = useState("");
  const [grantTier, setGrantTier] = useState<"1" | "2" | "3">("1");
  const [grantDays, setGrantDays] = useState("30");
  const [grantReason, setGrantReason] = useState("");
  const [grantPending, setGrantPending] = useState<null | { subId: string; tier: number; days: number; reason: string }>(null);
  const [grantDone, setGrantDone] = useState<string | null>(null);
  const [grantError, setGrantError] = useState<string | null>(null);

  // Lock subscription form
  const [lockSubId, setLockSubId] = useState("");
  const [lockReason, setLockReason] = useState("");
  const [lockPending, setLockPending] = useState<null | { subId: string; reason: string }>(null);
  const [lockDone, setLockDone] = useState<string | null>(null);
  const [lockError, setLockError] = useState<string | null>(null);

  const handleGrantSubmit = () => {
    if (!grantSubId.trim() || !grantReason.trim()) {
      setGrantError("Subscription ID and reason are required.");
      return;
    }
    setGrantPending({ subId: grantSubId.trim(), tier: parseInt(grantTier), days: parseInt(grantDays), reason: grantReason.trim() });
  };

  const handleGrantConfirm = async () => {
    if (!grantPending) return;
    setGrantPending(null);
    setGrantError(null);
    try {
      await adminApi.grantEntitlement({
        subscriptionId: grantPending.subId,
        tier: grantPending.tier,
        durationDays: grantPending.days,
        reason: grantPending.reason,
      });
      setGrantDone(`Entitlement Tier ${grantPending.tier} granted to ${grantPending.subId} for ${grantPending.days} days.`);
      setGrantSubId(""); setGrantTier("1"); setGrantDays("30"); setGrantReason("");
    } catch (err) {
      setGrantError(err instanceof Error ? err.message : "Grant failed.");
    }
  };

  const handleLockSubmit = () => {
    if (!lockSubId.trim() || !lockReason.trim()) {
      setLockError("Subscription ID and reason are required.");
      return;
    }
    setLockPending({ subId: lockSubId.trim(), reason: lockReason.trim() });
  };

  const handleLockConfirm = async () => {
    if (!lockPending) return;
    setLockPending(null);
    setLockError(null);
    try {
      await adminApi.lockSubscription(lockPending.subId, { reason: lockPending.reason });
      setLockDone(`Subscription ${lockPending.subId} locked.`);
      setLockSubId(""); setLockReason("");
    } catch (err) {
      setLockError(err instanceof Error ? err.message : "Lock failed.");
    }
  };

  if (!canAct) {
    return (
      <div>
        <Subtitle1 as="h1" block>Controls</Subtitle1>
        <Body1 style={{ color: "#888", fontStyle: "italic", marginTop: 16 }}>
          ACA_Admin or ACA_Support role required to access this page.
        </Body1>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 640 }}>
      {grantPending && (
        <ConfirmModal
          title="Confirm Entitlement Grant"
          detail={`Grant Tier ${grantPending.tier} to ${grantPending.subId} for ${grantPending.days} days? Reason: "${grantPending.reason}". This action is audited.`}
          onConfirm={handleGrantConfirm}
          onCancel={() => setGrantPending(null)}
        />
      )}
      {lockPending && (
        <ConfirmModal
          title="Confirm Subscription Lock"
          detail={`Lock subscription ${lockPending.subId}? Reason: "${lockPending.reason}". This action is audited and will block all new scans.`}
          onConfirm={handleLockConfirm}
          onCancel={() => setLockPending(null)}
        />
      )}

      <Subtitle1 as="h1" block style={{ marginBottom: 24 }}>Controls</Subtitle1>

      {/* Grant Entitlement */}
      <section aria-labelledby="grant-heading" style={{ marginBottom: 40 }}>
        <h2 id="grant-heading" style={{ fontSize: 16, marginBottom: 16 }}>Grant Entitlement</h2>
        {grantError && <ErrorState message={grantError} onRetry={() => setGrantError(null)} />}
        {grantDone && <AuditedBanner message={grantDone} />}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: grantDone ? 16 : 0 }}>
          <Field label="Subscription ID" required>
            <Input value={grantSubId} onChange={(_, { value }) => setGrantSubId(value)} placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
          </Field>
          <Field label="Tier" required>
            <Select value={grantTier} onChange={(_, { value }) => setGrantTier(value as "1" | "2" | "3")}>
              <option value="1">Tier 1</option>
              <option value="2">Tier 2</option>
              <option value="3">Tier 3</option>
            </Select>
          </Field>
          <Field label="Duration (days, 1-365)" required>
            <Input type="number" min={1} max={365} value={grantDays} onChange={(_, { value }) => setGrantDays(value)} />
          </Field>
          <Field label="Reason" required>
            <Input value={grantReason} onChange={(_, { value }) => setGrantReason(value)} placeholder="e.g. Pilot partner, support resolution" />
          </Field>
          <Button appearance="primary" onClick={handleGrantSubmit} style={{ alignSelf: "flex-start" }}>
            Grant Entitlement
          </Button>
        </div>
      </section>

      <Divider />

      {/* Lock Subscription */}
      <section aria-labelledby="lock-heading" style={{ marginTop: 40 }}>
        <h2 id="lock-heading" style={{ fontSize: 16, marginBottom: 16 }}>Lock Subscription</h2>
        <Body1 style={{ color: "#888", fontSize: 13, marginBottom: 12 }}>
          Locks block all new collection runs for the subscription. Existing reports remain accessible.
        </Body1>
        {lockError && <ErrorState message={lockError} onRetry={() => setLockError(null)} />}
        {lockDone && <AuditedBanner message={lockDone} />}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: lockDone ? 16 : 0 }}>
          <Field label="Subscription ID" required>
            <Input value={lockSubId} onChange={(_, { value }) => setLockSubId(value)} placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx" />
          </Field>
          <Field label="Reason" required>
            <Input value={lockReason} onChange={(_, { value }) => setLockReason(value)} placeholder="e.g. Payment dispute, AUP violation" />
          </Field>
          <Button appearance="outline" onClick={handleLockSubmit} style={{ alignSelf: "flex-start", borderColor: "#d13438", color: "#d13438" }}>
            Lock Subscription
          </Button>
        </div>
      </section>
    </div>
  );
}
