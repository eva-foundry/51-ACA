import React from "react";

export function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "Segoe UI, Arial, sans-serif" }}>
      <aside style={{ width: 260, padding: 16, borderRight: "1px solid #e5e5e5", background: "#fafafa" }}>
        <div style={{ fontWeight: 800, marginBottom: 16 }}>ACA Admin</div>
        <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <a href="/admin/dashboard">Dashboard</a>
          <a href="/admin/customers">Customers</a>
          <a href="/admin/billing">Billing</a>
          <a href="/admin/runs">Runs</a>
          <a href="/admin/audit">Audit</a>
        </nav>
        <div style={{ marginTop: 24, fontSize: 12, opacity: 0.7 }}>
          Backend RBAC is authoritative.
        </div>
      </aside>
      <main style={{ flex: 1, padding: 24 }}>{children}</main>
    </div>
  );
}
