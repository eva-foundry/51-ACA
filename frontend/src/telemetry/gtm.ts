/**
 * Google Tag Manager loader.
 * Only loads GTM script if consent has been granted.
 * GTM then fires GA4 and Clarity based on tag rules.
 */

declare global {
  interface Window {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    dataLayer: any[];
  }
}

let gtmLoaded = false;

export function loadGTM(containerId: string): void {
  if (gtmLoaded || !containerId) return;
  gtmLoaded = true;

  window.dataLayer = window.dataLayer || [];

  // GTM snippet
  (function (w, d, s, l, i) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (w as any)[l] = (w as any)[l] || [];
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (w as any)[l].push({
      "gtm.start": new Date().getTime(),
      event: "gtm.js",
    });
    const f = d.getElementsByTagName(s)[0]!;
    const j = d.createElement(s) as HTMLScriptElement;
    const dl = l !== "dataLayer" ? `&l=${l}` : "";
    j.async = true;
    j.src = `https://www.googletagmanager.com/gtm.js?id=${i}${dl}`;
    f.parentNode!.insertBefore(j, f);
  })(window, document, "script", "dataLayer", containerId);
}

export function pushEvent(event: string, params?: Record<string, unknown>): void {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event, ...params });
}
