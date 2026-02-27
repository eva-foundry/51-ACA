// EVA-STORY: ACA-05-021
/**
 * AdminDashboardPage -- /admin/dashboard
 * KPI cards from GET /v1/admin/kpis.
 * Uses dl/dt/dd for accessible KPI display.
 */

import { useEffect, useState } from "react";
import { Subtitle1, Body1, Spinner } from "@fluentui/react-components";
import { adminApi } from "../../api/adminApi";
import { ErrorState } from "../../components/ErrorState";
import type { AdminKpis } from "../../types/models";

interface KpiCardProps {
  label: string;
  value: string;
  sub?: string;
}

function KpiCard({ label, value, sub }: KpiCardProps) {
  return (
    <div
      style={{
        border: "1px solid #ddd",
        borderRadius: 8,
        padding: "16px 24px",
        background: "#fff",
        minWidth: 180,
        flex: "1 1 180px",
      }}
    >
      <dl style={{ margin: 0 }}>
        <dt style={{ fontSize: 13, color: "#666", marginBottom: 6 }}>{label}</dt>
        <dd style={{ margin: 0, fontSize: 28, fontWeight: 700, color: "#0078d4" }}>
          {value}
        </dd>
        {sub && (
          <dd style={{ margin: "4px 0 0", fontSize: 12, color: "#888" }}>{sub}</dd>
        )}
      </dl>
    </div>
  );
}

export default function AdminDashboardPage() {
  const [kpis, setKpis] = useState<AdminKpis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await adminApi.kpis();
      setKpis(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load KPIs.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const fmtCad = (n: number) =>
    new Intl.NumberFormat("en-CA", {
      style: "currency",
      currency: "CAD",
      maximumFractionDigits: 0,
    }).format(n);

  return (
    <div>
      <Subtitle1 as="h1" block style={{ marginBottom: 24 }}>
        Dashboard
      </Subtitle1>

      {isLoading && <Spinner label="Loading KPIs..." />}
      {error && <ErrorState message="Failed to load KPIs" detail={error} onRetry={load} />}

      {kpis && (
        <section aria-label="Key performance indicators">
          <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
            <KpiCard
              label="MRR (CAD)"
              value={fmtCad(kpis.mrrCad)}
              sub="Monthly Recurring Revenue"
            />
            <KpiCard
              label="Active Subscriptions"
              value={String(kpis.activeSubscriptions)}
            />
            <KpiCard
              label="Scans (last 24h)"
              value={String(kpis.scansLast24h)}
            />
            <KpiCard
              label="Failure Rate (24h)"
              value={`${kpis.failureRatePctLast24h.toFixed(1)}%`}
              sub={kpis.failureRatePctLast24h > 5 ? "Above threshold" : "Within normal range"}
            />
          </div>
        </section>
      )}

      {kpis && (
        <div style={{ marginTop: 32 }}>
          <Body1 style={{ color: "#555" }}>
            Metrics updated as of server response. Refresh the page to reload.
          </Body1>
        </div>
      )}
    </div>
  );
}
