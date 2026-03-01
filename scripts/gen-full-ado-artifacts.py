# scripts/gen-full-ado-artifacts.py
# Generates ado-artifacts.json from veritas-plan.json with all 257 ACA-NN-NNN stories as PBIs
# EVA-STORY: ACA-12-022
import json, pathlib, datetime

REPO = pathlib.Path(__file__).parent.parent
PLAN_FILE = REPO / ".eva" / "veritas-plan.json"
OUT_FILE  = REPO / "ado-artifacts.json"

EPIC_META = {
    "ACA-01": {"id_hint": "aca-foundation",    "tags": "aca;aca-foundation",    "title": "Foundation -- Repo Scaffold, Docker, CI, Health endpoints"},
    "ACA-02": {"id_hint": "aca-collection",    "tags": "aca;aca-collection",    "title": "Collection -- MSAL Auth, Resource Graph, Cost Management pull"},
    "ACA-03": {"id_hint": "aca-analysis",      "tags": "aca;aca-analysis",      "title": "Analysis -- 12-rule heuristic engine, FindingsAssembler"},
    "ACA-04": {"id_hint": "aca-api",           "tags": "aca;aca-api",           "title": "API -- FastAPI service: auth, collection, billing, admin, APIM"},
    "ACA-05": {"id_hint": "aca-frontend",      "tags": "aca;aca-frontend",      "title": "Frontend -- React 19, Fluent UI v9, 10 Spark screens"},
    "ACA-06": {"id_hint": "aca-billing",       "tags": "aca;aca-billing",       "title": "Billing -- Stripe Checkout, Webhook lifecycle, Entitlements"},
    "ACA-07": {"id_hint": "aca-delivery",      "tags": "aca;aca-delivery",      "title": "Delivery -- Jinja2 templates, ZIP packager, Blob SAS URLs"},
    "ACA-08": {"id_hint": "aca-observability", "tags": "aca;aca-observability", "title": "Observability -- App Insights, Log Analytics, GA4, Clarity"},
    "ACA-09": {"id_hint": "aca-i18n-a11y",     "tags": "aca;aca-i18n-a11y",     "title": "i18n and a11y -- 5 locales, multi-currency, WCAG 2.1 AA"},
    "ACA-10": {"id_hint": "aca-hardening",     "tags": "aca;aca-hardening",     "title": "Hardening -- APIM cache, rate limiting, idempotency, PIPEDA"},
    "ACA-11": {"id_hint": "aca-phase2-infra",  "tags": "aca;aca-phase2-infra",  "title": "Phase 2 Infra -- Terraform private landing zone, Lighthouse Mode C"},
    "ACA-12": {"id_hint": "aca-data-model",    "tags": "aca;aca-data-model",    "title": "Data Model -- ACA model server (port 8011), WBS tracking"},
    "ACA-13": {"id_hint": "aca-best-practices","tags": "aca;aca-best-practices","title": "Azure Best Practices -- Service catalog, IaC templates, 12 rules reference"},
    "ACA-14": {"id_hint": "aca-dpdca-agent",   "tags": "aca;aca-dpdca-agent",   "title": "DPDCA Cloud Agent -- GitHub Copilot agent story scaffolding"},
}

FEATURE_DESCS = {
    "aca-foundation":    "Mono-repo layout: services/api, collector, analysis, delivery, frontend. docker-compose, GitHub Actions CI, venv, requirements.txt, health/readiness endpoints, .env.example, data model server port 8011.",
    "aca-collection":    "Three connection modes: Mode A (delegated MSAL), Mode B (service principal), Mode C (Azure Lighthouse). Resource Graph inventory, Cost Management 91-day pull, Advisor recommendations pull, pre-flight verdict engine, CollectorJob ACA Job.",
    "aca-analysis":      "12 heuristic rules: idle VMs, orphaned disks, oversized SKUs, reserved instance opportunities, untagged resources, idle App Service Plans, over-provisioned Cosmos, unused Public IPs, legacy storage SKUs, unattached managed disks, dev/test licensing gaps, advisor score gaps. FindingsAssembler, AnalysisRun tracking, CAD savings estimates.",
    "aca-api":           "FastAPI routers: auth (connect/preflight/disconnect), collect (start/status), reports (tier1), billing (checkout/portal/stripe-webhook), entitlements (GET), admin (kpis/customers/grant/lock/reconcile/runs/audit). APIM entitlement cache policy (60s TTL). Pydantic models, Cosmos repos, JWT middleware.",
    "aca-frontend":      "Vite + React 19 + Fluent UI v9 + Spark design system. createBrowserRouter. RequireAuth + RequireRole guards. CustomerLayout + AdminLayout. 5 customer screens: Login, ConnectSubscription, CollectionStatus, FindingsTier1, Upgrade. 5 admin screens: Dashboard, Customers, Billing, Runs, Controls. WCAG 2.1 AA.",
    "aca-billing":       "Stripe Checkout sessions: Tier 2 one-time ($499 CAD), Tier 2 subscription ($150/mo), Tier 3 ($1499 CAD). Webhook handler. EntitlementService: grant, revoke, lock. PaymentsRepo + StripeCustomerMapRepo in Cosmos. Entitlement cache via APIM.",
    "aca-delivery":      "Delivery service: Jinja2 HTML/PDF templates for 12 finding types. ZIP packager (findings JSON + PDF + CSV). Blob Storage upload. 24-hour SAS URL generation. SHA-256 artifact verification. DeliveryJob ACA Job.",
    "aca-observability": "Structured JSON logging (structlog). Application Insights SDK. Log Analytics workspace. APIM usage metrics. GA4 event taxonomy (onboarding, collection, report, conversion funnel). Microsoft Clarity session replay. Consent Mode v2 (GTM). Privacy-first: no PII in analytics.",
    "aca-i18n-a11y":     "i18next 5 locales: en, fr-CA, pt-BR, es, de. Multi-currency: CAD, USD, BRL, EUR. ConsentBanner. WCAG 2.1 AA compliance. axe-core CI gate (zero violations on critical paths). aria-live regions for async status.",
    "aca-hardening":     "APIM entitlement cache (60s). Pre-flight caching. Rate limiting per subscription. Idempotency keys on POST endpoints. Webhook Stripe-Signature validation. PIPEDA soft-delete. Penetration testing checklist. CSP headers.",
    "aca-phase2-infra":  "Terraform private landing zone (VNET, Private Endpoints for Cosmos + Blob + APIM). Customer-managed VNET. Azure Lighthouse Mode C cross-tenant delegated access. BYO subscription onboarding wizard.",
    "aca-data-model":    "ACA-isolated data model: port 8011, SQLite, no Cosmos/Redis. 27 endpoints, 11 containers, 10 screens, 14 epics seeded. Veritas plan + trust score tracking. start.ps1 bootstrap. Separate from EVA POC data model (port 8010).",
    "aca-best-practices":"Azure Best Practices service catalog -- 12-category IaC template library, saving-opportunity-rules.md reference, Azure Advisor integration, rule scoring engine.",
    "aca-dpdca-agent":   "DPDCA Cloud Agent -- GitHub Copilot agent sprint scaffolding, ACA-METRICS commit trailer support, evidence receipt automation, parse-agent-log.py integration, ADO velocity dashboard wiring.",
}

