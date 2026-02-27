// EVA-STORY: ACA-05-008
/**
 * NavCustomer -- top navigation for the customer surface (/app/*).
 * Logo + nav links + LanguageSelector + user menu.
 */

import { Link, useLocation } from "react-router-dom";
import { Button, Text } from "@fluentui/react-components";
import { LanguageSelector } from "../../components/LanguageSelector";
import { useAuth } from "../auth/useAuth";

export function NavCustomer() {
  const { user, logout } = useAuth();
  const { pathname } = useLocation();

  const navLink = (to: string, label: string) => (
    <Link
      to={to}
      style={{
        textDecoration: "none",
        color: pathname.startsWith(to) ? "#0078d4" : "#333",
        fontWeight: pathname.startsWith(to) ? 600 : 400,
        padding: "0 12px",
      }}
    >
      {label}
    </Link>
  );

  return (
    <nav
      aria-label="Customer navigation"
      style={{
        display: "flex",
        alignItems: "center",
        gap: 8,
        padding: "0 24px",
        height: 48,
        borderBottom: "1px solid #d0d0d0",
        background: "#fff",
      }}
    >
      <a href="/" aria-label="ACA Home" style={{ fontWeight: 700, fontSize: 20, color: "#0078d4", textDecoration: "none", marginRight: 24 }}>
        ACA
      </a>

      {navLink("/app/connect", "Connect")}

      {user?.subscriptionId && (
        <>
          {navLink(`/app/status/${user.subscriptionId}`, "Status")}
          {navLink(`/app/findings/${user.subscriptionId}`, "Report")}
        </>
      )}

      <div style={{ flex: 1 }} />
      <LanguageSelector />

      {user && (
        <Text size={200} style={{ marginLeft: 16 }}>
          {user.upn}
        </Text>
      )}

      <Button size="small" appearance="subtle" onClick={logout} style={{ marginLeft: 8 }}>
        Sign out
      </Button>
    </nav>
  );
}
