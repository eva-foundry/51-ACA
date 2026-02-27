/**
 * AppShell -- root component for ACA.
 * Wraps FluentProvider + ConsentBanner + RouterProvider.
 * Replaces the BrowserRouter+Routes pattern in the old App.tsx.
 */

import { RouterProvider } from "react-router-dom";
import {
  FluentProvider,
  webLightTheme,
} from "@fluentui/react-components";
import { Suspense } from "react";
import { router } from "./routes/router";
import { ConsentBanner } from "../components/ConsentBanner";
import { Loading } from "./components/Loading";

export function AppShell() {
  return (
    <FluentProvider theme={webLightTheme}>
      {/* Skip to main content -- a11y */}
      <a
        href="#main-content"
        className="skip-link"
        style={{
          position: "absolute",
          top: -40,
          left: 0,
          background: "#0078d4",
          color: "#fff",
          padding: "8px 12px",
          zIndex: 9999,
          transition: "top 0.1s",
        }}
        onFocus={(e) => {
          (e.currentTarget as HTMLAnchorElement).style.top = "0";
        }}
        onBlur={(e) => {
          (e.currentTarget as HTMLAnchorElement).style.top = "-40px";
        }}
      >
        Skip to main content
      </a>

      <ConsentBanner />

      <Suspense fallback={<Loading label="Loading ACA..." />}>
        <RouterProvider router={router} />
      </Suspense>
    </FluentProvider>
  );
}
