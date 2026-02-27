// EVA-STORY: ACA-04-009
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Title2, Text, Button, ProgressBar,
  Badge, makeStyles, tokens,
} from "@fluentui/react-components";
import { trackPageView } from "../telemetry/analytics";

type CheckResult = { name: string; passed: boolean; message?: string };
type PreflightResult = { verdict: "go" | "warn" | "no_go"; checks: CheckResult[]; scanId?: string };

const useStyles = makeStyles({
  root: { maxWidth: "600px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
  checkList: { display: "flex", flexDirection: "column", gap: tokens.spacingVerticalS, listStyle: "none", padding: 0 },
  checkItem: { display: "flex", alignItems: "center", gap: tokens.spacingHorizontalS },
});

export default function PreFlight() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const styles = useStyles();
  const [result, setResult] = useState<PreflightResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    trackPageView("/preflight", "Pre-Flight Check");
    runPreflight();
  }, []);

  async function runPreflight() {
    try {
      const res = await fetch("/v1/auth/preflight", { method: "POST" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: PreflightResult = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("errors.preflight_failed"));
    } finally {
      setLoading(false);
    }
  }

  const verdictColor = result?.verdict === "go"
    ? "success" : result?.verdict === "warn" ? "warning" : "danger";

  return (
    <main className={styles.root}>
      <Title2>{t("preflight.title")}</Title2>
      {loading && (
        <>
          <Text role="status" aria-live="polite">{t("preflight.running")}</Text>
          <ProgressBar aria-label={t("preflight.running")} />
        </>
      )}
      {error && (
        <div role="alert" aria-live="assertive" style={{ color: tokens.colorPaletteRedForeground1 }}>
          {error}
        </div>
      )}
      {result && !loading && (
        <>
          <Badge color={verdictColor} style={{ marginBottom: tokens.spacingVerticalM }}>
            {t(`preflight.verdict.${result.verdict}`)}
          </Badge>
          <ul className={styles.checkList} aria-label={t("preflight.required_permissions")}>
            {result.checks.map((c) => (
              <li key={c.name} className={styles.checkItem}>
                <span aria-label={c.passed ? "Pass" : "Fail"} style={{ color: c.passed ? tokens.colorPaletteGreenForeground1 : tokens.colorPaletteRedForeground1 }}>
                  {c.passed ? "[PASS]" : "[FAIL]"}
                </span>
                <Text>{c.name}</Text>
                {c.message && <Text size={300}>{c.message}</Text>}
              </li>
            ))}
          </ul>
          {result.verdict !== "no_go" && (
            <Button
              appearance="primary"
              onClick={() => navigate(`/scan/${result.scanId ?? "new"}`)}
              style={{ marginTop: tokens.spacingVerticalL }}
            >
              {t("actions.start_scan")}
            </Button>
          )}
        </>
      )}
    </main>
  );
}
