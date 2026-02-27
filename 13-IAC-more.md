```bash

\#!/usr/bin/env bash

\# ==============================================================================

\# ACA Infrastructure Bootstrap (az cli) — Single File

\# Phase 1: reuse marco\* resources in EsDAICoE-Sandbox RG (dev sandbox)

\# Phase 2: provision new subscription + RG (commercial MVP)

\#

\# NOW INCLUDES:

\# - Cosmos DB + containers

\# - Key Vault secrets

\# - Managed Identity (UAMI) + Key Vault RBAC wiring

\# - Container Apps Environment + ACA API Container App

\# - Container Apps Jobs: collector / analysis / delivery

\# - (Optional) APIM creation + API import + policy placeholders

\#

\# Usage:

\#   MODE=phase1 ./aca-bootstrap.sh

\#   MODE=phase2 PHASE2\_SUBSCRIPTION\_ID=<sub> ./aca-bootstrap.sh

\#

\# Optional toggles:

\#   DO\_CONTAINERAPPS=true|false   (default true)

\#   DO\_APIM=true|false            (default false)

\#   USE\_ACR=true|false            (default true; if false, use GHCR public images)

\#

\# Images (required if DO\_CONTAINERAPPS=true):

\#   API\_IMAGE, COLLECTOR\_IMAGE, ANALYSIS\_IMAGE, DELIVERY\_IMAGE

\#   - If USE\_ACR=true: images should be in your ACR: <acr>.azurecr.io/<repo>:<tag>

\#   - If USE\_ACR=false: use ghcr.io/<org>/<repo>:<tag> (public) or other registry

\#

\# NOTE: Cosmos RBAC (data-plane) is optional and org-dependent; this script wires

\#       MI->KeyVault by default and uses Cosmos KEY from Key Vault for runtime.

\#       A Cosmos RBAC optional block is provided.

\# ==============================================================================



set -euo pipefail



\# ------------------------------------------------------------------------------

\# REQUIRED SETTINGS (edit these)

\# ------------------------------------------------------------------------------

MODE="${MODE:-phase1}"  # phase1 | phase2



DO\_CONTAINERAPPS="${DO\_CONTAINERAPPS:-true}"

DO\_APIM="${DO\_APIM:-false}"

USE\_ACR="${USE\_ACR:-true}"



\# Phase 1 (marco\* reuse) target

PHASE1\_SUBSCRIPTION\_ID="${PHASE1\_SUBSCRIPTION\_ID:-d2d4e571-e0f2-4f6c-901a-f88f7669bcba}"

PHASE1\_RG="${PHASE1\_RG:-EsDAICoE-Sandbox}"

PHASE1\_COSMOS\_ACCOUNT="${PHASE1\_COSMOS\_ACCOUNT:-marco-sandbox-cosmos}"

PHASE1\_KV\_NAME="${PHASE1\_KV\_NAME:-marcosandkv20260203}"

PHASE1\_ACR\_NAME="${PHASE1\_ACR\_NAME:-marcosandacr20260203}"

PHASE1\_LOC="${PHASE1\_LOC:-canadacentral}"



\# Phase 2 (new subscription) target

PHASE2\_SUBSCRIPTION\_ID="${PHASE2\_SUBSCRIPTION\_ID:-}"     # required for phase2

PHASE2\_RG="${PHASE2\_RG:-aca-prod-rg}"

PHASE2\_LOC="${PHASE2\_LOC:-canadacentral}"

PHASE2\_COSMOS\_ACCOUNT="${PHASE2\_COSMOS\_ACCOUNT:-aca-cosmos-$(date +%y%m%d%H%M)}"

PHASE2\_KV\_NAME="${PHASE2\_KV\_NAME:-aca-kv-$(date +%y%m%d%H%M)}"

PHASE2\_STORAGE="${PHASE2\_STORAGE:-acastorage$(date +%y%m%d%H%M)}"

PHASE2\_ACR\_NAME="${PHASE2\_ACR\_NAME:-acaacr$(date +%y%m%d%H%M)}"

PHASE2\_LOGS\_NAME="${PHASE2\_LOGS\_NAME:-aca-logs}"

PHASE2\_APPINSIGHTS\_NAME="${PHASE2\_APPINSIGHTS\_NAME:-aca-appinsights}"



\# ACA shared

COSMOS\_DB\_NAME="${COSMOS\_DB\_NAME:-aca}"



\# Cosmos containers

C\_SCANS="scans"

C\_INVENTORIES="inventories"

C\_COSTDATA="cost-data"

C\_ADVISOR="advisor"

C\_FINDINGS="findings"

C\_ENTITLEMENTS="entitlements"

C\_PAYMENTS="payments"

C\_CLIENTS="clients"

C\_STRIPE\_MAP="stripe\_customer\_map"            # PK=/stripeCustomerId



\# RU/s

RU\_DB="${RU\_DB:-400}"

RU\_CONTAINER="${RU\_CONTAINER:-400}"



\# Managed Identity + Container Apps naming

UAMI\_NAME="${UAMI\_NAME:-aca-uami}"

CA\_ENV\_NAME="${CA\_ENV\_NAME:-aca-ca-env}"

CA\_API\_NAME="${CA\_API\_NAME:-aca-api}"

CA\_COLLECTOR\_JOB="${CA\_COLLECTOR\_JOB:-aca-collector}"

CA\_ANALYSIS\_JOB="${CA\_ANALYSIS\_JOB:-aca-analysis}"

CA\_DELIVERY\_JOB="${CA\_DELIVERY\_JOB:-aca-delivery}"



\# Container Apps ingress

API\_INGRESS\_EXTERNAL="${API\_INGRESS\_EXTERNAL:-true}"  # true|false

API\_INGRESS\_PORT="${API\_INGRESS\_PORT:-8080}"



\# Images (required if DO\_CONTAINERAPPS=true)

API\_IMAGE="${API\_IMAGE:-}"

COLLECTOR\_IMAGE="${COLLECTOR\_IMAGE:-}"

ANALYSIS\_IMAGE="${ANALYSIS\_IMAGE:-}"

DELIVERY\_IMAGE="${DELIVERY\_IMAGE:-}"



\# Stripe + URLs (export before run OR set later; script stores them in KV if provided)

STRIPE\_SECRET\_KEY="${STRIPE\_SECRET\_KEY:-}"

STRIPE\_WEBHOOK\_SECRET="${STRIPE\_WEBHOOK\_SECRET:-}"

STRIPE\_PRICE\_TIER2\_ONE\_TIME="${STRIPE\_PRICE\_TIER2\_ONE\_TIME:-}"

STRIPE\_PRICE\_TIER2\_SUBSCRIPTION="${STRIPE\_PRICE\_TIER2\_SUBSCRIPTION:-}"

STRIPE\_PRICE\_TIER3\_ONE\_TIME="${STRIPE\_PRICE\_TIER3\_ONE\_TIME:-}"

PUBLIC\_APP\_URL="${PUBLIC\_APP\_URL:-}"

PUBLIC\_API\_URL="${PUBLIC\_API\_URL:-}"



\# Optional: API auth secrets (placeholders)

ENTRA\_TENANT\_ID="${ENTRA\_TENANT\_ID:-}"

ENTRA\_AUDIENCE="${ENTRA\_AUDIENCE:-}"



\# ------------------------------------------------------------------------------

\# Helpers

\# ------------------------------------------------------------------------------

need() { command -v "$1" >/dev/null 2>\&1 || { echo "ERROR: missing dependency: $1"; exit 1; }; }



az\_set\_sub() {

&nbsp; local sub="$1"

&nbsp; \[\[ -n "$sub" ]] || { echo "ERROR: subscription id is empty"; exit 1; }

&nbsp; az account set --subscription "$sub" >/dev/null

}



exists\_rg() { az group exists -n "$1" | grep -qi true; }



exists\_kv() { az keyvault show -g "$1" -n "$2" >/dev/null 2>\&1; }

exists\_cosmos() { az cosmosdb show -g "$1" -n "$2" >/dev/null 2>\&1; }

exists\_acr() { az acr show -g "$1" -n "$2" >/dev/null 2>\&1; }



exists\_cosmos\_db() { az cosmosdb sql database show -g "$1" -a "$2" -n "$3" >/dev/null 2>\&1; }

exists\_container() { az cosmosdb sql container show -g "$1" -a "$2" -d "$3" -n "$4" >/dev/null 2>\&1; }



exists\_uami() { az identity show -g "$1" -n "$2" >/dev/null 2>\&1; }

exists\_ca\_env() { az containerapp env show -g "$1" -n "$2" >/dev/null 2>\&1; }

exists\_ca\_app() { az containerapp show -g "$1" -n "$2" >/dev/null 2>\&1; }

exists\_ca\_job() { az containerapp job show -g "$1" -n "$2" >/dev/null 2>\&1; }



create\_rg\_if\_missing() {

&nbsp; if exists\_rg "$1"; then echo "OK: RG exists: $1"; else

&nbsp;   echo "CREATE: RG $1 ($2)"; az group create -n "$1" -l "$2" >/dev/null

&nbsp; fi

}



create\_kv\_if\_missing() {

&nbsp; if exists\_kv "$1" "$2"; then echo "OK: Key Vault exists: $2"; else

&nbsp;   echo "CREATE: Key Vault $2"; az keyvault create -g "$1" -n "$2" -l "$3" >/dev/null

&nbsp; fi

}



create\_cosmos\_if\_missing() {

&nbsp; if exists\_cosmos "$1" "$2"; then echo "OK: Cosmos account exists: $2"; else

&nbsp;   echo "CREATE: Cosmos account $2"

&nbsp;   az cosmosdb create \\

&nbsp;     -g "$1" -n "$2" \\

&nbsp;     --locations regionName="$3" failoverPriority=0 isZoneRedundant=false \\

&nbsp;     --default-consistency-level "Session" \\

&nbsp;     --enable-free-tier true \\

&nbsp;     --backup-policy-type "Periodic" \\

&nbsp;     --backup-interval 240 \\

&nbsp;     --backup-retention 8 >/dev/null

&nbsp; fi

}



create\_cosmos\_db\_if\_missing() {

&nbsp; if exists\_cosmos\_db "$1" "$2" "$3"; then echo "OK: Cosmos DB exists: $3"; else

&nbsp;   echo "CREATE: Cosmos DB: $3 (RU=$4)"

&nbsp;   az cosmosdb sql database create -g "$1" -a "$2" -n "$3" --throughput "$4" >/dev/null

&nbsp; fi

}



create\_container\_if\_missing() {

&nbsp; if exists\_container "$1" "$2" "$3" "$4"; then echo "OK: Container exists: $4"; else

&nbsp;   echo "CREATE: Container $4 (PK=$5 RU=$6)"

&nbsp;   az cosmosdb sql container create \\

&nbsp;     -g "$1" -a "$2" -d "$3" -n "$4" -p "$5" --throughput "$6" >/dev/null

&nbsp; fi

}



kv\_set\_secret\_if\_value() {

&nbsp; local kv="$1" name="$2" value="${3:-}"

&nbsp; if \[\[ -z "$value" ]]; then

&nbsp;   echo "SKIP: secret $name (no value provided)"

&nbsp;   return 0

&nbsp; fi

&nbsp; echo "SET: KV secret $name"

&nbsp; az keyvault secret set --vault-name "$kv" --name "$name" --value "$value" >/dev/null

}



require\_images\_if\_containerapps() {

&nbsp; if \[\[ "$DO\_CONTAINERAPPS" != "true" ]]; then return 0; fi

&nbsp; local missing=0

&nbsp; for v in API\_IMAGE COLLECTOR\_IMAGE ANALYSIS\_IMAGE DELIVERY\_IMAGE; do

&nbsp;   if \[\[ -z "${!v}" ]]; then echo "ERROR: $v is required when DO\_CONTAINERAPPS=true"; missing=1; fi

&nbsp; done

&nbsp; \[\[ $missing -eq 0 ]] || exit 1

}



\# ------------------------------------------------------------------------------

\# Shared: Ensure ACA Cosmos schema + KV secrets in target RG/subscription

\# ------------------------------------------------------------------------------

ensure\_aca\_cosmos\_schema() {

&nbsp; local rg="$1" cosmos="$2" kv="$3" loc="$4"



&nbsp; create\_cosmos\_db\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$RU\_DB"



&nbsp; # Core ACA containers (PK=/subscriptionId)

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_SCANS"        "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_INVENTORIES"  "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_COSTDATA"     "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_ADVISOR"      "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_FINDINGS"     "/subscriptionId" "$RU\_CONTAINER"



&nbsp; # Billing/entitlements containers

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_ENTITLEMENTS" "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_PAYMENTS"     "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_CLIENTS"      "/subscriptionId" "$RU\_CONTAINER"

&nbsp; create\_container\_if\_missing "$rg" "$cosmos" "$COSMOS\_DB\_NAME" "$C\_STRIPE\_MAP"   "/stripeCustomerId" "$RU\_CONTAINER"



&nbsp; # Cosmos endpoint/key -> KV (recommended; apps read from KV at runtime)

&nbsp; local endpoint key

&nbsp; endpoint="$(az cosmosdb show -g "$rg" -n "$cosmos" --query documentEndpoint -o tsv)"

&nbsp; key="$(az cosmosdb keys list -g "$rg" -n "$cosmos" --type keys --query primaryMasterKey -o tsv)"



&nbsp; kv\_set\_secret\_if\_value "$kv" "COSMOS\_ENDPOINT" "$endpoint"

&nbsp; kv\_set\_secret\_if\_value "$kv" "COSMOS\_KEY" "$key"

&nbsp; kv\_set\_secret\_if\_value "$kv" "COSMOS\_DB\_NAME" "$COSMOS\_DB\_NAME"



&nbsp; # Stripe + URLs

&nbsp; kv\_set\_secret\_if\_value "$kv" "STRIPE\_SECRET\_KEY" "$STRIPE\_SECRET\_KEY"

&nbsp; kv\_set\_secret\_if\_value "$kv" "STRIPE\_WEBHOOK\_SECRET" "$STRIPE\_WEBHOOK\_SECRET"

&nbsp; kv\_set\_secret\_if\_value "$kv" "STRIPE\_PRICE\_TIER2\_ONE\_TIME" "$STRIPE\_PRICE\_TIER2\_ONE\_TIME"

&nbsp; kv\_set\_secret\_if\_value "$kv" "STRIPE\_PRICE\_TIER2\_SUBSCRIPTION" "$STRIPE\_PRICE\_TIER2\_SUBSCRIPTION"

&nbsp; kv\_set\_secret\_if\_value "$kv" "STRIPE\_PRICE\_TIER3\_ONE\_TIME" "$STRIPE\_PRICE\_TIER3\_ONE\_TIME"

&nbsp; kv\_set\_secret\_if\_value "$kv" "PUBLIC\_APP\_URL" "$PUBLIC\_APP\_URL"

&nbsp; kv\_set\_secret\_if\_value "$kv" "PUBLIC\_API\_URL" "$PUBLIC\_API\_URL"



&nbsp; # Optional: Entra/OIDC values if you want API to validate tokens

&nbsp; kv\_set\_secret\_if\_value "$kv" "ENTRA\_TENANT\_ID" "$ENTRA\_TENANT\_ID"

&nbsp; kv\_set\_secret\_if\_value "$kv" "ENTRA\_AUDIENCE" "$ENTRA\_AUDIENCE"



&nbsp; echo "OK: ACA Cosmos schema + KV secrets ensured."

}



\# ------------------------------------------------------------------------------

\# Managed Identity + Key Vault RBAC wiring

\# ------------------------------------------------------------------------------

ensure\_uami\_and\_kv\_access() {

&nbsp; local rg="$1" kv="$2"



&nbsp; if exists\_uami "$rg" "$UAMI\_NAME"; then

&nbsp;   echo "OK: UAMI exists: $UAMI\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: UAMI $UAMI\_NAME"

&nbsp;   az identity create -g "$rg" -n "$UAMI\_NAME" >/dev/null

&nbsp; fi



&nbsp; local principal\_id

&nbsp; principal\_id="$(az identity show -g "$rg" -n "$UAMI\_NAME" --query principalId -o tsv)"

&nbsp; local kv\_id

&nbsp; kv\_id="$(az keyvault show -g "$rg" -n "$kv" --query id -o tsv)"



&nbsp; # RBAC role for reading secrets (least privilege)

&nbsp; # If your org uses access policies instead of RBAC, this may fail; in that case switch to:

&nbsp; #   az keyvault set-policy --name <kv> --object-id <principal\_id> --secret-permissions get list

&nbsp; echo "ASSIGN: Key Vault Secrets User to UAMI on KV scope"

&nbsp; az role assignment create \\

&nbsp;   --assignee-object-id "$principal\_id" \\

&nbsp;   --assignee-principal-type ServicePrincipal \\

&nbsp;   --role "Key Vault Secrets User" \\

&nbsp;   --scope "$kv\_id" >/dev/null 2>\&1 || true



&nbsp; echo "OK: UAMI + Key Vault access wired."

}



\# ------------------------------------------------------------------------------

\# Container Apps: environment + API app + jobs

\# ------------------------------------------------------------------------------

ensure\_containerapps() {

&nbsp; local rg="$1" loc="$2" kv="$3" acr\_name="$4"



&nbsp; if \[\[ "$DO\_CONTAINERAPPS" != "true" ]]; then

&nbsp;   echo "SKIP: Container Apps (DO\_CONTAINERAPPS=false)"

&nbsp;   return 0

&nbsp; fi

&nbsp; require\_images\_if\_containerapps



&nbsp; # Ensure extension (safe if already installed)

&nbsp; az extension add --name containerapp --upgrade >/dev/null 2>\&1 || true



&nbsp; # Create Container Apps environment

&nbsp; if exists\_ca\_env "$rg" "$CA\_ENV\_NAME"; then

&nbsp;   echo "OK: Container Apps env exists: $CA\_ENV\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: Container Apps env $CA\_ENV\_NAME"

&nbsp;   az containerapp env create -g "$rg" -n "$CA\_ENV\_NAME" -l "$loc" >/dev/null

&nbsp; fi



&nbsp; # UAMI id

&nbsp; local uami\_id

&nbsp; uami\_id="$(az identity show -g "$rg" -n "$UAMI\_NAME" --query id -o tsv)"



&nbsp; # Registry auth

&nbsp; local registry\_server="" registry\_user="" registry\_pass=""

&nbsp; if \[\[ "$USE\_ACR" == "true" ]]; then

&nbsp;   registry\_server="$(az acr show -g "$rg" -n "$acr\_name" --query loginServer -o tsv 2>/dev/null || true)"

&nbsp;   if \[\[ -z "$registry\_server" ]]; then

&nbsp;     echo "ERROR: USE\_ACR=true but ACR '$acr\_name' not found in RG '$rg'."

&nbsp;     echo "  - Set USE\_ACR=false to use public GHCR images, OR"

&nbsp;     echo "  - Point acr\_name to an existing ACR in this RG."

&nbsp;     exit 1

&nbsp;   fi

&nbsp;   # Use admin creds for bootstrap (fine for dev); for prod prefer MI-based ACR pull with AcrPull role.

&nbsp;   az acr update -g "$rg" -n "$acr\_name" --admin-enabled true >/dev/null 2>\&1 || true

&nbsp;   registry\_user="$(az acr credential show -g "$rg" -n "$acr\_name" --query username -o tsv)"

&nbsp;   registry\_pass="$(az acr credential show -g "$rg" -n "$acr\_name" --query "passwords\[0].value" -o tsv)"

&nbsp; fi



&nbsp; # Helper: set env vars from Key Vault references (apps will read secrets via KV at startup)

&nbsp; # Container Apps supports secret references; we’ll store KV URI strings as secrets.

&nbsp; # We keep it simple: the app knows which secrets to fetch from KV using Managed Identity.

&nbsp; local kv\_uri

&nbsp; kv\_uri="$(az keyvault show -g "$rg" -n "$kv" --query properties.vaultUri -o tsv)"



&nbsp; # -----------------------

&nbsp; # ACA API Container App

&nbsp; # -----------------------

&nbsp; if exists\_ca\_app "$rg" "$CA\_API\_NAME"; then

&nbsp;   echo "OK: Container App exists: $CA\_API\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: Container App $CA\_API\_NAME"



&nbsp;   local ingress="external"

&nbsp;   \[\[ "$API\_INGRESS\_EXTERNAL" == "true" ]] || ingress="internal"



&nbsp;   if \[\[ "$USE\_ACR" == "true" ]]; then

&nbsp;     az containerapp create \\

&nbsp;       -g "$rg" -n "$CA\_API\_NAME" \\

&nbsp;       --environment "$CA\_ENV\_NAME" \\

&nbsp;       --image "$API\_IMAGE" \\

&nbsp;       --registry-server "$registry\_server" \\

&nbsp;       --registry-username "$registry\_user" \\

&nbsp;       --registry-password "$registry\_pass" \\

&nbsp;       --ingress "$ingress" \\

&nbsp;       --target-port "$API\_INGRESS\_PORT" \\

&nbsp;       --min-replicas 1 --max-replicas 2 \\

&nbsp;       --cpu 1.0 --memory 2Gi \\

&nbsp;       --user-assigned "$uami\_id" \\

&nbsp;       --env-vars \\

&nbsp;         KEYVAULT\_URI="$kv\_uri" \\

&nbsp;         COSMOS\_ENDPOINT\_SECRET\_NAME="COSMOS\_ENDPOINT" \\

&nbsp;         COSMOS\_KEY\_SECRET\_NAME="COSMOS\_KEY" \\

&nbsp;         COSMOS\_DB\_SECRET\_NAME="COSMOS\_DB\_NAME" \\

&nbsp;         STRIPE\_SECRET\_KEY\_NAME="STRIPE\_SECRET\_KEY" \\

&nbsp;         STRIPE\_WEBHOOK\_SECRET\_NAME="STRIPE\_WEBHOOK\_SECRET" \\

&nbsp;         STRIPE\_PRICE\_TIER2\_ONE\_TIME\_NAME="STRIPE\_PRICE\_TIER2\_ONE\_TIME" \\

&nbsp;         STRIPE\_PRICE\_TIER2\_SUBSCRIPTION\_NAME="STRIPE\_PRICE\_TIER2\_SUBSCRIPTION" \\

&nbsp;         STRIPE\_PRICE\_TIER3\_ONE\_TIME\_NAME="STRIPE\_PRICE\_TIER3\_ONE\_TIME" \\

&nbsp;         PUBLIC\_APP\_URL\_NAME="PUBLIC\_APP\_URL" \\

&nbsp;         PUBLIC\_API\_URL\_NAME="PUBLIC\_API\_URL" \\

&nbsp;         ENTRA\_TENANT\_ID\_NAME="ENTRA\_TENANT\_ID" \\

&nbsp;         ENTRA\_AUDIENCE\_NAME="ENTRA\_AUDIENCE" \\

&nbsp;       >/dev/null

&nbsp;   else

&nbsp;     az containerapp create \\

&nbsp;       -g "$rg" -n "$CA\_API\_NAME" \\

&nbsp;       --environment "$CA\_ENV\_NAME" \\

&nbsp;       --image "$API\_IMAGE" \\

&nbsp;       --ingress "$ingress" \\

&nbsp;       --target-port "$API\_INGRESS\_PORT" \\

&nbsp;       --min-replicas 1 --max-replicas 2 \\

&nbsp;       --cpu 1.0 --memory 2Gi \\

&nbsp;       --user-assigned "$uami\_id" \\

&nbsp;       --env-vars \\

&nbsp;         KEYVAULT\_URI="$kv\_uri" \\

&nbsp;         COSMOS\_ENDPOINT\_SECRET\_NAME="COSMOS\_ENDPOINT" \\

&nbsp;         COSMOS\_KEY\_SECRET\_NAME="COSMOS\_KEY" \\

&nbsp;         COSMOS\_DB\_SECRET\_NAME="COSMOS\_DB\_NAME" \\

&nbsp;         STRIPE\_SECRET\_KEY\_NAME="STRIPE\_SECRET\_KEY" \\

&nbsp;         STRIPE\_WEBHOOK\_SECRET\_NAME="STRIPE\_WEBHOOK\_SECRET" \\

&nbsp;         STRIPE\_PRICE\_TIER2\_ONE\_TIME\_NAME="STRIPE\_PRICE\_TIER2\_ONE\_TIME" \\

&nbsp;         STRIPE\_PRICE\_TIER2\_SUBSCRIPTION\_NAME="STRIPE\_PRICE\_TIER2\_SUBSCRIPTION" \\

&nbsp;         STRIPE\_PRICE\_TIER3\_ONE\_TIME\_NAME="STRIPE\_PRICE\_TIER3\_ONE\_TIME" \\

&nbsp;         PUBLIC\_APP\_URL\_NAME="PUBLIC\_APP\_URL" \\

&nbsp;         PUBLIC\_API\_URL\_NAME="PUBLIC\_API\_URL" \\

&nbsp;         ENTRA\_TENANT\_ID\_NAME="ENTRA\_TENANT\_ID" \\

&nbsp;         ENTRA\_AUDIENCE\_NAME="ENTRA\_AUDIENCE" \\

&nbsp;       >/dev/null

&nbsp;   fi

&nbsp; fi



&nbsp; # -----------------------

&nbsp; # Container Apps Jobs

&nbsp; # -----------------------

&nbsp; create\_job() {

&nbsp;   local job="$1" image="$2"

&nbsp;   if exists\_ca\_job "$rg" "$job"; then

&nbsp;     echo "OK: CA Job exists: $job"

&nbsp;     return 0

&nbsp;   fi

&nbsp;   echo "CREATE: CA Job $job"



&nbsp;   if \[\[ "$USE\_ACR" == "true" ]]; then

&nbsp;     az containerapp job create \\

&nbsp;       -g "$rg" -n "$job" \\

&nbsp;       --environment "$CA\_ENV\_NAME" \\

&nbsp;       --trigger-type "manual" \\

&nbsp;       --replica-timeout 3600 \\

&nbsp;       --replica-retry-limit 1 \\

&nbsp;       --replica-completion-count 1 \\

&nbsp;       --parallelism 1 \\

&nbsp;       --image "$image" \\

&nbsp;       --registry-server "$registry\_server" \\

&nbsp;       --registry-username "$registry\_user" \\

&nbsp;       --registry-password "$registry\_pass" \\

&nbsp;       --cpu 1.0 --memory 2Gi \\

&nbsp;       --user-assigned "$uami\_id" \\

&nbsp;       --env-vars \\

&nbsp;         KEYVAULT\_URI="$kv\_uri" \\

&nbsp;         COSMOS\_ENDPOINT\_SECRET\_NAME="COSMOS\_ENDPOINT" \\

&nbsp;         COSMOS\_KEY\_SECRET\_NAME="COSMOS\_KEY" \\

&nbsp;         COSMOS\_DB\_SECRET\_NAME="COSMOS\_DB\_NAME" \\

&nbsp;       >/dev/null

&nbsp;   else

&nbsp;     az containerapp job create \\

&nbsp;       -g "$rg" -n "$job" \\

&nbsp;       --environment "$CA\_ENV\_NAME" \\

&nbsp;       --trigger-type "manual" \\

&nbsp;       --replica-timeout 3600 \\

&nbsp;       --replica-retry-limit 1 \\

&nbsp;       --replica-completion-count 1 \\

&nbsp;       --parallelism 1 \\

&nbsp;       --image "$image" \\

&nbsp;       --cpu 1.0 --memory 2Gi \\

&nbsp;       --user-assigned "$uami\_id" \\

&nbsp;       --env-vars \\

&nbsp;         KEYVAULT\_URI="$kv\_uri" \\

&nbsp;         COSMOS\_ENDPOINT\_SECRET\_NAME="COSMOS\_ENDPOINT" \\

&nbsp;         COSMOS\_KEY\_SECRET\_NAME="COSMOS\_KEY" \\

&nbsp;         COSMOS\_DB\_SECRET\_NAME="COSMOS\_DB\_NAME" \\

&nbsp;       >/dev/null

&nbsp;   fi

&nbsp; }



&nbsp; create\_job "$CA\_COLLECTOR\_JOB" "$COLLECTOR\_IMAGE"

&nbsp; create\_job "$CA\_ANALYSIS\_JOB" "$ANALYSIS\_IMAGE"

&nbsp; create\_job "$CA\_DELIVERY\_JOB" "$DELIVERY\_IMAGE"



&nbsp; echo "OK: Container Apps environment, API app, and jobs are ready."

&nbsp; if \[\[ "$API\_INGRESS\_EXTERNAL" == "true" ]]; then

&nbsp;   echo "API FQDN:"

&nbsp;   az containerapp show -g "$rg" -n "$CA\_API\_NAME" --query properties.configuration.ingress.fqdn -o tsv

&nbsp; fi

}



\# ------------------------------------------------------------------------------

\# OPTIONAL: Cosmos RBAC (data-plane) for UAMI (org-dependent)

\# This is NOT required if your apps read COSMOS\_KEY from Key Vault and use key auth.

\# If your org wants keyless auth, you can enable AAD auth and assign a Cosmos SQL role.

\# ------------------------------------------------------------------------------

cosmos\_rbac\_optional() {

&nbsp; local rg="$1" cosmos="$2"

&nbsp; echo "INFO: Cosmos RBAC is optional and org-dependent."

&nbsp; echo "      This script does not enable Cosmos RBAC by default."

&nbsp; echo "      If you want to attempt it:"

&nbsp; cat <<'EOF'

\# 1) Get UAMI principalId and Cosmos account id:

\# uami\_principal\_id=$(az identity show -g <rg> -n <uami> --query principalId -o tsv)

\# cosmos\_id=$(az cosmosdb show -g <rg> -n <cosmos> --query id -o tsv)

\#

\# 2) List built-in SQL role definitions:

\# az cosmosdb sql role definition list -g <rg> -a <cosmos> -o table

\#

\# 3) Create role assignment (choose a role definition id):

\# role\_def\_id="<roleDefinitionId>"

\# az cosmosdb sql role assignment create \\

\#   -g <rg> -a <cosmos> \\

\#   --scope "/" \\

\#   --principal-id "$uami\_principal\_id" \\

\#   --role-definition-id "$role\_def\_id"

EOF

}



\# ------------------------------------------------------------------------------

\# OPTIONAL: APIM provisioning (costly/slow; org policy may block)

\# ------------------------------------------------------------------------------

ensure\_apim\_optional() {

&nbsp; local rg="$1" loc="$2"

&nbsp; if \[\[ "$DO\_APIM" != "true" ]]; then

&nbsp;   echo "SKIP: APIM (DO\_APIM=false)"

&nbsp;   return 0

&nbsp; fi



&nbsp; # You can set APIM\_NAME explicitly; default derived from RG (must be globally unique)

&nbsp; APIM\_NAME="${APIM\_NAME:-aca-apim-$(date +%y%m%d%H%M)}"

&nbsp; APIM\_PUBLISHER\_EMAIL="${APIM\_PUBLISHER\_EMAIL:-marco@example.com}"

&nbsp; APIM\_PUBLISHER\_NAME="${APIM\_PUBLISHER\_NAME:-ACA}"



&nbsp; if az apim show -g "$rg" -n "$APIM\_NAME" >/dev/null 2>\&1; then

&nbsp;   echo "OK: APIM exists: $APIM\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: APIM $APIM\_NAME (Developer SKU)"

&nbsp;   az apim create \\

&nbsp;     -g "$rg" -n "$APIM\_NAME" \\

&nbsp;     --location "$loc" \\

&nbsp;     --publisher-email "$APIM\_PUBLISHER\_EMAIL" \\

&nbsp;     --publisher-name "$APIM\_PUBLISHER\_NAME" \\

&nbsp;     --sku-name Developer >/dev/null

&nbsp; fi



&nbsp; echo "NOTE: API import/policies depend on your OpenAPI spec path and product design."

&nbsp; echo "You can import later with:"

&nbsp; cat <<'EOF'

\# az apim api import -g <rg> --service-name <apim> \\

\#   --path aca --api-id aca \\

\#   --specification-format OpenApi --specification-path ./openapi.yaml

EOF

}



\# ------------------------------------------------------------------------------

\# Phase 1: reuse marco\* resources

\# ------------------------------------------------------------------------------

phase1() {

&nbsp; echo "========================"

&nbsp; echo "PHASE 1 — marco\* reuse"

&nbsp; echo "========================"

&nbsp; az\_set\_sub "$PHASE1\_SUBSCRIPTION\_ID"



&nbsp; # Validate expected existing RG/resources

&nbsp; exists\_rg "$PHASE1\_RG" || { echo "ERROR: RG not found: $PHASE1\_RG"; exit 1; }

&nbsp; exists\_cosmos "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" || { echo "ERROR: Cosmos not found: $PHASE1\_COSMOS\_ACCOUNT"; exit 1; }

&nbsp; exists\_kv "$PHASE1\_RG" "$PHASE1\_KV\_NAME" || { echo "ERROR: KeyVault not found: $PHASE1\_KV\_NAME"; exit 1; }



&nbsp; # ACR is optional if USE\_ACR=false

&nbsp; if \[\[ "$USE\_ACR" == "true" ]]; then

&nbsp;   exists\_acr "$PHASE1\_RG" "$PHASE1\_ACR\_NAME" || { echo "ERROR: ACR not found: $PHASE1\_ACR\_NAME"; exit 1; }

&nbsp; fi



&nbsp; ensure\_aca\_cosmos\_schema "$PHASE1\_RG" "$PHASE1\_COSMOS\_ACCOUNT" "$PHASE1\_KV\_NAME" "$PHASE1\_LOC"

&nbsp; ensure\_uami\_and\_kv\_access "$PHASE1\_RG" "$PHASE1\_KV\_NAME"

&nbsp; ensure\_containerapps "$PHASE1\_RG" "$PHASE1\_LOC" "$PHASE1\_KV\_NAME" "$PHASE1\_ACR\_NAME"

&nbsp; ensure\_apim\_optional "$PHASE1\_RG" "$PHASE1\_LOC"



&nbsp; echo "OK: Phase 1 complete."

}



\# ------------------------------------------------------------------------------

\# Phase 2: provision new subscription + RG

\# ------------------------------------------------------------------------------

phase2() {

&nbsp; echo "=========================================="

&nbsp; echo "PHASE 2 — new subscription + new RG"

&nbsp; echo "=========================================="

&nbsp; \[\[ -n "$PHASE2\_SUBSCRIPTION\_ID" ]] || { echo "ERROR: PHASE2\_SUBSCRIPTION\_ID is required"; exit 1; }

&nbsp; az\_set\_sub "$PHASE2\_SUBSCRIPTION\_ID"



&nbsp; create\_rg\_if\_missing "$PHASE2\_RG" "$PHASE2\_LOC"



&nbsp; # Cosmos

&nbsp; create\_cosmos\_if\_missing "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$PHASE2\_LOC"



&nbsp; # KV

&nbsp; create\_kv\_if\_missing "$PHASE2\_RG" "$PHASE2\_KV\_NAME" "$PHASE2\_LOC"



&nbsp; # Storage (Tier3 artifacts)

&nbsp; if az storage account show -g "$PHASE2\_RG" -n "$PHASE2\_STORAGE" >/dev/null 2>\&1; then

&nbsp;   echo "OK: Storage exists: $PHASE2\_STORAGE"

&nbsp; else

&nbsp;   echo "CREATE: Storage $PHASE2\_STORAGE"

&nbsp;   az storage account create \\

&nbsp;     -g "$PHASE2\_RG" -n "$PHASE2\_STORAGE" -l "$PHASE2\_LOC" \\

&nbsp;     --sku Standard\_RAGRS --kind StorageV2 \\

&nbsp;     --https-only true \\

&nbsp;     --allow-blob-public-access false >/dev/null

&nbsp; fi



&nbsp; # ACR (optional)

&nbsp; if \[\[ "$USE\_ACR" == "true" ]]; then

&nbsp;   if exists\_acr "$PHASE2\_RG" "$PHASE2\_ACR\_NAME"; then

&nbsp;     echo "OK: ACR exists: $PHASE2\_ACR\_NAME"

&nbsp;   else

&nbsp;     echo "CREATE: ACR $PHASE2\_ACR\_NAME"

&nbsp;     az acr create -g "$PHASE2\_RG" -n "$PHASE2\_ACR\_NAME" -l "$PHASE2\_LOC" --sku Standard >/dev/null

&nbsp;   fi

&nbsp; fi



&nbsp; # Logs + AppInsights (optional but recommended)

&nbsp; if az monitor log-analytics workspace show -g "$PHASE2\_RG" -n "$PHASE2\_LOGS\_NAME" >/dev/null 2>\&1; then

&nbsp;   echo "OK: Log Analytics exists: $PHASE2\_LOGS\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: Log Analytics $PHASE2\_LOGS\_NAME"

&nbsp;   az monitor log-analytics workspace create -g "$PHASE2\_RG" -n "$PHASE2\_LOGS\_NAME" -l "$PHASE2\_LOC" >/dev/null

&nbsp; fi



&nbsp; if az monitor app-insights component show -g "$PHASE2\_RG" -a "$PHASE2\_APPINSIGHTS\_NAME" >/dev/null 2>\&1; then

&nbsp;   echo "OK: App Insights exists: $PHASE2\_APPINSIGHTS\_NAME"

&nbsp; else

&nbsp;   echo "CREATE: App Insights $PHASE2\_APPINSIGHTS\_NAME"

&nbsp;   local ws\_id

&nbsp;   ws\_id="$(az monitor log-analytics workspace show -g "$PHASE2\_RG" -n "$PHASE2\_LOGS\_NAME" --query id -o tsv)"

&nbsp;   az monitor app-insights component create \\

&nbsp;     -g "$PHASE2\_RG" -a "$PHASE2\_APPINSIGHTS\_NAME" -l "$PHASE2\_LOC" \\

&nbsp;     --kind web --workspace "$ws\_id" >/dev/null

&nbsp; fi



&nbsp; ensure\_aca\_cosmos\_schema "$PHASE2\_RG" "$PHASE2\_COSMOS\_ACCOUNT" "$PHASE2\_KV\_NAME" "$PHASE2\_LOC"

&nbsp; ensure\_uami\_and\_kv\_access "$PHASE2\_RG" "$PHASE2\_KV\_NAME"



&nbsp; if \[\[ "$USE\_ACR" == "true" ]]; then

&nbsp;   ensure\_containerapps "$PHASE2\_RG" "$PHASE2\_LOC" "$PHASE2\_KV\_NAME" "$PHASE2\_ACR\_NAME"

&nbsp; else

&nbsp;   ensure\_containerapps "$PHASE2\_RG" "$PHASE2\_LOC" "$PHASE2\_KV\_NAME" ""

&nbsp; fi



&nbsp; ensure\_apim\_optional "$PHASE2\_RG" "$PHASE2\_LOC"



&nbsp; echo "OK: Phase 2 complete."

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



echo

echo "============================"

echo "POST-RUN CHECKLIST (practical)"

echo "============================"

echo "1) Ensure your API container reads Key Vault secrets using Managed Identity."

echo "   - KEYVAULT\_URI env var is set in the Container App/Jobs."

echo "2) Configure Stripe webhook endpoint in Stripe dashboard:"

echo "   - https://<api-fqdn>/v1/webhooks/stripe"

echo "3) If using GA4+Clarity, wire GTM in React frontend and keep consent gating."

echo "4) If you enable APIM later: apply tier gating + entitlements caching policies."

echo

```



