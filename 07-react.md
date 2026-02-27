Got it — here are \*\*copy/paste-ready React (Vite/CRA-compatible) stubs\*\* for:



\* GA4 via \*\*GTM dataLayer\*\*

\* Microsoft \*\*Clarity\*\* custom events

\* A simple \*\*consent banner\*\* (no dependencies)

\* A small \*\*provider wrapper\*\* you can drop into `App.tsx`



No secrets, no Azure identifiers, no emails.



---



\## 1) `frontend/src/telemetry/consent.ts`



```ts

// frontend/src/telemetry/consent.ts

export type TelemetryConsent = "accepted" | "rejected" | "unset";



const CONSENT\_KEY = "aca\_telemetry\_consent\_v1";



export function getTelemetryConsent(): TelemetryConsent {

&nbsp; const v = localStorage.getItem(CONSENT\_KEY);

&nbsp; if (v === "accepted" || v === "rejected") return v;

&nbsp; return "unset";

}



export function setTelemetryConsent(consent: Exclude<TelemetryConsent, "unset">) {

&nbsp; localStorage.setItem(CONSENT\_KEY, consent);

}



export function isTelemetryEnabled(): boolean {

&nbsp; return getTelemetryConsent() === "accepted";

}

```



---



\## 2) `frontend/src/telemetry/gtm.ts`



```ts

// frontend/src/telemetry/gtm.ts

declare global {

&nbsp; interface Window {

&nbsp;   dataLayer?: any\[];

&nbsp; }

}



export function ensureDataLayer() {

&nbsp; if (!window.dataLayer) window.dataLayer = \[];

}



export function pushToDataLayer(event: string, props: Record<string, unknown> = {}) {

&nbsp; ensureDataLayer();

&nbsp; window.dataLayer!.push({

&nbsp;   event,

&nbsp;   ...props,

&nbsp; });

}

```



---



\## 3) `frontend/src/telemetry/clarity.ts`



```ts

// frontend/src/telemetry/clarity.ts

declare global {

&nbsp; interface Window {

&nbsp;   clarity?: (...args: any\[]) => void;

&nbsp; }

}



/\*\*

&nbsp;\* Clarity custom events:

&nbsp;\* https://learn.microsoft.com/en-us/clarity/setup-and-installation/clarity-api

&nbsp;\*/

export function clarityEvent(name: string) {

&nbsp; if (typeof window.clarity === "function") {

&nbsp;   window.clarity("event", name);

&nbsp; }

}



/\*\*

&nbsp;\* Optional: set user properties (keep privacy-safe).

&nbsp;\* Avoid email, tenantId, subscriptionId, etc.

&nbsp;\*/

export function claritySet(key: string, value: string) {

&nbsp; if (typeof window.clarity === "function") {

&nbsp;   window.clarity("set", key, value);

&nbsp; }

}

```



---



\## 4) `frontend/src/telemetry/analytics.ts`



