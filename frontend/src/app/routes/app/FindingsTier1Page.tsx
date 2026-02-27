// EVA-STORY: ACA-05-019
/**
 * FindingsTier1Page -- /app/findings/:subscriptionId
 * Renders free Tier 1 report from GET /v1/reports/tier1.
 * Shows MoneyRangeBar + EffortBadge per finding.
 * Blurred upgrade CTA for Tier 2+ details.
 */

import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  Subtitle1,
  Body1,
  Table,
  TableHeader,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  Badge,
} from "@fluentui/react-components";
import { appApi } from "../../api/appApi";
import { MoneyRangeBar } from "../../components/MoneyRangeBar";
import { EffortBadge } from "../../components/EffortBadge";
import { Loading } from "../../components/Loading";
import { ErrorState } from "../../components/ErrorState";
import type { Tier1Report } from "../../types/models";

export default function FindingsTier1Page() {
  const { subscriptionId } = useParams<{ subscriptionId: string }>();
  const [report, setReport] = useState<Tier1Report | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadReport = async () => {
    if (!subscriptionId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await appApi.getTier1Report(subscriptionId);
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load report.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadReport(); }, [subscriptionId]);

  if (isLoading) return <Loading label="Loading your cost report..." />;
  if (error) return <ErrorState message="Could not load report" detail={error} onRetry={loadReport} />;
  if (!report) return null;

  const fmtCad = (n: number) =>
    new Intl.NumberFormat("en-CA", {
      style: "currency",
      currency: report.currency,
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <div style={{ maxWidth: 1100 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 4 }}>
        Free Scan Summary
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 8 }}>
        Subscription: <code>{subscriptionId}</code>
      </Body1>

      <div
        role="region"
        aria-label="Total estimated saving range"
        style={{
          background: "#f0f7ff",
          border: "1px solid #b3d4f5",
          borderRadius: 8,
          padding: "16px 24px",
          marginBottom: 24,
        }}
      >
        <Body1>
          <strong>Total estimated annual saving: </strong>
          <span style={{ fontSize: 20, fontWeight: 700, color: "#0078d4" }}>
            {fmtCad(report.totalSavingLow)} &ndash; {fmtCad(report.totalSavingHigh)}
          </span>
        </Body1>
        <Body1 style={{ fontSize: 12, color: "#555", marginTop: 4 }}>
          {report.findings.length} opportunities identified. Upgrade for full details.
        </Body1>
      </div>

      <Table aria-label="Cost findings">
        <TableHeader>
          <TableRow>
            <TableHeaderCell scope="col">Category</TableHeaderCell>
            <TableHeaderCell scope="col">Opportunity</TableHeaderCell>
            <TableHeaderCell scope="col">Estimated Saving (CAD/yr)</TableHeaderCell>
            <TableHeaderCell scope="col">Effort</TableHeaderCell>
          </TableRow>
        </TableHeader>
        <TableBody>
          {report.findings.map((f) => (
            <TableRow key={f.id}>
              <TableCell>
                <Badge size="small" appearance="outline">{f.category}</Badge>
              </TableCell>
              <TableCell>{f.title}</TableCell>
              <TableCell>
                <MoneyRangeBar
                  low={f.estimatedSavingLow}
                  high={f.estimatedSavingHigh}
                  currency={report.currency}
                />
              </TableCell>
              <TableCell>
                <EffortBadge effort={f.effortClass} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <div
        style={{
          marginTop: 32,
          padding: 24,
          background: "#fff8e1",
          border: "1px solid #ffe082",
          borderRadius: 8,
        }}
      >
        <Subtitle1 block style={{ marginBottom: 8 }}>
          Unlock Full Advisory Report
        </Subtitle1>
        <Body1 style={{ color: "#555", marginBottom: 16 }}>
          Get full narrative, risk ratings, evidence, and ready-to-run IaC implementation
          packages with Tier 2 or Tier 3.
        </Body1>
        <Link
          to={`/app/upgrade/${encodeURIComponent(subscriptionId!)}`}
          style={{
            background: "#0078d4",
            color: "#fff",
            padding: "10px 24px",
            borderRadius: 4,
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          View Upgrade Options
        </Link>
      </div>
    </div>
  );
}
