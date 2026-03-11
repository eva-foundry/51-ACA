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
import { useTranslation } from "react-i18next";

export default function FindingsTier1Page() {
  const { t, i18n } = useTranslation();
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
      setError(err instanceof Error ? err.message : t("pages.report.load_failed"));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { loadReport(); }, [subscriptionId]);

  if (isLoading) return <Loading label={t("pages.report.loading")} />;
  if (error) return <ErrorState message={t("pages.report.could_not_load")} detail={error} onRetry={loadReport} />;
  if (!report) return null;

  const fmtCad = (n: number) =>
    new Intl.NumberFormat(i18n.language === "fr" ? "fr-CA" : "en-CA", {
      style: "currency",
      currency: report.currency,
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <div style={{ maxWidth: 1100 }}>
      <Subtitle1 as="h1" block style={{ marginBottom: 4 }}>
        {t("pages.report.title")}
      </Subtitle1>
      <Body1 style={{ color: "#555", marginBottom: 8 }}>
        {t("pages.report.subscription")}: <code>{subscriptionId}</code>
      </Body1>

      <div
        role="region"
        aria-label={t("pages.report.savings_region_label")}
        style={{
          background: "#f0f7ff",
          border: "1px solid #b3d4f5",
          borderRadius: 8,
          padding: "16px 24px",
          marginBottom: 24,
        }}
      >
        <Body1>
          <strong>{t("findings.total_savings")}: </strong>
          <span style={{ fontSize: 20, fontWeight: 700, color: "#0078d4" }}>
            {fmtCad(report.totalSavingLow)} &ndash; {fmtCad(report.totalSavingHigh)}
          </span>
        </Body1>
        <Body1 style={{ fontSize: 12, color: "#555", marginTop: 4 }}>
          {t("pages.report.opportunities", { count: report.findings.length })}
        </Body1>
      </div>

      <Table aria-label={t("pages.report.table_label")}>
        <TableHeader>
          <TableRow>
            <TableHeaderCell scope="col">{t("pages.report.table.category")}</TableHeaderCell>
            <TableHeaderCell scope="col">{t("pages.report.table.opportunity")}</TableHeaderCell>
            <TableHeaderCell scope="col">{t("pages.report.table.saving")}</TableHeaderCell>
            <TableHeaderCell scope="col">{t("pages.report.table.effort")}</TableHeaderCell>
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
          {t("pages.report.unlock_title")}
        </Subtitle1>
        <Body1 style={{ color: "#555", marginBottom: 16 }}>
          {t("pages.report.unlock_body")}
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
          {t("pages.report.view_upgrade")}
        </Link>
      </div>
    </div>
  );
}