```ts

// frontend/src/telemetry/analytics.ts

import { isTelemetryEnabled } from "./consent";

import { pushToDataLayer } from "./gtm";

import { clarityEvent } from "./clarity";



export type AcaTier = 1 | 2 | 3;



export type AnalyticsEventName =

&nbsp; | "login\_success"

&nbsp; | "subscription\_selected"

&nbsp; | "preflight\_started"

&nbsp; | "preflight\_pass"

&nbsp; | "preflight\_fail"

&nbsp; | "scan\_started"

&nbsp; | "scan\_completed"

&nbsp; | "analysis\_started"

&nbsp; | "analysis\_completed"

&nbsp; | "findings\_viewed\_tier1"

&nbsp; | "unlock\_cta\_clicked"

&nbsp; | "checkout\_started"

&nbsp; | "checkout\_completed"

&nbsp; | "deliverable\_ready"

&nbsp; | "deliverable\_downloaded";



export type ErrorCategory = "missing\_permission" | "auth\_failed" | "api\_error" | "rate\_limited";



export type AnalyticsProps = Record<string, unknown>;



/\*\*

&nbsp;\* Privacy guardrails:

&nbsp;\* - DO NOT send: subscriptionId, tenantId, emails, resource names, meter names, raw costs per resource.

&nbsp;\* - Use only opaque ACA ids (scanId, analysisId, deliverableId) and coarse metrics (counts, durations).

&nbsp;\*/

export function track(eventName: AnalyticsEventName, props: AnalyticsProps = {}) {

&nbsp; if (!isTelemetryEnabled()) return;



&nbsp; // Always add a timestamp. Avoid PII.

&nbsp; const safeProps = {

&nbsp;   event\_time\_utc: new Date().toISOString(),

&nbsp;   ...props,

&nbsp; };



&nbsp; // GTM/GA4: push into dataLayer

&nbsp; pushToDataLayer(eventName, safeProps);



&nbsp; // Clarity: optionally mirror key events for UX replay filters

&nbsp; // Keep it low volume and meaningful.

&nbsp; if (

&nbsp;   eventName === "preflight\_fail" ||

&nbsp;   eventName === "unlock\_cta\_clicked" ||

&nbsp;   eventName === "checkout\_started" ||

&nbsp;   eventName === "checkout\_completed" ||

&nbsp;   eventName === "deliverable\_downloaded"

&nbsp; ) {

&nbsp;   clarityEvent(eventName);

&nbsp; }

}

```



---



\## 5) `frontend/src/components/ConsentBanner.tsx`



```tsx

// frontend/src/components/ConsentBanner.tsx

import React from "react";

import { getTelemetryConsent, setTelemetryConsent, TelemetryConsent } from "../telemetry/consent";



type Props = {

&nbsp; onChoice?: (consent: Exclude<TelemetryConsent, "unset">) => void;

};



export function ConsentBanner({ onChoice }: Props) {

&nbsp; const \[consent, setConsent] = React.useState<TelemetryConsent>("unset");



&nbsp; React.useEffect(() => {

&nbsp;   setConsent(getTelemetryConsent());

&nbsp; }, \[]);



&nbsp; if (consent !== "unset") return null;



&nbsp; const accept = () => {

&nbsp;   setTelemetryConsent("accepted");

&nbsp;   setConsent("accepted");

&nbsp;   onChoice?.("accepted");

&nbsp; };



&nbsp; const reject = () => {

&nbsp;   setTelemetryConsent("rejected");

&nbsp;   setConsent("rejected");

&nbsp;   onChoice?.("rejected");

&nbsp; };



&nbsp; return (

&nbsp;   <div

&nbsp;     role="dialog"

&nbsp;     aria-live="polite"

&nbsp;     aria-label="Analytics consent"

&nbsp;     style={{

&nbsp;       position: "fixed",

&nbsp;       left: 16,

&nbsp;       right: 16,

&nbsp;       bottom: 16,

&nbsp;       padding: 16,

&nbsp;       borderRadius: 12,

&nbsp;       background: "white",

&nbsp;       boxShadow: "0 10px 30px rgba(0,0,0,0.15)",

&nbsp;       zIndex: 9999,

&nbsp;       maxWidth: 960,

&nbsp;       margin: "0 auto",

&nbsp;     }}

&nbsp;   >

&nbsp;     <div style={{ display: "flex", gap: 16, alignItems: "flex-start", flexWrap: "wrap" }}>

&nbsp;       <div style={{ flex: "1 1 420px", minWidth: 280 }}>

&nbsp;         <div style={{ fontWeight: 700, marginBottom: 6 }}>Help us improve ACA</div>

&nbsp;         <div style={{ lineHeight: 1.4 }}>

&nbsp;           We use Google Analytics (GA4) and Microsoft Clarity to understand product usage and improve the

&nbsp;           experience. We do not send Azure subscription IDs, tenant IDs, emails, or resource names.

&nbsp;         </div>

&nbsp;       </div>

&nbsp;       <div style={{ display: "flex", gap: 8, flex: "0 0 auto" }}>

&nbsp;         <button

&nbsp;           type="button"

&nbsp;           onClick={reject}

&nbsp;           style={{

&nbsp;             padding: "10px 14px",

&nbsp;             borderRadius: 10,

&nbsp;             border: "1px solid #ccc",

&nbsp;             background: "white",

&nbsp;             cursor: "pointer",

&nbsp;             fontWeight: 600,

&nbsp;           }}

&nbsp;         >

&nbsp;           Reject

&nbsp;         </button>

&nbsp;         <button

&nbsp;           type="button"

&nbsp;           onClick={accept}

&nbsp;           style={{

&nbsp;             padding: "10px 14px",

&nbsp;             borderRadius: 10,

&nbsp;             border: "1px solid #0b57d0",

&nbsp;             background: "#0b57d0",

&nbsp;             color: "white",

&nbsp;             cursor: "pointer",

&nbsp;             fontWeight: 700,

&nbsp;           }}

&nbsp;         >

&nbsp;           Accept

&nbsp;         </button>

&nbsp;       </div>

&nbsp;     </div>

&nbsp;   </div>

&nbsp; );

}

```



