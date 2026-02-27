// EVA-STORY: ACA-05-022
/**
 * AdminCustomersPage -- /admin/customers
 * Search + table of customer subscriptions.
 * Deep-link to AdminRunsPage per subscription.
 */

import { useState, FormEvent } from "react";
import { Link } from "react-router-dom";
import {
  Button,
  Input,
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
} from "@fluentui/react-components";
import { adminApi } from "../../api/adminApi";
import { ErrorState } from "../../components/ErrorState";
import type { AdminCustomerRow } from "../../types/models";

export default function AdminCustomersPage() {
  const [query, setQuery] = useState("");
  const [rows, setRows] = useState<AdminCustomerRow[] | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e?: FormEvent) => {
    e?.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      const { items } = await adminApi.searchCustomers(query);
      setRows(items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <Subtitle1 as="h1" block style={{ marginBottom: 24 }}>
        Customers
      </Subtitle1>

      <form
        role="search"
        onSubmit={handleSearch}
        style={{ display: "flex", gap: 8, alignItems: "flex-end", marginBottom: 24 }}
      >
        <Input
          value={query}
          onChange={(_, { value }) => setQuery(value)}
          placeholder="Search by subscription ID, UPN, or tier..."
          style={{ minWidth: 320 }}
          aria-label="Search customers"
        />
        <Button appearance="primary" type="submit" disabled={isLoading}>
          {isLoading ? "Searching..." : "Search"}
        </Button>
      </form>

      {error && <ErrorState message="Search failed" detail={error} onRetry={handleSearch} />}
      {isLoading && <Spinner label="Searching..." />}

      {rows && rows.length === 0 && (
        <Body1 style={{ color: "#888" }}>No customers found for query: "{query}"</Body1>
      )}

      {rows && rows.length > 0 && (
        <Table aria-label="Customer search results">
          <TableHeader>
            <TableRow>
              <TableHeaderCell scope="col">Subscription ID</TableHeaderCell>
              <TableHeaderCell scope="col">Tier</TableHeaderCell>
              <TableHeaderCell scope="col">Payment Status</TableHeaderCell>
              <TableHeaderCell scope="col">Locked</TableHeaderCell>
              <TableHeaderCell scope="col">Last Activity</TableHeaderCell>
              <TableHeaderCell scope="col">Actions</TableHeaderCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.subscriptionId}>
                <TableCell style={{ fontFamily: "monospace", fontSize: 13 }}>
                  {row.subscriptionId}
                </TableCell>
                <TableCell>
                  <Badge appearance="filled" size="small">
                    Tier {row.tier}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge
                    color={row.paymentStatus === "paid" ? "success" : "warning"}
                    size="small"
                  >
                    {row.paymentStatus}
                  </Badge>
                </TableCell>
                <TableCell>
                  {row.isLocked ? (
                    <Badge color="danger" size="small">LOCKED</Badge>
                  ) : (
                    <Badge color="success" size="small">Active</Badge>
                  )}
                </TableCell>
                <TableCell style={{ fontSize: 12, color: "#666" }}>
                  {row.lastActivityUtc
                    ? new Date(row.lastActivityUtc).toLocaleString("en-CA")
                    : "--"}
                </TableCell>
                <TableCell>
                  <Link
                    to={`/admin/runs?subscriptionId=${encodeURIComponent(row.subscriptionId)}`}
                    style={{ fontSize: 13 }}
                  >
                    View Runs
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
