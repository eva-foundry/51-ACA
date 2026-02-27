// EVA-STORY: ACA-05-016
/**
 * LoginPage -- ACA entry point.
 * Entra ID OIDC sign-in CTA.
 * Dev bypass: when VITE_DEV_AUTH=true, auto-redirects to /app/connect.
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Subtitle1, Body1 } from "@fluentui/react-components";
import { useAuth } from "../../auth/useAuth";

export default function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const navigate = useNavigate();

  // If already authenticated, go to connect page
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/app/connect", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleLogin = async () => {
    await login();
    navigate("/app/connect");
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "80vh",
        gap: 24,
        textAlign: "center",
        padding: 32,
      }}
    >
      <h1 style={{ fontSize: 40, fontWeight: 700, color: "#0078d4", margin: 0 }}>
        Azure Cost Advisor
      </h1>
      <Subtitle1>
        Connect your Azure subscription and get a free prioritized cost report in minutes.
      </Subtitle1>
      <Body1 style={{ maxWidth: 480, color: "#555" }}>
        Read-only access. No resource modifications. Run a free Tier 1 scan with no credit card
        required. Unlock full advisory and IaC deliverables with Tier 2 and Tier 3.
      </Body1>

      <Button
        appearance="primary"
        size="large"
        onClick={handleLogin}
        style={{ marginTop: 16, minWidth: 200 }}
      >
        Sign in with Microsoft
      </Button>

      {import.meta.env.VITE_DEV_AUTH === "true" && (
        <Body1 style={{ fontSize: 12, color: "#888", marginTop: 8 }}>
          Dev mode active (VITE_DEV_AUTH=true) &mdash; sign-in is bypassed.
        </Body1>
      )}
    </div>
  );
}
