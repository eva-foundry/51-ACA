// EVA-STORY: ACA-05-010
import React from "react";
import ReactDOM from "react-dom/client";
import { AppShell } from "./app/AppShell";
import "./i18n";

// a11y: axe-core dev overlay (strip in production build)
if (import.meta.env.DEV) {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const axe = await import("@axe-core/react");
  axe.default(React, ReactDOM, 1000);
}

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <AppShell />
  </React.StrictMode>
);
