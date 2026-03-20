import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { RequireRole } from "./components/RequireRole";
import { DashboardPage } from "./pages/DashboardPage";
import { CustomersPage } from "./pages/CustomersPage";
import { BillingPage } from "./pages/BillingPage";
import { RunsPage } from "./pages/RunsPage";
import { AuditPage } from "./pages/AuditPage";

export function AdminRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/admin/dashboard" replace />} />
      <Route
        path="/dashboard"
        element={<RequireRole anyOf={["ACA_Admin", "ACA_FinOps"]}><DashboardPage /></RequireRole>}
      />
      <Route
        path="/customers"
        element={<RequireRole anyOf={["ACA_Admin", "ACA_Support"]}><CustomersPage /></RequireRole>}
      />
      <Route
        path="/billing"
        element={<RequireRole anyOf={["ACA_Admin", "ACA_FinOps"]}><BillingPage /></RequireRole>}
      />
      <Route
        path="/runs"
        element={<RequireRole anyOf={["ACA_Admin", "ACA_Support"]}><RunsPage /></RequireRole>}
      />
      <Route
        path="/audit"
        element={<RequireRole anyOf={["ACA_Admin"]}><AuditPage /></RequireRole>}
      />
      <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
    </Routes>
  );
}
