// EVA-STORY: ACA-05-035
import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  Button,
  Text,
  makeStyles,
  tokens,
} from "@fluentui/react-components";
import { getConsent, acceptAll, rejectNonEssential } from "../telemetry/consent";
import { loadGTM } from "../telemetry/gtm";

const useStyles = makeStyles({
  banner: {
    position: "fixed",
    bottom: 0,
    left: 0,
    right: 0,
    backgroundColor: tokens.colorNeutralBackground1,
    borderTop: `1px solid ${tokens.colorNeutralStroke1}`,
    padding: `${tokens.spacingVerticalM} ${tokens.spacingHorizontalL}`,
    display: "flex",
    gap: tokens.spacingHorizontalM,
    alignItems: "center",
    flexWrap: "wrap",
    zIndex: 1000,
  },
  text: {
    flex: 1,
    minWidth: "200px",
  },
  actions: {
    display: "flex",
    gap: tokens.spacingHorizontalS,
    flexWrap: "wrap",
  },
});

export function ConsentBanner() {
  const { t } = useTranslation();
  const styles = useStyles();
  const [show, setShow] = useState(false);

  useEffect(() => {
    const consent = getConsent();
    if (!consent) {
      setShow(true);
    } else if (consent.analytics_storage === "granted") {
      // Previously accepted -- load GTM now
      const gtmId = import.meta.env.VITE_GTM_CONTAINER_ID as string | undefined;
      if (gtmId) loadGTM(gtmId);
    }
  }, []);

  function handleAccept() {
    acceptAll();
    const gtmId = import.meta.env.VITE_GTM_CONTAINER_ID as string | undefined;
    if (gtmId) loadGTM(gtmId);
    setShow(false);
  }

  function handleReject() {
    rejectNonEssential();
    setShow(false);
  }

  if (!show) return null;

  return (
    <div
      role="dialog"
      aria-labelledby="consent-title"
      aria-describedby="consent-body"
      className={styles.banner}
    >
      <div className={styles.text}>
        <Text weight="semibold" id="consent-title">
          {t("consent.banner_title")}
        </Text>
        <Text id="consent-body" block>
          {t("consent.banner_body")}
        </Text>
      </div>
      <div className={styles.actions}>
        <Button appearance="primary" onClick={handleAccept}>
          {t("consent.accept")}
        </Button>
        <Button appearance="secondary" onClick={handleReject}>
          {t("consent.reject")}
        </Button>
      </div>
    </div>
  );
}
