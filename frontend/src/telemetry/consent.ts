// EVA-STORY: ACA-08-005
/**
 * Consent state management.
 * Consent is required before loading GTM (which fires GA4 and Clarity).
 * Complies with Google Consent Mode v2 and PIPEDA requirements.
 */

export type ConsentState = {
  analytics_storage: "granted" | "denied";
  functionality_storage: "granted" | "denied";
  personalization_storage: "granted" | "denied";
};

const CONSENT_KEY = "aca_consent";

export function getConsent(): ConsentState | null {
  try {
    const raw = localStorage.getItem(CONSENT_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as ConsentState;
  } catch {
    return null;
  }
}

export function setConsent(state: ConsentState): void {
  localStorage.setItem(CONSENT_KEY, JSON.stringify(state));
  // Push to dataLayer for GTM Consent Mode v2
  pushConsentUpdate(state);
}

export function hasConsented(): boolean {
  const c = getConsent();
  return c?.analytics_storage === "granted";
}

export function acceptAll(): void {
  setConsent({
    analytics_storage: "granted",
    functionality_storage: "granted",
    personalization_storage: "granted",
  });
}

export function rejectNonEssential(): void {
  setConsent({
    analytics_storage: "denied",
    functionality_storage: "denied",
    personalization_storage: "denied",
  });
}

function pushConsentUpdate(state: ConsentState): void {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const dl = (window as any).dataLayer;
  if (!dl) return;
  dl.push({
    event: "consent_update",
    ...state,
  });
}
