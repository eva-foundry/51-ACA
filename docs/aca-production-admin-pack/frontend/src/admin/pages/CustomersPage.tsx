import React from "react";
import { SearchBar } from "../components/SearchBar";

export function CustomersPage() {
  const [q, setQ] = React.useState("");

  const runSearch = async () => {
    console.log("search", q);
  };

  return (
    <div>
      <h1>Customers</h1>
      <SearchBar
        value={q}
        onChange={setQ}
        onSubmit={runSearch}
        placeholder="Search by subscriptionId / Stripe customer id…"
      />

      <div style={{ marginTop: 16, border: "1px solid #e5e5e5", borderRadius: 12, padding: 12 }}>
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Results</div>
        <div style={{ opacity: 0.7 }}>No results yet.</div>
      </div>

      <div style={{ marginTop: 16 }}>
        <h2>Support actions</h2>
        <ul>
          <li>Grant Tier 2 / Tier 3 for N days</li>
          <li>Lock / unlock subscription</li>
          <li>Open Stripe portal</li>
        </ul>
      </div>
    </div>
  );
}
