// EVA-STORY: ACA-05-006
/**
 * CustomerLayout -- wraps all /app/* customer routes.
 * NavCustomer top bar + main content area via <Outlet />.
 */

import { Outlet } from "react-router-dom";
import { Suspense } from "react";
import { NavCustomer } from "./NavCustomer";
import { Loading } from "../components/Loading";

export function CustomerLayout() {
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
      <NavCustomer />

      <main
        id="main-content"
        tabIndex={-1}
        style={{ flex: 1, padding: "24px 32px", maxWidth: 1200, width: "100%", margin: "0 auto" }}
      >
        <Suspense fallback={<Loading label="Loading page..." />}>
          <Outlet />
        </Suspense>
      </main>

      <footer style={{ padding: "16px 32px", borderTop: "1px solid #d0d0d0", fontSize: 12, color: "#888" }}>
        ACA -- Azure Cost Advisor. All data handled per our privacy policy.
      </footer>
    </div>
  );
}
