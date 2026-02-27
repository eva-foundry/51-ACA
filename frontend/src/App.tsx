// EVA-STORY: ACA-05-010
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Suspense, lazy } from "react";
import { Spinner } from "@fluentui/react-components";
import { ConsentBanner } from "./components/ConsentBanner";

// Code-split each page for optimal bundle size
const Landing = lazy(() => import("./pages/Landing"));
const Login = lazy(() => import("./pages/Login"));
const Connect = lazy(() => import("./pages/Connect"));
const PreFlight = lazy(() => import("./pages/PreFlight"));
const ScanStatus = lazy(() => import("./pages/ScanStatus"));
const Findings = lazy(() => import("./pages/Findings"));
const Checkout = lazy(() => import("./pages/Checkout"));
const Download = lazy(() => import("./pages/Download"));
const BillingPortal = lazy(() => import("./pages/BillingPortal"));
const Admin = lazy(() => import("./pages/Admin"));

const fallback = (
  <div role="status" aria-label="Loading page">
    <Spinner label="Loading..." />
  </div>
);

export default function App() {
  return (
    <BrowserRouter>
      <ConsentBanner />
      <Suspense fallback={fallback}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/connect" element={<Connect />} />
          <Route path="/preflight" element={<PreFlight />} />
          <Route path="/scan/:scanId" element={<ScanStatus />} />
          <Route path="/findings/:scanId" element={<Findings />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/download/:deliverableId" element={<Download />} />
          <Route path="/billing" element={<BillingPortal />} />
          <Route path="/admin" element={<Admin />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
