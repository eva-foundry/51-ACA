import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Title2, Text, Button, ProgressBar, Badge, makeStyles, tokens,
} from "@fluentui/react-components";
import { trackPageView, trackEvent } from "../telemetry/analytics";

type ScanStatus = "pending" | "collecting" | "analysing" | "done" | "failed";
type ScanState = { scanId: string; status: ScanStatus; stats?: { findings_count: number }; error?: string };

const POLL_INTERVAL_MS = 3000;

const useStyles = makeStyles({
  root: { maxWidth: "600px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
});

export default function ScanStatus() {
  const { t } = useTranslation();
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const styles = useStyles();
  const [scan, setScan] = useState<ScanState | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    trackPageView(`/scan/${scanId ?? ""}`, "Scan Status");
    if (scanId && scanId !== "new") {
      pollScan(scanId);
    } else {
      startScan();
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scanId]);

  async function startScan() {
    trackEvent("scan_started");
    const res = await fetch("/v1/scans", { method: "POST" });
    if (!res.ok) return;
    const data = await res.json();
    navigate(`/scan/${data.scanId}`, { replace: true });
  }

  function pollScan(id: string) {
    intervalRef.current = setInterval(async () => {
      const res = await fetch(`/v1/scans/${id}`);
      if (!res.ok) return;
      const data: ScanState = await res.json();
      setScan(data);
      if (data.status === "done" || data.status === "failed") {
        clearInterval(intervalRef.current!);
        if (data.status === "done") trackEvent("scan_completed");
      }
    }, POLL_INTERVAL_MS);
  }

  const inProgress = !scan || (scan.status !== "done" && scan.status !== "failed");

  return (
    <main className={styles.root}>
      <Title2>Scan</Title2>
      {inProgress && (
        <>
          <Text role="status" aria-live="polite">
            {t(`scan.status.${scan?.status ?? "pending"}`)}
          </Text>
          <ProgressBar aria-label={t(`scan.status.${scan?.status ?? "pending"}`)} />
        </>
      )}
      {scan?.status === "done" && (
        <>
          <Badge color="success" aria-label="Scan complete">{t("scan.status.done")}</Badge>
          <Text block style={{ marginTop: tokens.spacingVerticalM }}>
            Findings: {scan.stats?.findings_count ?? 0}
          </Text>
          <Button
            appearance="primary"
            onClick={() => navigate(`/findings/${scan.scanId}`)}
            style={{ marginTop: tokens.spacingVerticalL }}
          >
            {t("actions.view_findings")}
          </Button>
        </>
      )}
      {scan?.status === "failed" && (
        <div role="alert" aria-live="assertive" style={{ color: tokens.colorPaletteRedForeground1 }}>
          {t("errors.scan_failed")}
          {scan.error && <Text block>{scan.error}</Text>}
        </div>
      )}
    </main>
  );
}
