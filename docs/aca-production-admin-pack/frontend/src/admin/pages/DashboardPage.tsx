import React from "react";

export function DashboardPage() {
  return (
    <div>
      <h1>Dashboard</h1>
      <p>MTD revenue, active subscriptions, 24h scans/analyses/deliveries, failure rate.</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginTop: 12 }}>
        {[
          "Revenue MTD",
          "Active subscriptions",
          "Scans (24h)",
          "Analyses (24h)",
          "Deliveries (24h)",
          "Failure rate (24h)",
          "Webhook lag p95",
          "Churn MTD",
        ].map((k) => (
          <div key={k} style={{ border: "1px solid #e5e5e5", borderRadius: 12, padding: 12, background: "white" }}>
            <div style={{ fontWeight: 700 }}>{k}</div>
            <div style={{ fontSize: 28, marginTop: 6 }}>—</div>
          </div>
        ))}
      </div>
    </div>
  );
}
