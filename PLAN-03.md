# PLAN-03: Delivery, Observability, and Internationalization (Epics 7-9)

**Module**: PLAN-03  
**Epics**: 7 (Delivery), 8 (Observability), 9 (i18n/a11y)  
**Stories**: 44 total (9 + 14 + 21)  
**Function Points**: 220 (80 + 55 + 85)

---

## Epic 7: Delivery Packager (Tier 3)

**Goal**: Tier 3 deliverable ZIP generated, uploaded, SAS URL delivered (168-hour/7-day duration).  
**Status**: NOT STARTED  
**Stories**: 9  
**Function Points**: 80

**Key Decision**: Templates are Bicep only. Terraform is NOT included in delivery templates to keep Phase 1 simple. Generator skips missing main.tf gracefully (TemplateNotFound pass).

---

## Feature 7.1: IaC template library (Bicep Phase 1 only)

### Story ACA-07-001: Template folder structure
12 Jinja2 template folders exist in services/delivery/app/templates/ (one per deliverable_template_id from analysis rules). Folders: tmpl-devbox-autostop, tmpl-log-retention, tmpl-defender-plan, tmpl-compute-schedule, tmpl-anomaly-alert, tmpl-stale-envs, tmpl-search-sku, tmpl-acr-consolidation, tmpl-dns-consolidation, tmpl-savings-plan, tmpl-apim-token-budget, tmpl-chargeback-policy

**Acceptance**: 12 directories exist, each with template files

### Story ACA-07-002: Bicep templates implementation
Each folder has main.bicep and README.md (Bicep Phase 1 only; main.tf is deferred to Phase 2 / Epic 11)

**Acceptance**: Each template folder contains main.bicep + README.md

### Story ACA-07-003: Template parameterization
Templates are parameterized with scan_id, subscription_id, and finding fields

**Acceptance**: Templates use Jinja2 variables, render with scan context

### Story ACA-07-004: Template content sourcing
Template content sourced from 12-IaCscript.md patterns

**Acceptance**: Templates match content from docs/12-IaCscript.md examples

---

## Feature 7.2: Package and deliver

### Story ACA-07-005: IaC artifact generation
Delivery service generates all IaC artifacts for a scan's findings

**Acceptance**: Service reads findings, generates templates for each deliverable_template_id

### Story ACA-07-006: ZIP assembly with manifest
ZIP is assembled with findings.json manifest at root

**Acceptance**: ZIP contains findings.json + all generated templates

### Story ACA-07-007: SHA-256 signing
ZIP is signed with SHA-256 and the hash stored in the deliverables container

**Acceptance**: SHA-256 hash computed, stored in Cosmos deliverable record

### Story ACA-07-008: Azure Blob upload with 7-day SAS URL
ZIP is uploaded to Azure Blob Storage with 168h (7-day) SAS URL

**Acceptance**: Blob uploaded, SAS token expires after exactly 168 hours

### Story ACA-07-009: Deliverable record persistence
Deliverable record is written to Cosmos with sasUrl, sha256, artifactCount

**Acceptance**: deliverables container has record with all fields populated

---

## Epic 8: Observability and Telemetry

**Goal**: GA4, Clarity, App Insights all wired. Zero PII in any telemetry event.  
**Status**: PARTIAL  
**Stories**: 14  
**Function Points**: 55

---

## Feature 8.1: Frontend telemetry

### Story ACA-08-001: GTM container integration
GTM container is loaded in index.html with consent gating

**Acceptance**: GTM snippet loads conditionally based on consent state

### Story ACA-08-002: GA4 tag firing
GA4 tag fires after consent accepted

**Acceptance**: GA4 pageview events appear in real-time dashboard after consent

### Story ACA-08-003: Clarity tag firing
Clarity tag fires after consent accepted with form field masking ON

**Acceptance**: Clarity session recordings show masked form inputs

### Story ACA-08-004: Analytics event instrumentation
All 16 AnalyticsEventName events are fired at correct points in the UI

**Acceptance**: Events tracked: page_view, scan_start, scan_complete, tier_upgrade, checkout_initiated, checkout_completed, findings_viewed, download_deliverable, etc.

### Story ACA-08-005: Consent banner behavior
Consent banner allows accept/reject: rejected state suppresses all tags

**Acceptance**: Rejecting consent prevents all telemetry scripts from loading

### Story ACA-08-006: Consent persistence
Consent preference is respected across page reloads (localStorage)

**Acceptance**: Consent choice stored, respected on subsequent visits

---

## Feature 8.2: Backend observability

### Story ACA-08-007: App Insights connection
App Insights connection string is set in all Container Apps via KV reference

**Acceptance**: All services send logs to shared App Insights workspace

### Story ACA-08-008: Structured JSON logging
All service logs are structured JSON and appear in Azure Monitor

**Acceptance**: Logs queryable via KQL, include timestamp, level, component, message

### Story ACA-08-009: Custom metrics emission
Scan duration, analysis duration, delivery duration are emitted as custom metrics

**Acceptance**: Metrics visible in App Insights Metrics Explorer

### Story ACA-08-010: Error categorization
All API errors (4xx, 5xx) are logged with error_category enum (no raw messages)

**Acceptance**: Errors categorized: auth_failed, tier_required, resource_not_found, etc.

### Story ACA-08-011: Webhook event logging
Stripe webhook events are logged with event type + subscriptionId (hashed)

**Acceptance**: Webhook logs queryable, PII excluded (subscriptionId hashed)