def sprint_for(done: bool) -> str:
    return "51-aca\\Sprint-2" if done else "51-aca\\Sprint-Backlog"

def state_for(done: bool) -> str:
    return "Done" if done else "New"

def safe_acceptance(title: str, story_id: str) -> str:
    return f"[{story_id}] passes: implementation present, tests pass, EVA-STORY tag in source file."

plan = json.loads(PLAN_FILE.read_text(encoding="utf-8"))

features = []
user_stories = []
story_count = 0

for feat in plan["features"]:
    eid = feat["id"]
    meta = EPIC_META.get(eid)
    if not meta:
        print(f"[WARN] No meta for {eid} -- skipping")
        continue

    features.append({
        "id_hint": meta["id_hint"],
        "type": "Feature",
        "title": meta["title"],
        "description": FEATURE_DESCS.get(meta["id_hint"], meta["title"]),
        "tags": meta["tags"],
        "parent": "epic"
    })

    for story in feat["stories"]:
        sid    = story["id"]
        stitle = story.get("title", sid)
        done   = bool(story.get("done", False))
        # Truncate extremely long titles at 255 chars (ADO limit)
        full_title = f"[{sid}] {stitle}"
        if len(full_title) > 250:
            full_title = full_title[:247] + "..."

        user_stories.append({
            "id_hint": sid.lower().replace("-", ""),
            "type": "Product Backlog Item",
            "title": full_title,
            "acceptance_criteria": safe_acceptance(stitle, sid),
            "tags": f"aca;{meta['id_hint']};{sid.lower()}",
            "iteration_path": sprint_for(done),
            "state": state_for(done),
            "parent": meta["id_hint"],
            "evidence": {
                "story_id": sid,
                "done": done
            }
        })
        story_count += 1

artifact = {
    "schema_version": "1.1",
    "generated_at": datetime.datetime.utcnow().isoformat(),
    "generated_from": "veritas-plan.json",
    "ado_org": "https://dev.azure.com/marcopresta",
    "ado_project": "51-aca",
    "ado_process": "Scrum",
    "github_repo": "eva-foundry/51-ACA",
    "project_maturity": "active",
    "sprints_needed": [
        {"name": "Sprint-1",       "start_date": "2026-02-01", "finish_date": "2026-02-14"},
        {"name": "Sprint-2",       "start_date": "2026-02-15", "finish_date": "2026-02-28"},
        {"name": "Sprint-3",       "start_date": "2026-03-01", "finish_date": "2026-03-14"},
        {"name": "Sprint-Backlog", "start_date": "",           "finish_date": ""}
    ],
    "epic": {
        "skip_if_id_exists": None,
        "type": "Epic",
        "title": "Azure Cost Advisor (ACA) -- Phase 1 Commercial SaaS",
        "description": "Azure Cost Advisor is a commercial SaaS product that helps Azure subscribers discover and act on cost-saving opportunities. Customers connect their subscription (delegated, service principal, or Lighthouse), the platform runs a 12-rule heuristic analysis, and delivers tiered findings. Billing via Stripe. Stack: FastAPI + React 19 + Fluent UI v9 + Cosmos DB + Azure Container Apps + APIM + Stripe.",
        "tags": "aca;51-aca",
        "area_path": "51-aca"
    },
    "features": features,
    "user_stories": user_stories
}

OUT_FILE.write_text(json.dumps(artifact, indent=2, ensure_ascii=True), encoding="utf-8")
print(f"[PASS] Generated ado-artifacts.json")
print(f"  Features : {len(features)}")
print(f"  Stories  : {story_count}")
print(f"  Output   : {OUT_FILE}")
