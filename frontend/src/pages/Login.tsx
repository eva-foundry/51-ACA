import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Title2, Text, Button, makeStyles, tokens } from "@fluentui/react-components";
import { trackPageView, trackEvent } from "../telemetry/analytics";

const useStyles = makeStyles({
  root: { maxWidth: "480px", margin: "0 auto", padding: tokens.spacingVerticalXXL },
});

export default function Login() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const styles = useStyles();

  useEffect(() => { trackPageView("/login", "Login"); }, []);

  function handleConnect() {
    trackEvent("connect_flow_started");
    navigate("/connect");
  }

  return (
    <main className={styles.root}>
      <Title2 id="login-heading">{t("actions.connect_subscription")}</Title2>
      <Text block>{t("app.tagline")}</Text>
      <Button
        appearance="primary"
        onClick={handleConnect}
        style={{ marginTop: tokens.spacingVerticalL }}
        aria-describedby="login-heading"
      >
        {t("actions.connect_subscription")}
      </Button>
    </main>
  );
}
