// EVA-STORY: ACA-05-024
/**
 * AdminRunsPage -- /admin/runs
 * Filterable run history from GET /v1/admin/runs.
 * Type + subscriptionId filters.
 */

import { useState, FormEvent, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import {
  Button,
  Input,
  Select,
  Subtitle1,
  Body1,
  Table,
  TableHeader,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  Badge,
  Spinner,
  Field,
} from "@fluentui/react-components";
import { adminApi } from "../../api/adminApi";
import { ErrorState } from "../../components/ErrorState";
import type { AdminRunRecord } from "../../types/models";

const RUN_TYPES = ["", "scan", "analysis", "delivery"] as const;

function statusColor(s: string) {
  if (s === "succeeded") return "success" as const;
  if (s === "failed")    return "danger" as const;
  if (s === "running")   return "informative" as const;
  return undefined;
}

export default function AdminRunsPage() {
  const [searchParams] = useSearchParams();
  const [type, setType] = useState<string>(searchParams.get("type") ?? "");
  const [subId, setSubId] = useState<string>(searchParams.get("subscriptionId") ?? "");
  const [runs, setRuns] = useState<AdminRunRecord[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { items } = await adminApi.getRuns({
        type: type || undefined,
        subscriptionId: subId || undefined,
      });
      setRuns(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load runs.");
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-load if deep-linked with subscriptionId
  useEffect(() => {
    if (searchParams.get("subscriptionId")) load();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleFilter = (e: FormEvent) => {
    e.preventDefault();
    load();
  };

  return (
    <div>
      <Subtitle1 as="h1" block style={{ marginBottom: 24 }}>
        Run History
      </Subtitle1>

      <form
        onSubmit={handleFilter}
        style={{ display: "flex", gap: 12, alignItems: "flex-end", marginBottom: 24, flexWrap: "wrap" }}
      >
        <Field label="Run Type">
          <Select
            value={type}
            onChange={(_, { value }) => setType(value)}
            style={{ minWidth: 160 }}
          >
            <option value="">All types</option>
            {RUN_TYPES.filter(Boolean).map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </Select>
        </Field>
        <Field label="Subscription ID">
          <Input
            value={subId}
            onChange={(_, { value }) => setSubId(value)}
            placeholder="Filter by subscription..."
            style={{ minWidth: 280 }}
          />
        </Field>
        <Button appearance="primary" type="submit" disabled={isLoading}>
          {isLoading ? "Loading..." : "Apply"}
        </Button>
      </form>

      {error && <ErrorState message="Failed to load runs" detail={error} onRetry={load} />}
      {isLoading && <Spinner label="Loading runs..." />}

      {runs && runs.length === 0 && (
        <Body1 style={{ color: "#888" }}>No runs match the current filters.</Body1>
      )}

      {runs && runs.length > 0 && (
        <Table aria-label="Run history">
          <TableHeader>
            <TableRow>
              <TableHeaderCell scope="col">Run ID</TableHeaderCell>
              <TableHeaderCell scope="col">Subscription</TableHeaderCell>
              <TableHeaderCell scope="col">Type</TableHeaderCell>
              <TableHeaderCell scope="col">Status</TableHeaderCell>
              <TableHeaderCell scope="col">Duration</TableHeaderCell>
              <TableHeaderCell scope="col">Correlation ID</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {runs.map((r) => (
              <TableRow key={r.runId}>
                <TableCell style={{ fontFamily: "monospace", fontSize: 12 }}>
                  {r.runId}
                </TableCell>
                <TableCell style={{ fontFamily: "monospace", fontSize: 12 }}>
                  {r.subscriptionId}
                </TableCell>
                <TableCell>
                  <Badge appearance="outline" size="small">{r.type}</Badge>
                </TableCell>
                <TableCell>
                  <Badge color={statusColor(r.status)} size="small">{r.status}</Badge>
                </TableCell>
                <TableCell style={{ fontSize: 13 }}>
                  {r.durationMs != null ? `${(r.durationMs / 1000).toFixed(1)}s` : "--"}
                </TableCell>
                <TableCell style={{ fontFamily: "monospace", fontSize: 12, color: "#888" }}>
                  {r.correlationId ?? "--"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
