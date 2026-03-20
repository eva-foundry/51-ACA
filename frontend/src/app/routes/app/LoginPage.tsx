// EVA-STORY: ACA-05-016
/**
 * LoginPage -- ACA entry point.
 * Entra ID OIDC sign-in CTA.
 * Dev bypass: when VITE_DEV_AUTH=true, auto-redirects to /app/connect.
 */

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Button, Subtitle1, Body1 } from "@fluentui/react-components";
import { useAuth } from "../../auth/useAuth";

export default function LoginPage() {
  const { t } = useTranslation();
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
        {t("app.title")}
      </h1>
      <Subtitle1>
        {t("pages.login.tagline")}
      </Subtitle1>
      <Body1 style={{ maxWidth: 480, color: "#555" }}>
        {t("pages.login.description")}
      </Body1>

      <Button
        appearance="primary"
        size="large"
        onClick={handleLogin}
        style={{ marginTop: 16, minWidth: 200 }}
      >
        {t("pages.login.sign_in")}
      </Button>

      {import.meta.env.VITE_DEV_AUTH === "true" && (
        <Body1 style={{ fontSize: 12, color: "#888", marginTop: 8 }}>
          {t("pages.login.dev_mode")}
        </Body1>
      )}
    </div>
  );
}
