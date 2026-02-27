import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  Title2, Text, Button, Badge, makeStyles, tokens,
  Table, TableBody, TableCell, TableCellLayout,
  TableHeader, TableHeaderCell, TableRow,
} from "@fluentui/react-components";
import { trackPageView, trackEvent } from "../telemetry/analytics";
import { formatCurrency } from "../i18n";

type Finding = {
  id: string;
  category: string;
  title: string;
  estimated_saving_low: number;
  estimated_saving_high: number;
  effort_class: "easy" | "medium" | "hard";
  risk_class: "none" | "low" | "medium" | "high";
  narrative: string;
};

const EFFORT_COLOR: Record<string, "success" | "warning" | "danger"> = {
  easy: "success",
  medium: "warning",
  hard: "danger",
};

const useStyles = makeStyles({
  root: { maxWidth: "900px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
  summary: { marginBottom: tokens.spacingVerticalL },
  upgradeBar: {
    backgroundColor: tokens.colorNeutralBackground2,
    padding: tokens.spacingVerticalM,
    borderRadius: tokens.borderRadiusMedium,
    marginBottom: tokens.spacingVerticalL,
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    flexWrap: "wrap",
    gap: tokens.spacingHorizontalM,
  },
});

export default function Findings() {
  const { t } = useTranslation();
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  const styles = useStyles();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    trackPageView(`/findings/${scanId ?? ""}`, "Findings");
    fetchFindings();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scanId]);

  async function fetchFindings() {
    if (!scanId) return;
    const res = await fetch(`/v1/findings/${scanId}`);
    if (res.ok) {
      const data = await res.json();
      setFindings(data.findings ?? []);
    }
    setLoading(false);
  }

  const totalSavingsLow = findings.reduce((s, f) => s + f.estimated_saving_low, 0);
  const totalSavingsHigh = findings.reduce((s, f) => s + f.estimated_saving_high, 0);

  return (
    <main className={styles.root}>
      <Title2 id="findings-heading">{t("findings.title")}</Title2>
      {!loading && findings.length > 0 && (
        <div className={styles.summary} aria-labelledby="savings-label">
          <Text id="savings-label" weight="semibold">{t("findings.total_savings")}: </Text>
          <Text
            aria-label={`Estimated savings: ${formatCurrency(totalSavingsLow)} to ${formatCurrency(totalSavingsHigh)} per year`}
          >
            {formatCurrency(totalSavingsLow)} -- {formatCurrency(totalSavingsHigh)}/year
          </Text>
        </div>
      )}
      {/* Upgrade prompt for free tier */}
      <div className={styles.upgradeBar} role="region" aria-label="Upgrade to see full findings">
        <Text>Full findings report requires Standard or higher tier.</Text>
        <Button
          appearance="primary"
          onClick={() => { trackEvent("checkout_started", { tier: "2" }); navigate("/checkout?tier=2"); }}
        >
          {t("actions.upgrade")}
        </Button>
      </div>
      {loading ? (
        <Text role="status" aria-live="polite">{t("a11y.loading")}</Text>
      ) : (
        <Table aria-labelledby="findings-heading">
          <TableHeader>
            <TableRow>
              <TableHeaderCell scope="col">Category</TableHeaderCell>
              <TableHeaderCell scope="col">Finding</TableHeaderCell>
              <TableHeaderCell scope="col">Est. Savings</TableHeaderCell>
              <TableHeaderCell scope="col">Effort</TableHeaderCell>
              <TableHeaderCell scope="col">Risk</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {findings.map((f) => (
              <TableRow
                key={f.id}
                onClick={() => trackEvent("finding_expanded", { category: f.category })}
              >
                <TableCell><TableCellLayout>{f.category}</TableCellLayout></TableCell>
                <TableCell><TableCellLayout>{f.title}</TableCellLayout></TableCell>
                <TableCell>
                  <TableCellLayout>
                    <span aria-label={`${formatCurrency(f.estimated_saving_low)} to ${formatCurrency(f.estimated_saving_high)} per year`}>
                      {formatCurrency(f.estimated_saving_low)} -- {formatCurrency(f.estimated_saving_high)}/yr
                    </span>
                  </TableCellLayout>
                </TableCell>
                <TableCell>
                  <TableCellLayout>
                    <Badge color={EFFORT_COLOR[f.effort_class]}>{t(`findings.effort.${f.effort_class}`)}</Badge>
                  </TableCellLayout>
                </TableCell>
                <TableCell>
                  <TableCellLayout>{t(`findings.risk.${f.risk_class}`)}</TableCellLayout>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </main>
  );
}
