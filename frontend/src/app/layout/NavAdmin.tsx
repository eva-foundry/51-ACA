/**
 * NavAdmin -- top nav + sidebar for the admin surface (/admin/*).
 * Logo + sidebar links + user info.
 */

import { Link, useLocation } from "react-router-dom";
import { Button, Text } from "@fluentui/react-components";
import { useAuth } from "../auth/useAuth";

const ADMIN_LINKS = [
  { to: "/admin/dashboard",  label: "Dashboard"  },
  { to: "/admin/customers",  label: "Customers"  },
  { to: "/admin/billing",    label: "Billing"    },
  { to: "/admin/runs",       label: "Runs"       },
  { to: "/admin/controls",   label: "Controls"   },
];

export function NavAdmin() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();

  return (
    <nav
      aria-label="Admin navigation"
      style={{
        display: "flex",
        flexDirection: "column",
        width: 200,
        minHeight: "100vh",
        borderRight: "1px solid #d0d0d0",
        background: "#f5f5f5",
        padding: "16px 0",
      }}
    >
      <div style={{ padding: "0 16px 16px", borderBottom: "1px solid #d0d0d0" }}>
        <a
          href="/admin/dashboard"
          aria-label="ACA Admin"
          style={{ fontWeight: 700, fontSize: 18, color: "#0078d4", textDecoration: "none" }}
        >
          ACA Admin
        </a>
      </div>

      <ul style={{ listStyle: "none", margin: 0, padding: "8px 0", flex: 1 }} role="menubar">
        {ADMIN_LINKS.map(({ to, label }) => (
          <li key={to} role="none">
            <Link
              to={to}
              role="menuitem"
              style={{
                display: "block",
                padding: "10px 20px",
                textDecoration: "none",
                background: pathname.startsWith(to) ? "#dde8f5" : "transparent",
                color: pathname.startsWith(to) ? "#003c82" : "#333",
                fontWeight: pathname.startsWith(to) ? 600 : 400,
                borderLeft: pathname.startsWith(to) ? "3px solid #0078d4" : "3px solid transparent",
              }}
            >
              {label}
            </Link>
          </li>
        ))}
      </ul>

      <div style={{ padding: "12px 16px", borderTop: "1px solid #d0d0d0" }}>
        {user && (
          <Text size={100} style={{ display: "block", marginBottom: 8, color: "#555" }}>
            {user.upn}
          </Text>
        )}
        <Button size="small" appearance="subtle" onClick={logout}>
          Sign out
        </Button>
      </div>
    </nav>
  );
}
