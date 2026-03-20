import React from "react";
import { AdminLayout } from "./components/AdminLayout";
import { AdminRoutes } from "./routes";

export function AdminApp() {
  return (
    <AdminLayout>
      <AdminRoutes />
    </AdminLayout>
  );
}
