// EVA-STORY: ACA-05-007
/**
 * AdminLayout -- wraps all /admin/* admin routes.
 * NavAdmin sidebar (left) + main content area via <Outlet />.
 */

import { Outlet } from "react-router-dom";
import { Suspense } from "react";
import { NavAdmin } from "./NavAdmin";
import { Loading } from "../components/Loading";

export function AdminLayout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <NavAdmin />

      <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
        <header style={{ padding: "12px 24px", borderBottom: "1px solid #d0d0d0", background: "#fff" }}>
          <span style={{ fontSize: 14, color: "#555" }}>Azure Cost Advisor &mdash; Admin Console</span>
        </header>

        <main
          id="main-content"
          tabIndex={-1}
          style={{ flex: 1, padding: "24px", background: "#fafafa" }}
        >
          <Suspense fallback={<Loading label="Loading page..." />}>
            <Outlet />
          </Suspense>
        </main>
      </div>
    </div>
  );
}
