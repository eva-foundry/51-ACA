// EVA-STORY: ACA-05-018
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
import { useTranslation } from "react-i18next";

const STEP_LABEL_KEYS: Record<string, string> = {
  inventory: "pages.status.steps.inventory",
  cost_data: "pages.status.steps.cost_data",
  advisor: "pages.status.steps.advisor",
  policy: "pages.status.steps.policy",
  analysis: "pages.status.steps.analysis",
};

function stepIntent(s: CollectionStepStatus) {
  if (s === "done")    return "success";
  if (s === "error")   return "danger";
  if (s === "running") return "informative";
  return undefined;
}

export default function CollectionStatusPage() {
  const { t } = useTranslation();
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
        setError(data.error ?? t("errors.scan_failed"));
        return;
      }
      // Schedule next poll with cap at 30s
      backoffRef.current = Math.min(backoffRef.current * 1.4, 30_000);
      intervalRef.current = setTimeout(poll, backoffRef.current);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("pages.status.poll_retry"));
      intervalRef.current = setTimeout(poll, 15_000);
    }
  };

  useEffect(() => {
    poll();
    return () => { if (intervalRef.current) clearTimeout(intervalRef.current); };
  }, [subscriptionId]);

  return (
    <div style={{ maxWidth: 640 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 8 }}>
        {t("pages.status.title")}
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 24 }}>
        {t("pages.status.subtitle")}
      </Body1>

      {error && <ErrorState message={error} />}

      {status && (
        <>
          <div
            role="status"
            aria-live="polite"
            aria-label={t("pages.status.progress_label", { progress: status.progress })}
            style={{ marginBottom: 16 }}
          >
            <ProgressBar
              value={status.progress / 100}
              shape="rounded"
              thickness="large"
            />
            <Body1 style={{ marginTop: 8, color: "#555" }}>
              {t("pages.status.progress_text", { progress: status.progress })}
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
                <span>{t(STEP_LABEL_KEYS[step.name] ?? "pages.status.steps.unknown", { name: step.name })}</span>
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
