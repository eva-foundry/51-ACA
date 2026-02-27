import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Title2, Text, Button, Badge, Spinner, makeStyles, tokens } from "@fluentui/react-components";
import { trackPageView, trackEvent } from "../telemetry/analytics";

type Deliverable = {
  deliverableId: string;
  status: "pending" | "generating" | "ready" | "expired";
  download?: { sasUrl: string; expiresUtc: string };
  artifact?: { sha256: string; sizeBytes: number };
};

const useStyles = makeStyles({
  root: { maxWidth: "600px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
  detail: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalS },
});

export default function Download() {
  const { t } = useTranslation();
  const { deliverableId } = useParams<{ deliverableId: string }>();
  const styles = useStyles();
  const [item, setItem] = useState<Deliverable | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    trackPageView(`/download/${deliverableId ?? ""}`, "Download");
    fetchDeliverable();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [deliverableId]);

  async function fetchDeliverable() {
    if (!deliverableId) return;
    const res = await fetch(`/v1/deliverables/${deliverableId}`);
    if (res.ok) setItem(await res.json());
    setLoading(false);
  }

  function handleDownload() {
    if (!item?.download?.sasUrl) return;
    trackEvent("download_initiated");
    window.open(item.download.sasUrl, "_blank", "noopener,noreferrer");
  }

  return (
    <main className={styles.root}>
      <Title2>{t("actions.download")}</Title2>
      {loading && <Spinner label={t("a11y.loading")} />}
      {!loading && !item && <Text role="alert">{t("errors.generic")}</Text>}
      {item && (
        <div className={styles.detail}>
          <Badge color={item.status === "ready" ? "success" : item.status === "expired" ? "danger" : "informative"}>
            {item.status}
          </Badge>
          {item.artifact && (
            <>
              <Text>Size: {Math.round(item.artifact.sizeBytes / 1024)} KB</Text>
              <Text>SHA-256: <code>{item.artifact.sha256}</code></Text>
            </>
          )}
          {item.download?.expiresUtc && (
            <Text>
              Expires: {new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(item.download.expiresUtc))}
            </Text>
          )}
          <Button
            appearance="primary"
            onClick={handleDownload}
            disabled={item.status !== "ready"}
            aria-label={item.status !== "ready" ? `Download unavailable -- status: ${item.status}` : "Download deliverable ZIP"}
          >
            {t("actions.download")}
          </Button>
        </div>
      )}
    </main>
  );
}