---



\## 6) Wire it into React: `frontend/src/App.tsx` (example)



```tsx

// frontend/src/App.tsx

import React from "react";

import { ConsentBanner } from "./components/ConsentBanner";

import { track } from "./telemetry/analytics";



export default function App() {

&nbsp; return (

&nbsp;   <>

&nbsp;     <ConsentBanner

&nbsp;       onChoice={(c) => {

&nbsp;         // Optional: track consent choice ONLY after accepted (since telemetry must be off by default).

&nbsp;         if (c === "accepted") track("login\_success", { source: "consent\_accept\_example" });

&nbsp;       }}

&nbsp;     />



&nbsp;     <main style={{ padding: 24 }}>

&nbsp;       <h1>ACA</h1>



&nbsp;       <button

&nbsp;         onClick={() =>

&nbsp;           track("preflight\_started", {

&nbsp;             mode: "delegated",

&nbsp;           })

&nbsp;         }

&nbsp;       >

&nbsp;         Example: Preflight Started

&nbsp;       </button>

&nbsp;     </main>

&nbsp;   </>

&nbsp; );

}

```



---



\## 7) GTM + GA4 + Clarity setup (what to paste where)



\### Add GTM snippet to `frontend/index.html`



Replace `GTM-XXXXXXX` with your GTM container ID.



```html

<!-- Google Tag Manager -->

<script>

&nbsp; (function (w, d, s, l, i) {

&nbsp;   w\[l] = w\[l] || \[];

&nbsp;   w\[l].push({ "gtm.start": new Date().getTime(), event: "gtm.js" });

&nbsp;   var f = d.getElementsByTagName(s)\[0],

&nbsp;     j = d.createElement(s),

&nbsp;     dl = l != "dataLayer" ? "\&l=" + l : "";

&nbsp;   j.async = true;

&nbsp;   j.src = "https://www.googletagmanager.com/gtm.js?id=" + i + dl;

&nbsp;   f.parentNode.insertBefore(j, f);

&nbsp; })(window, document, "script", "dataLayer", "GTM-XXXXXXX");

</script>

<!-- End Google Tag Manager -->

```



\*\*Note:\*\* If you want \*strict\* consent gating, you can conditionally inject this script only after consent. The above code assumes you’ll block tags in GTM until consent.



\### In GTM



\* Create \*\*GA4 Configuration\*\* tag (your GA measurement ID)

\* Create \*\*GA4 Event\*\* tag:



&nbsp; \* Event Name: `{{Event}}`

&nbsp; \* Parameters: map from dataLayer fields you send (e.g., `analysisId`, `tier`, etc.)

\* Add \*\*Clarity\*\* tag using your Clarity project ID (via template or custom HTML)

\* Add a \*\*Consent\*\* mechanism (either GTM consent mode or a simple “block triggers until consent” variable)



---



\## Next (payments integration)



If you want, I’ll generate the matching backend stubs:



\* `routers/checkout.py` (Stripe Checkout Session create)

\* `routers/webhooks\_stripe.py` (signature verification + entitlement unlock)

\* `routers/billing.py` (customer portal)

\* `routers/entitlements.py`



Just say: \*\*“generate the Stripe backend stubs”\*\* and tell me whether you’re using \*\*FastAPI\*\* (I assumed yes from your earlier plan).



