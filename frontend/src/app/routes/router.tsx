// EVA-STORY: ACA-05-011
/**
 * ACA router -- Spark pattern (docs 22-23).
 *
 * Customer surface: /app/* -- RequireAuth -> CustomerLayout
 * Admin surface:    /admin/* -- RequireAuth -> RequireRole -> AdminLayout
 * Root route:       / -> LoginPage (no auth)
 *
 * All page components are lazy-loaded for optimal bundle splitting.
 */

import { createBrowserRouter } from "react-router-dom";
import { lazy } from "react";

import { RequireAuth } from "../auth/RequireAuth";
import { RequireRole } from "../auth/RequireRole";
import { CustomerLayout } from "../layout/CustomerLayout";
import { AdminLayout } from "../layout/AdminLayout";
import { ADMIN_ROLES } from "../auth/roles";

// Customer pages (lazy)
const LoginPage               = lazy(() => import("./app/LoginPage"));
const ConnectSubscriptionPage = lazy(() => import("./app/ConnectSubscriptionPage"));
const CollectionStatusPage    = lazy(() => import("./app/CollectionStatusPage"));
const FindingsTier1Page       = lazy(() => import("./app/FindingsTier1Page"));
const UpgradePage             = lazy(() => import("./app/UpgradePage"));

// Admin pages (lazy)
const AdminDashboardPage  = lazy(() => import("./admin/AdminDashboardPage"));
const AdminCustomersPage  = lazy(() => import("./admin/AdminCustomersPage"));
const AdminBillingPage    = lazy(() => import("./admin/AdminBillingPage"));
const AdminRunsPage       = lazy(() => import("./admin/AdminRunsPage"));
const AdminControlsPage   = lazy(() => import("./admin/AdminControlsPage"));

export const router = createBrowserRouter([
  // Root: Login (no auth required)
  { path: "/", element: <LoginPage /> },

  // Customer surface
  {
    path: "/app",
    element: (
      <RequireAuth>
        <CustomerLayout />
      </RequireAuth>
    ),
    children: [
      { path: "connect",                element: <ConnectSubscriptionPage /> },
      { path: "status/:subscriptionId", element: <CollectionStatusPage />   },
      { path: "findings/:subscriptionId", element: <FindingsTier1Page />    },
      { path: "upgrade/:subscriptionId",  element: <UpgradePage />          },
    ],
  },

  // Admin surface
  {
    path: "/admin",
    element: (
      <RequireAuth>
        <RequireRole anyOf={ADMIN_ROLES as unknown as import("../auth/roles").AcaRole[]}>
          <AdminLayout />
        </RequireRole>
      </RequireAuth>
    ),
    children: [
      { path: "dashboard",  element: <AdminDashboardPage /> },
      { path: "customers",  element: <AdminCustomersPage /> },
      { path: "billing",    element: <AdminBillingPage />   },
      { path: "runs",       element: <AdminRunsPage />      },
      { path: "controls",   element: <AdminControlsPage />  },
    ],
  },
]);
