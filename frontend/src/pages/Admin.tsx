// EVA-STORY: ACA-05-021
import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Title2, Text, Spinner, makeStyles, tokens,
  Table, TableBody, TableCell, TableCellLayout,
  TableHeader, TableHeaderCell, TableRow,
} from "@fluentui/react-components";
import { trackPageView } from "../telemetry/analytics";

type AdminStats = {
  total_scans: number;
  total_clients: number;
  total_findings: number;
  total_payments: number;
  active_subscriptions: number;
};

const useStyles = makeStyles({
  root: { maxWidth: "900px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
  statGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: tokens.spacingHorizontalM,
    marginBottom: tokens.spacingVerticalXL,
  },
  statCard: {
    padding: tokens.spacingVerticalM,
    backgroundColor: tokens.colorNeutralBackground2,
    borderRadius: tokens.borderRadiusMedium,
    textAlign: "center",
  },
});

export default function Admin() {
  const { t } = useTranslation();
  const styles = useStyles();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    trackPageView("/admin", "Admin");
    fetchStats();
  }, []);

  async function fetchStats() {
    const res = await fetch("/v1/admin/stats");
    if (res.ok) setStats(await res.json());
    setLoading(false);
  }

  const metrics: { key: keyof AdminStats; label: string }[] = [
    { key: "total_scans", label: "Total Scans" },
    { key: "total_clients", label: "Clients" },
    { key: "total_findings", label: "Findings" },
    { key: "total_payments", label: "Payments" },
    { key: "active_subscriptions", label: "Active Subscriptions" },
  ];

  return (
    <main className={styles.root}>
      <Title2>{t("nav.admin")}</Title2>
      {loading && <Spinner label={t("a11y.loading")} />}
      {stats && (
        <>
          <dl className={styles.statGrid} aria-label="System statistics">
            {metrics.map(({ key, label }) => (
              <div key={key} className={styles.statCard} role="group" aria-label={label}>
                <dt><Text size={300}>{label}</Text></dt>
                <dd><Text size={600} weight="semibold">{stats[key]}</Text></dd>
              </div>
            ))}
          </dl>
          {/* Placeholder for rule status table */}
          <Table aria-label="Analysis rules status">
            <TableHeader>
              <TableRow>
                <TableHeaderCell scope="col">Rule</TableHeaderCell>
                <TableHeaderCell scope="col">Status</TableHeaderCell>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell><TableCellLayout>Rule data fetched separately from /v1/admin/stats</TableCellLayout></TableCell>
                <TableCell><TableCellLayout>--</TableCellLayout></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </>
      )}
    </main>
  );
}
