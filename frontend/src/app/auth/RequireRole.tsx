/**
 * RequireRole -- redirect to /app/connect if user lacks any of the specified roles.
 * Use inside RequireAuth so the user is already known to be authenticated.
 *
 * Usage (in router.tsx):
 *   <RequireRole anyOf={["ACA_Admin", "ACA_Support", "ACA_FinOps"]}>
 *     <AdminLayout />
 *   </RequireRole>
 */

import { type ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "./useAuth";
import type { AcaRole } from "./roles";

interface Props {
  anyOf: AcaRole[];
  children: ReactNode;
}

export function RequireRole({ anyOf, children }: Props) {
  const { hasRole } = useAuth();

  if (!hasRole(...anyOf)) {
    return <Navigate to="/app/connect" replace />;
  }

  return <>{children}</>;
}
