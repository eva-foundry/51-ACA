```bash

\#!/usr/bin/env bash

\# ==============================================================================

\# ACA Infrastructure Bootstrap (az cli) — Phase 1 (marco\* sandbox reuse) AND

\# Phase 2 (new subscription / new RG).

\#

\# Single-file runner: set MODE=phase1 or MODE=phase2 and fill variables below.

\#

\# Phase 1 goal: reuse existing marco\* resources in EsDAICoE-Sandbox (no provisioning

\# required except ACA-specific Cosmos DB containers / secrets) :contentReference\[oaicite:0]{index=0}

\#

\# Marco\* inventory snapshot (resources exist in EsDAICoE-Sandbox):

\# - marco-sandbox-cosmos (Cosmos DB)

\# - marcosandkv20260203 (Key Vault)

\# - marcosandacr20260203 (ACR)

\# - marco-sandbox-apim (APIM)

\# - marco-sandbox-appinsights (AppInsights)

\# - etc. :contentReference\[oaicite:1]{index=1} :contentReference\[oaicite:2]{index=2}

\#

\# Phase 2 goal: provision a clean private subscription + RG for commercial MVP

\# (Container Apps, Cosmos, APIM, Key Vault, Storage, AppInsights/Logs, etc.). :contentReference\[oaicite:3]{index=3}

\#

\# NOTE:

\# - This script assumes you already have az cli installed and you are logged in:

\#     az login

\# - Some org environments restrict creating certain resources (OpenAI, APIM tiers, etc.).

\#   The script is written to be safe: it checks existence before creating.

\# ==============================================================================



set -euo pipefail



\# ------------------------------------------------------------------------------

\# REQUIRED SETTINGS (edit these)

\# ------------------------------------------------------------------------------

MODE="${MODE:-phase1}"  # phase1 | phase2



\# Phase 1 (marco\* reuse) target

PHASE1\_SUBSCRIPTION\_ID="${PHASE1\_SUBSCRIPTION\_ID:-d2d4e571-e0f2-4f6c-901a-f88f7669bcba}"   # from inventory tags/links :contentReference\[oaicite:4]{index=4}

PHASE1\_RG="${PHASE1\_RG:-EsDAICoE-Sandbox}"

PHASE1\_COSMOS\_ACCOUNT="${PHASE1\_COSMOS\_ACCOUNT:-marco-sandbox-cosmos}"                     # exists :contentReference\[oaicite:5]{index=5}

PHASE1\_KV\_NAME="${PHASE1\_KV\_NAME:-marcosandkv20260203}"                                    # exists :contentReference\[oaicite:6]{index=6}

PHASE1\_LOC="${PHASE1\_LOC:-canadacentral}"



\# Phase 2 (new subscription) target

PHASE2\_SUBSCRIPTION\_ID="${PHASE2\_SUBSCRIPTION\_ID:-}"     # set me (private ACA sub)

PHASE2\_RG="${PHASE2\_RG:-aca-prod-rg}"

PHASE2\_LOC="${PHASE2\_LOC:-canadacentral}"

PHASE2\_COSMOS\_ACCOUNT="${PHASE2\_COSMOS\_ACCOUNT:-aca-cosmos-$(date +%y%m%d%H%M)}"  # must be globally unique (lowercase, 3-44)

PHASE2\_KV\_NAME="${PHASE2\_KV\_NAME:-aca-kv-$(date +%y%m%d%H%M)}"                    # must be globally unique

PHASE2\_STORAGE="${PHASE2\_STORAGE:-acastorage$(date +%y%m%d%H%M)}"                 # must be globally unique (lowercase, 3-24)

PHASE2\_ACR\_NAME="${PHASE2\_ACR\_NAME:-acaacr$(date +%y%m%d%H%M)}"                   # must be globally unique

PHASE2\_APPINSIGHTS\_NAME="${PHASE2\_APPINSIGHTS\_NAME:-aca-appinsights}"

PHASE2\_LOGS\_NAME="${PHASE2\_LOGS\_NAME:-aca-logs}"



\# ACA Cosmos database name (shared across phase1/phase2)

COSMOS\_DB\_NAME="${COSMOS\_DB\_NAME:-aca}"



\# ------------------------------------------------------------------------------

\# ACA Containers (PK strategy)

\# ------------------------------------------------------------------------------

\# Tenant-scoped: PK=/subscriptionId (matches ACA design) :contentReference\[oaicite:7]{index=7}

C\_SCANS="scans"

C\_INVENTORIES="inventories"

C\_COSTDATA="cost-data"

C\_ADVISOR="advisor"

C\_FINDINGS="findings"



\# Billing/Entitlements (from your Stripe + gating work)

C\_ENTITLEMENTS="entitlements"                 # PK=/subscriptionId

C\_PAYMENTS="payments"                         # PK=/subscriptionId

C\_CLIENTS="clients"                           # PK=/subscriptionId

C\_STRIPE\_MAP="stripe\_customer\_map"            # PK=/stripeCustomerId (webhook O(1) lookup)



\# Throughput (RU/s). Adjust as needed.

RU\_DB="${RU\_DB:-400}"

RU\_CONTAINER="${RU\_CONTAINER:-400}"



\# ------------------------------------------------------------------------------

\# Helpers

\# ------------------------------------------------------------------------------

need() { command -v "$1" >/dev/null 2>\&1 || { echo "ERROR: missing dependency: $1"; exit 1; }; }



az\_set\_sub() {

&nbsp; local sub="$1"

&nbsp; if \[\[ -z "$sub" ]]; then

&nbsp;   echo "ERROR: subscription id is empty"; exit 1

&nbsp; fi

&nbsp; az account set --subscription "$sub" >/dev/null

}



exists\_rg() {

&nbsp; local rg="$1"

&nbsp; az group exists -n "$rg" | grep -qi true

}



exists\_kv() {

&nbsp; local rg="$1" kv="$2"

&nbsp; az keyvault show -g "$rg" -n "$kv" >/dev/null 2>\&1

}



exists\_cosmos() {

&nbsp; local rg="$1" acct="$2"

&nbsp; az cosmosdb show -g "$rg" -n "$acct" >/dev/null 2>\&1

}



exists\_cosmos\_db() {

&nbsp; local rg="$1" acct="$2" db="$3"

&nbsp; az cosmosdb sql database show -g "$rg" -a "$acct" -n "$db" >/dev/null 2>\&1

}



exists\_container() {

&nbsp; local rg="$1" acct="$2" db="$3" c="$4"

&nbsp; az cosmosdb sql container show -g "$rg" -a "$acct" -d "$db" -n "$c" >/dev/null 2>\&1

}



create\_rg\_if\_missing() {

&nbsp; local rg="$1" loc="$2"

&nbsp; if exists\_rg "$rg"; then

&nbsp;   echo "OK: RG exists: $rg"

&nbsp; else

&nbsp;   echo "CREATE: RG $rg ($loc)"

&nbsp;   az group create -n "$rg" -l "$loc" >/dev/null

&nbsp; fi

}



create\_kv\_if\_missing() {

&nbsp; local rg="$1" kv="$2" loc="$3"

&nbsp; if exists\_kv "$rg" "$kv"; then

&nbsp;   echo "OK: Key Vault exists: $kv"

&nbsp; else

&nbsp;   echo "CREATE: Key Vault $kv"

&nbsp;   # Using RBAC auth is recommended for production, but vaults may be policy-based in some orgs.

&nbsp;   # This creates a vault; you can later switch/access model based on your tenant rules.

&nbsp;   az keyvault create -g "$rg" -n "$kv" -l "$loc" >/dev/null

&nbsp; fi

}



create\_cosmos\_if\_missing() {

&nbsp; local rg="$1" acct="$2" loc="$3"

&nbsp; if exists\_cosmos "$rg" "$acct"; then

&nbsp;   echo "OK: Cosmos account exists: $acct"

&nbsp; else

&nbsp;   echo "CREATE: Cosmos account $acct"

&nbsp;   az cosmosdb create \\

&nbsp;     -g "$rg" -n "$acct" \\

&nbsp;     --locations regionName="$loc" failoverPriority=0 isZoneRedundant=false \\

&nbsp;     --default-consistency-level "Session" \\

&nbsp;     --enable-free-tier true \\

&nbsp;     --backup-policy-type "Periodic" \\

&nbsp;     --backup-interval 240 \\

&nbsp;     --backup-retention 8 >/dev/null

&nbsp; fi

}



create\_cosmos\_db\_if\_missing() {

&nbsp; local rg="$1" acct="$2" db="$3" ru="$4"

&nbsp; if exists\_cosmos\_db "$rg" "$acct" "$db"; then

&nbsp;   echo "OK: Cosmos DB exists: $db"

&nbsp; else

&nbsp;   echo "CREATE: Cosmos DB: $db (RU=$ru)"

&nbsp;   az cosmosdb sql database create -g "$rg" -a "$acct" -n "$db" --throughput "$ru" >/dev/null

&nbsp; fi

}



create\_container\_if\_missing() {

&nbsp; local rg="$1" acct="$2" db="$3" c="$4" pk="$5" ru="$6"

&nbsp; if exists\_container "$rg" "$acct" "$db" "$c"; then

&nbsp;   echo "OK: Container exists: $c"

&nbsp; else

&nbsp;   echo "CREATE: Container $c (PK=$pk RU=$ru)"

&nbsp;   az cosmosdb sql container create \\

&nbsp;     -g "$rg" -a "$acct" -d "$db" -n "$c" \\

&nbsp;     -p "$pk" \\

&nbsp;     --throughput "$ru" >/dev/null

&nbsp; fi

}



kv\_set\_secret\_if\_value() {

&nbsp; local kv="$1" name="$2" value="${3:-}"

&nbsp; if \[\[ -z "$value" ]]; then

&nbsp;   echo "SKIP: secret $name (no value provided)"

&nbsp;   return 0

&nbsp; fi

&nbsp; echo "SET: KeyVault secret $name"

&nbsp; az keyvault secret set --vault-name "$kv" --name "$name" --value "$value" >/dev/null

}



\# ------------------------------------------------------------------------------

\# Phase 1: marco\* reuse

\# ------------------------------------------------------------------------------

phase1() {

&nbsp; echo "========================"

&nbsp; echo "PHASE 1 — marco\* reuse"

&nbsp; echo "========================"

&nbsp; echo "Target RG:  $PHASE1\_RG"

&nbsp; echo "Cosmos:     $PHASE1\_COSMOS\_ACCOUNT"

&nbsp; echo "Key Vault:  $PHASE1\_KV\_NAME"

&nbsp; echo



&nbsp; az\_set\_sub "$PHASE1\_SUBSCRIPTION\_ID"



&nbsp; # Validate expected existing infra (from inventory)

&nbsp; if ! exists\_rg "$PHASE1\_RG"; then

&nbsp;   echo "ERROR: Phase1 RG not found: $PHASE1\_RG (expected per inventory)"; exit 1

&nbsp; fi

&nbsp; if ! exists\_cosmos "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT"; then

&nbsp;   echo "ERROR: Phase1 Cosmos not found: $PHASE1\_COSMOS\_ACCOUNT (expected)"; exit 1

&nbsp; fi

&nbsp; if ! exists\_kv "$PHASE1\_RG" "$PHASE1\_KV\_NAME"; then

&nbsp;   echo "ERROR: Phase1 KeyVault not found: $PHASE1\_KV\_NAME (expected)"; exit 1

&nbsp; fi



&nbsp; # Ensure ACA DB + containers exist inside marco-sandbox-cosmos

&nbsp; create\_cosmos\_db\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$RU\_DB"



&nbsp; # Core ACA data containers (PK=/subscriptionId)

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_SCANS"       "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_INVENTORIES" "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_COSTDATA"    "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_ADVISOR"     "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_FINDINGS"    "/subscriptionId" "$RU\_CONTAINER"



&nbsp; # Billing/entitlements containers

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_ENTITLEMENTS" "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_PAYMENTS"     "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_CLIENTS"      "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_STRIPE\_MAP"   "/stripeCustomerId" "$RU\_CONTAINER"



&nbsp; echo

&nbsp; echo "DONE: Phase 1 Cosmos schema is ready in marco-sandbox-cosmos."

&nbsp; echo "Next: seed Key Vault secrets (optional in Phase 1, required Phase 2)."

&nbsp; echo

&nbsp; echo "To seed secrets, export env vars then re-run this script:"

&nbsp; echo "  export STRIPE\_SECRET\_KEY=..."

&nbsp; echo "  export STRIPE\_WEBHOOK\_SECRET=..."

&nbsp; echo "  export STRIPE\_PRICE\_TIER2\_ONE\_TIME=..."

&nbsp; echo "  export STRIPE\_PRICE\_TIER2\_SUBSCRIPTION=..."

&nbsp; echo "  export STRIPE\_PRICE\_TIER3\_ONE\_TIME=..."

&nbsp; echo "  export PUBLIC\_APP\_URL=https://..."

&nbsp; echo "  export PUBLIC\_API\_URL=https://..."

&nbsp; echo "  export COSMOS\_ENDPOINT=https://...documents.azure.com:443/"

&nbsp; echo "  export COSMOS\_KEY=..."

&nbsp; echo



&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "STRIPE\_SECRET\_KEY" "${STRIPE\_SECRET\_KEY:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "STRIPE\_WEBHOOK\_SECRET" "${STRIPE\_WEBHOOK\_SECRET:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "STRIPE\_PRICE\_TIER2\_ONE\_TIME" "${STRIPE\_PRICE\_TIER2\_ONE\_TIME:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "STRIPE\_PRICE\_TIER2\_SUBSCRIPTION" "${STRIPE\_PRICE\_TIER2\_SUBSCRIPTION:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "STRIPE\_PRICE\_TIER3\_ONE\_TIME" "${STRIPE\_PRICE\_TIER3\_ONE\_TIME:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "PUBLIC\_APP\_URL" "${PUBLIC\_APP\_URL:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "PUBLIC\_API\_URL" "${PUBLIC\_API\_URL:-}"



&nbsp; # Cosmos connection (if you want to store these in KV too)

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "COSMOS\_ENDPOINT" "${COSMOS\_ENDPOINT:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "COSMOS\_KEY" "${COSMOS\_KEY:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE1\_KV\_NAME" "COSMOS\_DB\_NAME" "$COSMOS\_DB\_NAME"



&nbsp; echo

&nbsp; echo "OK: Phase 1 complete."

&nbsp; echo "Reminder: Phase 1 is explicitly 'Developer Go-Live on marco\* Infrastructure' :contentReference\[oaicite:8]{index=8}"

}



\# ------------------------------------------------------------------------------

\# Phase 2: new subscription + new RG (commercial MVP)

\# ------------------------------------------------------------------------------

phase2() {

&nbsp; echo "=========================================="

&nbsp; echo "PHASE 2 — new subscription + new RG"

&nbsp; echo "=========================================="

&nbsp; if \[\[ -z "$PHASE2\_SUBSCRIPTION\_ID" ]]; then

&nbsp;   echo "ERROR: PHASE2\_SUBSCRIPTION\_ID is required for phase2"; exit 1

&nbsp; fi



&nbsp; az\_set\_sub "$PHASE2\_SUBSCRIPTION\_ID"



&nbsp; create\_rg\_if\_missing "$PHASE2\_RG" "$PHASE2\_LOC"



&nbsp; # Cosmos + DB + containers

&nbsp; create\_cosmos\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$PHASE2\_LOC"

&nbsp; create\_cosmos\_db\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$RU\_DB"



&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_SCANS"        "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_INVENTORIES"  "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_COSTDATA"     "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_ADVISOR"      "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_FINDINGS"     "/subscriptionId" "$RU\_CONTAINER"



&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_ENTITLEMENTS" "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_PAYMENTS"     "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_CLIENTS"      "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$COSMOS\_DB\_NAME" "$C\_STRIPE\_MAP"   "/stripeCustomerId" "$RU\_CONTAINER"



&nbsp; # Key Vault

&nbsp; create\_kv\_if\_missing "$PHASE2\_RG" "$PHASE2\_KV\_NAME" "$PHASE2\_LOC"



&nbsp; # Storage (for Tier 3 zip packages + any landing zones)

&nbsp; if az storage account show -g "$PHASE2\_RG" -n "$PHASE2\_STORAGE" >/dev/null 2>\&1; then

&nbsp;   echo "OK: Storage exists: $PHASE2\_STORAGE"

&nbsp; else

&nbsp;   echo "CREATE: Storage $PHASE2\_STORAGE (RA-GRS recommended for prod; using Standard\_RAGRS)"

&nbsp;   az storage account create \\

&nbsp;     -g "$PHASE2\_RG" -n "$PHASE2\_STORAGE" -l "$PHASE2\_LOC" \\

&nbsp;     --sku Standard\_RAGRS --kind StorageV2 \\

&nbsp;     --https-only true \\

&nbsp;     --allow-blob-public-access false >/dev/null

&nbsp; fi



&nbsp; # ACR (optional but typical for runtime; GHCR can still be build registry)

&nbsp; if az acr show -g "$PHASE2\_RG" -n "$PHASE2\_ACR\_NAME" >/dev/null 2>\&1; then

&nbsp;   echo "OK: ACR exists: $PHASE2\_ACR\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: ACR $PHASE2\_ACR\_NAME (Standard recommended for prod; using Standard)"

&nbsp;   az acr create -g "$PHASE2\_RG" -n "$PHASE2\_ACR\_NAME" -l "$PHASE2\_LOC" --sku Standard >/dev/null

&nbsp; fi



&nbsp; # Log Analytics + App Insights (classic pattern)

&nbsp; if az monitor log-analytics workspace show -g "$PHASE2\_RG" -n "$PHASE2\_LOGS\_NAME" >/dev/null 2>\&1; then

&nbsp;   echo "OK: Log Analytics workspace exists: $PHASE2\_LOGS\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: Log Analytics workspace $PHASE2\_LOGS\_NAME"

&nbsp;   az monitor log-analytics workspace create -g "$PHASE2\_RG" -n "$PHASE2\_LOGS\_NAME" -l "$PHASE2\_LOC" >/dev/null

&nbsp; fi



&nbsp; # App Insights (workspace-based)

&nbsp; if az monitor app-insights component show -g "$PHASE2\_RG" -a "$PHASE2\_APPINSIGHTS\_NAME" >/dev/null 2>\&1; then

&nbsp;   echo "OK: App Insights exists: $PHASE2\_APPINSIGHTS\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: App Insights $PHASE2\_APPINSIGHTS\_NAME (workspace-based)"

&nbsp;   WORKSPACE\_ID="$(az monitor log-analytics workspace show -g "$PHASE2\_RG" -n "$PHASE2\_LOGS\_NAME" --query id -o tsv)"

&nbsp;   az monitor app-insights component create \\

&nbsp;     -g "$PHASE2\_RG" -a "$PHASE2\_APPINSIGHTS\_NAME" -l "$PHASE2\_LOC" \\

&nbsp;     --kind web \\

&nbsp;     --workspace "$WORKSPACE\_ID" >/dev/null

&nbsp; fi



&nbsp; # Cosmos endpoint/key -> store in KV (recommended)

&nbsp; COSMOS\_ENDPOINT\_ACTUAL="$(az cosmosdb show -g "$PHASE2\_RG" -n "$PHASE2\_COSMOS\_ACCOUNT" --query documentEndpoint -o tsv)"

&nbsp; COSMOS\_KEY\_ACTUAL="$(az cosmosdb keys list -g "$PHASE2\_RG" -n "$PHASE2\_COSMOS\_ACCOUNT" --type keys --query primaryMasterKey -o tsv)"



&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "COSMOS\_ENDPOINT" "$COSMOS\_ENDPOINT\_ACTUAL"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "COSMOS\_KEY" "$COSMOS\_KEY\_ACTUAL"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "COSMOS\_DB\_NAME" "$COSMOS\_DB\_NAME"



&nbsp; # Stripe + public URLs (you can export env vars before running)

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "STRIPE\_SECRET\_KEY" "${STRIPE\_SECRET\_KEY:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "STRIPE\_WEBHOOK\_SECRET" "${STRIPE\_WEBHOOK\_SECRET:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "STRIPE\_PRICE\_TIER2\_ONE\_TIME" "${STRIPE\_PRICE\_TIER2\_ONE\_TIME:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "STRIPE\_PRICE\_TIER2\_SUBSCRIPTION" "${STRIPE\_PRICE\_TIER2\_SUBSCRIPTION:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "STRIPE\_PRICE\_TIER3\_ONE\_TIME" "${STRIPE\_PRICE\_TIER3\_ONE\_TIME:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "PUBLIC\_APP\_URL" "${PUBLIC\_APP\_URL:-}"

&nbsp; kv\_set\_secret\_if\_value "$PHASE2\_KV\_NAME" "PUBLIC\_API\_URL" "${PUBLIC\_API\_URL:-}"



&nbsp; echo

&nbsp; echo "DONE: Phase 2 core infra provisioned (Cosmos+containers, KV, Storage, ACR, Logs, AppInsights)."

&nbsp; echo "This aligns with 'Commercial MVP on Private Azure Subscription' objective :contentReference\[oaicite:9]{index=9}"

&nbsp; echo

&nbsp; echo "NEXT (intentionally NOT auto-created here, since org policies vary):"

&nbsp; echo "  - APIM (Developer/Standard), policies for tier gating + caching (you already have patterns)"

&nbsp; echo "  - Container Apps Environment + apps/jobs (aca-api, aca-collector, aca-analysis, aca-delivery) :contentReference\[oaicite:10]{index=10}"

&nbsp; echo "  - Azure OpenAI / Foundry resources (availability + approvals vary)"

&nbsp; echo "  - GitHub OIDC federated identity to this subscription (no stored creds) :contentReference\[oaicite:11]{index=11}"

}



\# ------------------------------------------------------------------------------

\# Entry

\# ------------------------------------------------------------------------------

need az

need bash



case "$MODE" in

&nbsp; phase1) phase1 ;;

&nbsp; phase2) phase2 ;;

&nbsp; \*)

&nbsp;   echo "ERROR: MODE must be phase1 or phase2. Got: $MODE"

&nbsp;   exit 1

&nbsp;   ;;

esac

```



This single script matches your plan to \*\*start on existing marco\*\*\* infra in \*\*EsDAICoE-Sandbox\*\*  and later \*\*move cleanly to a new subscription/RG for commercial MVP\*\* .



If you want, I can extend this same file to also:



\* create \*\*Container Apps Environment + container apps/jobs\*\* (FastAPI + 3 workers),

\* create \*\*APIM\*\* and import the API spec + apply the \*\*tier-gating + entitlements caching\*\* policies,

\* create a \*\*User Assigned Managed Identity\*\* and wire it to Key Vault + Cosmos RBAC.