\### What you need to set before you run it (Phase 1 dev sandbox)



At minimum, because you said “proceed”, Container Apps will be created unless you turn it off:



```bash

export MODE=phase1

export DO\_CONTAINERAPPS=true

export USE\_ACR=true



\# Images (example – replace with your real repos/tags)

export API\_IMAGE="marcosandacr20260203.azurecr.io/aca/api:dev"

export COLLECTOR\_IMAGE="marcosandacr20260203.azurecr.io/aca/collector:dev"

export ANALYSIS\_IMAGE="marcosandacr20260203.azurecr.io/aca/analysis:dev"

export DELIVERY\_IMAGE="marcosandacr20260203.azurecr.io/aca/delivery:dev"



\# Optional but recommended: seed KV secrets in the run

export STRIPE\_SECRET\_KEY="sk\_..."

export STRIPE\_WEBHOOK\_SECRET="whsec\_..."

export STRIPE\_PRICE\_TIER2\_ONE\_TIME="price\_..."

export STRIPE\_PRICE\_TIER2\_SUBSCRIPTION="price\_..."

export STRIPE\_PRICE\_TIER3\_ONE\_TIME="price\_..."

export PUBLIC\_APP\_URL="https://app.aca.example.com"

export PUBLIC\_API\_URL="https://api.aca.example.com"



./aca-bootstrap.sh

```



If you want, next I can generate the \*\*minimal FastAPI code snippet\*\* that reads secrets from Key Vault using Managed Identity (so your Container App uses KV without embedding keys).