---

## Feature 8.3: Alerting

### Story ACA-08-012: API error rate alert
Alert: API service 5xx rate > 5% in 5 minutes -> PagerDuty / email

**Acceptance**: Alert rule configured, triggers on threshold breach

### Story ACA-08-013: Collector failure alert
Alert: Collector job failure -> email + Cosmos audit record

**Acceptance**: Failed collector jobs trigger notification

### Story ACA-08-014: Anomaly detection alert
Alert: Anomaly detection rule fires -> owner notified (Story R-05 output)

**Acceptance**: R-05 findings trigger notification (email or webhook)

---

## Epic 9: i18n and a11y

**Goal**: All 5 locales live (EN, FR, PT-BR, ES, DE). WCAG 2.1 AA passing in axe-core CI gate.  
**Status**: IN PROGRESS  
**Stories**: 21  
**Function Points**: 85

---

## Feature 9.1: Internationalization (i18n)

### Story ACA-09-001: i18next configuration
i18next is configured with 5 locale namespaces in frontend/src/i18n/

**Acceptance**: i18next.ts config file exists, 5 namespaces registered

### Story ACA-09-002: String extraction
All user-visible strings are extracted to translation files (no hardcoded EN text)

**Acceptance**: Grep source for hardcoded strings returns zero UI text

### Story ACA-09-003: Language selector component
Language selector is visible in the nav with locale names in their own language: English, Français, Português (Brasil), Español, Deutsch

**Acceptance**: Dropdown shows all 5 locales, names in native language

### Story ACA-09-004: Locale persistence
Locale preference is persisted in localStorage

**Acceptance**: Selected locale remembered across sessions

### Story ACA-09-005: Date formatting
Date formats use Intl.DateTimeFormat -- locale-aware, no hardcoded format

**Acceptance**: Dates display in locale-specific format (MM/DD/YYYY vs DD/MM/YYYY)

### Story ACA-09-006: Number and currency formatting
Number/currency formats use Intl.NumberFormat with locale and currency options: CAD, USD, BRL, EUR supported on findings page saving estimates

**Acceptance**: Currency symbols and formatting match locale conventions

### Story ACA-09-007: French (Canadian) translation completion
fr (fr-CA) translations are completed before Phase 1 go-live (required for Canadian market)

**Acceptance**: All UI strings translated to French, reviewed by native speaker

### Story ACA-09-008: Additional locale translations
pt-BR, es, and de translations are completed before Phase 1 go-live as best-effort machine translation (DECISION LOCKED 2026-02-27: all 5 locales ship in Phase 1; professional review is Phase 2 hardening)

**Acceptance**: Translations exist for all 3 locales, flagged for review

### Story ACA-09-009: API error message localization
API error messages returned with Accept-Language header support for the 5 supported locales (error codes + localized message)

**Acceptance**: API inspects Accept-Language, returns localized error messages

### Story ACA-09-010: Stripe checkout locale
Stripe checkout locale is set from user preference

**Acceptance**: Stripe session locale matches user's selected language

---

## Feature 9.2: Accessibility (a11y) - WCAG 2.1 AA compliance

### Story ACA-09-011: axe-core CI gate
axe-core CI check runs on every PR -- zero critical or serious violations gate

**Acceptance**: Playwright + axe-core CI job blocks merge on violations

### Story ACA-09-012: Icon button labels
All icon-only buttons have aria-label in all 5 locales

**Acceptance**: Every icon button has descriptive aria-label attribute

### Story ACA-09-013: Form field labels
All form fields have associated <label> elements (no placeholder-as-label)

**Acceptance**: Labels correctly associated via htmlFor or wrapping

### Story ACA-09-014: Table semantics
Findings table has proper <th scope="col"> headers

**Acceptance**: Table headers marked with scope attribute for screen readers

### Story ACA-09-015: Status indicators accessibility
PreFlight status indicators use both colour and icon/text (not colour-only)

**Acceptance**: PASS/FAIL/WARN indicated by color + icon + text label

### Story ACA-09-016: Color contrast compliance
Colour contrast ratio >= 4.5:1 for all body text (verified in Figma + axe)

**Acceptance**: All text meets WCAG AA contrast requirements

### Story ACA-09-017: Focus ring visibility
Focus ring is visible and high-contrast on all focusable elements

**Acceptance**: Keyboard focus clearly visible on all interactive elements

### Story ACA-09-018: Skip to content link
Skip-to-content link is the first focusable element on every page

**Acceptance**: Link visible on tab focus, jumps to main content

### Story ACA-09-019: Consent banner accessibility
Consent banner is keyboard-accessible and screen-reader-labelled

**Acceptance**: Banner navigable via keyboard, ARIA labels present

### Story ACA-09-020: Keyboard-only flow verification
Keyboard-only walkthrough of the full Tier 1 flow passes before M1.4 sign-off

**Acceptance**: Complete flow (login → connect → scan → findings → upgrade) navigable via keyboard only

### Story ACA-09-021: Playwright accessibility tests
Playwright headless tests cover the Tier 1 customer flow with axe-core assertions. Target: 95% end-to-end coverage. CI gate blocks on failure. All 5 locales exercised in Playwright suite. Runs on ubuntu-latest headless.

**Acceptance**: Test suite runs in CI, tests all 5 locales, blocks on axe violations

---

**End of PLAN-03** -- Continue to [PLAN-04.md](PLAN-04.md) for Epics 10-12
