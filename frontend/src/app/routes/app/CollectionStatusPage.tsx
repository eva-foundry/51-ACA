/**
 * CollectionStatusPage -- /app/status/:subscriptionId
 * Polls GET /v1/collect/status with exponential backoff.
 * Shows named pipeline steps + progress bar.
 * Redirects to /app/findings/:subscriptionId when complete.
 */

import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ProgressBar, Subtitle1, Body1, Badge } from "@fluentui/react-components";
import { appApi } from "../../api/appApi";
import { ErrorState } from "../../components/ErrorState";
import type { CollectionStatus, CollectionStepStatus } from "../../types/models";

const STEP_LABEL_MAP: Record<string, string> = {
  inventory:  "Resource Inventory",
  cost_data:  "Cost Data (91 days)",
  advisor:    "Azure Advisor",
  policy:     "Policy Compliance",
  analysis:   "Analysis Engine",
};

function stepIntent(s: CollectionStepStatus) {
  if (s === "done")    return "success";
  if (s === "error")   return "danger";
  if (s === "running") return "informative";
  return undefined;
}

export default function CollectionStatusPage() {
  const { subscriptionId } = useParams<{ subscriptionId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<CollectionStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const backoffRef = useRef(5000);

  const poll = async () => {
    if (!subscriptionId) return;
    try {
      const data = await appApi.getCollectionStatus(subscriptionId);
      setStatus(data);
      setError(null);

      if (data.status === "complete") {
        navigate(`/app/findings/${encodeURIComponent(subscriptionId)}`, { replace: true });
        return;
      }
      if (data.status === "failed") {
        setError(data.error ?? "Collection failed. Please try again from the Connect page.");
        return;
      }
      // Schedule next poll with cap at 30s
      backoffRef.current = Math.min(backoffRef.current * 1.4, 30_000);
      intervalRef.current = setTimeout(poll, backoffRef.current);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Polling error. Will retry...");
      intervalRef.current = setTimeout(poll, 15_000);
    }
  };

  useEffect(() => {
    poll();
    return () => { if (intervalRef.current) clearTimeout(intervalRef.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [subscriptionId]);

  return (
    <div style={{ maxWidth: 640 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 8 }}>
        Collecting data&hellip;
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 24 }}>
        ACA is pulling read-only data from your Azure subscription.
        This typically takes 2&ndash;4 minutes.
      </Body1>

      {error && <ErrorState message={error} />}

      {status && (
        <>
          <div
            role="status"
            aria-live="polite"
            aria-label={`Collection ${status.progress}% complete`}
            style={{ marginBottom: 16 }}
          >
            <ProgressBar
              value={status.progress / 100}
              shape="rounded"
              thickness="large"
            />
            <Body1 style={{ marginTop: 8, color: "#555" }}>
              {status.progress}% complete
            </Body1>
          </div>

          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {status.steps.map((step) => (
              <li
                key={step.name}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                  padding: "10px 0",
                  borderBottom: "1px solid #eee",
                }}
              >
                <Badge
                  color={stepIntent(step.status) as "success" | "danger" | "informative" | undefined}
                  size="small"
                >
                  {step.status}
                </Badge>
                <span>{STEP_LABEL_MAP[step.name] ?? step.name}</span>
                {step.message && (
                  <span style={{ fontSize: 12, color: "#888", marginLeft: "auto" }}>
                    {step.message}
                  </span>
                )}
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
