#!/usr/bin/env bash

# ==============================================================================
# ACA Infrastructure Bootstrap (az cli)
# Phase 1: reuse marco* resources in EsDAICoE-Sandbox RG (dev sandbox)
# Phase 2: provision new subscription + RG (commercial MVP)
#
# Includes:
#   - Cosmos DB + all 11 containers (including admin_audit_events)
#   - Key Vault secrets
#   - Managed Identity (UAMI) + Key Vault RBAC wiring
#   - Container Apps Environment + ACA API Container App
#   - Container Apps Jobs: collector / analysis / delivery
#   - (Optional) APIM creation + policy placeholder
#
# Usage:
#   MODE=phase1 ./bootstrap.sh
#   MODE=phase2 PHASE2_SUBSCRIPTION_ID=<sub> ./bootstrap.sh
#
# Optional toggles:
#   DO_CONTAINERAPPS=true|false   (default true)
#   DO_APIM=true|false            (default false)
#   USE_ACR=true|false            (default true)
#
# Images (required when DO_CONTAINERAPPS=true):
#   API_IMAGE, COLLECTOR_IMAGE, ANALYSIS_IMAGE, DELIVERY_IMAGE
# ==============================================================================

set -euo pipefail

# ------------------------------------------------------------------------------
# REQUIRED SETTINGS
# ------------------------------------------------------------------------------
MODE="${MODE:-phase1}"  # phase1 | phase2

DO_CONTAINERAPPS="${DO_CONTAINERAPPS:-true}"
DO_APIM="${DO_APIM:-false}"
USE_ACR="${USE_ACR:-true}"

# Phase 1 (marco* reuse) target
PHASE1_SUBSCRIPTION_ID="${PHASE1_SUBSCRIPTION_ID:-d2d4e571-e0f2-4f6c-901a-f88f7669bcba}"
PHASE1_RG="${PHASE1_RG:-EsDAICoE-Sandbox}"
PHASE1_COSMOS_ACCOUNT="${PHASE1_COSMOS_ACCOUNT:-marco-sandbox-cosmos}"
PHASE1_KV_NAME="${PHASE1_KV_NAME:-marcosandkv20260203}"
PHASE1_ACR_NAME="${PHASE1_ACR_NAME:-marcosandacr20260203}"
PHASE1_LOC="${PHASE1_LOC:-canadacentral}"

# Phase 2 (new subscription)
PHASE2_SUBSCRIPTION_ID="${PHASE2_SUBSCRIPTION_ID:-}"
PHASE2_RG="${PHASE2_RG:-aca-prod-rg}"
PHASE2_LOC="${PHASE2_LOC:-canadacentral}"
PHASE2_COSMOS_ACCOUNT="${PHASE2_COSMOS_ACCOUNT:-aca-cosmos-$(date +%y%m%d%H%M)}"
PHASE2_KV_NAME="${PHASE2_KV_NAME:-aca-kv-$(date +%y%m%d%H%M)}"
PHASE2_ACR_NAME="${PHASE2_ACR_NAME:-acaacr$(date +%y%m%d%H%M)}"

# Cosmos
COSMOS_DB_NAME="${COSMOS_DB_NAME:-aca}"
RU_DB="${RU_DB:-400}"
RU_CONTAINER="${RU_CONTAINER:-400}"

# Container names
C_SCANS="scans"
C_INVENTORIES="inventories"
C_COSTDATA="cost-data"
C_ADVISOR="advisor"
C_FINDINGS="findings"
C_ENTITLEMENTS="entitlements"
C_PAYMENTS="payments"
C_CLIENTS="clients"
C_STRIPE_MAP="stripe_customer_map"
C_DELIVERABLES="deliverables"
C_ADMIN_AUDIT="admin_audit_events"       # Added: admin ops audit trail (PK=/subscriptionId)

# Managed Identity + Container Apps
UAMI_NAME="${UAMI_NAME:-aca-uami}"
CA_ENV_NAME="${CA_ENV_NAME:-aca-ca-env}"
CA_API_NAME="${CA_API_NAME:-aca-api}"
CA_COLLECTOR_JOB="${CA_COLLECTOR_JOB:-aca-collector}"
CA_ANALYSIS_JOB="${CA_ANALYSIS_JOB:-aca-analysis}"
CA_DELIVERY_JOB="${CA_DELIVERY_JOB:-aca-delivery}"

API_INGRESS_EXTERNAL="${API_INGRESS_EXTERNAL:-true}"
API_INGRESS_PORT="${API_INGRESS_PORT:-8080}"

# Images (set before running)
API_IMAGE="${API_IMAGE:-}"
COLLECTOR_IMAGE="${COLLECTOR_IMAGE:-}"
ANALYSIS_IMAGE="${ANALYSIS_IMAGE:-}"
DELIVERY_IMAGE="${DELIVERY_IMAGE:-}"

# Secrets (set as env vars or will be skipped)
STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-}"
STRIPE_WEBHOOK_SECRET="${STRIPE_WEBHOOK_SECRET:-}"
STRIPE_PRICE_TIER2_ONE_TIME="${STRIPE_PRICE_TIER2_ONE_TIME:-}"
STRIPE_PRICE_TIER2_SUBSCRIPTION="${STRIPE_PRICE_TIER2_SUBSCRIPTION:-}"
STRIPE_PRICE_TIER3_ONE_TIME="${STRIPE_PRICE_TIER3_ONE_TIME:-}"
PUBLIC_APP_URL="${PUBLIC_APP_URL:-}"
PUBLIC_API_URL="${PUBLIC_API_URL:-}"
ENTRA_TENANT_ID="${ENTRA_TENANT_ID:-}"
ENTRA_AUDIENCE="${ENTRA_AUDIENCE:-}"

# ------------------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------------------

need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: missing dependency: $1"; exit 1; }; }

az_set_sub() {
  local sub="$1"
  [[ -n "$sub" ]] || { echo "ERROR: subscription id is empty"; exit 1; }
  az account set --subscription "$sub" >/dev/null
}

exists_rg()        { az group exists -n "$1" | grep -qi true; }
exists_kv()        { az keyvault show -g "$1" -n "$2" >/dev/null 2>&1; }
exists_cosmos()    { az cosmosdb show -g "$1" -n "$2" >/dev/null 2>&1; }
exists_cosmos_db() { az cosmosdb sql database show -g "$1" -a "$2" -n "$3" >/dev/null 2>&1; }
exists_container() { az cosmosdb sql container show -g "$1" -a "$2" -d "$3" -n "$4" >/dev/null 2>&1; }
exists_uami()      { az identity show -g "$1" -n "$2" >/dev/null 2>&1; }
exists_ca_env()    { az containerapp env show -g "$1" -n "$2" >/dev/null 2>&1; }
exists_ca_app()    { az containerapp show -g "$1" -n "$2" >/dev/null 2>&1; }
exists_ca_job()    { az containerapp job show -g "$1" -n "$2" >/dev/null 2>&1; }

create_container_if_missing() {
  local rg="$1" cosmos="$2" db="$3" name="$4" pk="$5" ru="$6"
  if exists_container "$rg" "$cosmos" "$db" "$name"; then
    echo "OK: Container exists: $name"
  else
    echo "CREATE: Container $name (PK=$pk RU=$ru)"
    az cosmosdb sql container create \
      -g "$rg" -a "$cosmos" -d "$db" -n "$name" -p "$pk" --throughput "$ru" >/dev/null
  fi
}

kv_set_secret_if_value() {
  local kv="$1" name="$2" value="${3:-}"
  if [[ -z "$value" ]]; then echo "SKIP: secret $name (no value)"; return 0; fi
  echo "SET: KV secret $name"
  az keyvault secret set --vault-name "$kv" --name "$name" --value "$value" >/dev/null
}

require_images_if_containerapps() {
  [[ "$DO_CONTAINERAPPS" != "true" ]] && return 0
  local missing=0
  for v in API_IMAGE COLLECTOR_IMAGE ANALYSIS_IMAGE DELIVERY_IMAGE; do
    if [[ -z "${!v}" ]]; then echo "ERROR: $v is required when DO_CONTAINERAPPS=true"; missing=1; fi
  done
  [[ $missing -eq 0 ]] || exit 1
}

# ------------------------------------------------------------------------------
# Cosmos schema (all 11 containers including admin_audit_events)
# ------------------------------------------------------------------------------
ensure_aca_cosmos_schema() {
  local rg="$1" cosmos="$2" kv="$3"

  # Create DB
  if ! exists_cosmos_db "$rg" "$cosmos" "$COSMOS_DB_NAME"; then
    echo "CREATE: Cosmos DB $COSMOS_DB_NAME"
    az cosmosdb sql database create -g "$rg" -a "$cosmos" -n "$COSMOS_DB_NAME" --throughput "$RU_DB" >/dev/null
  else
    echo "OK: Cosmos DB exists: $COSMOS_DB_NAME"
  fi

  # Core scan containers (PK=/subscriptionId)
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_SCANS"        "/subscriptionId" "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_INVENTORIES"  "/subscriptionId" "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_COSTDATA"     "/subscriptionId" "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_ADVISOR"      "/subscriptionId" "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_FINDINGS"     "/subscriptionId" "$RU_CONTAINER"

  # Billing containers
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_ENTITLEMENTS" "/subscriptionId"   "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_PAYMENTS"     "/subscriptionId"   "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_CLIENTS"      "/subscriptionId"   "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_DELIVERABLES" "/subscriptionId"   "$RU_CONTAINER"
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_STRIPE_MAP"   "/stripeCustomerId" "$RU_CONTAINER"

  # Admin audit trail container (PK=/subscriptionId, doc id = aae::<uuid>)
  # Action enum: ENTITLEMENT_GRANTED | SUBSCRIPTION_LOCKED | SUBSCRIPTION_UNLOCKED |
  #              STRIPE_RECONCILE | RATE_LIMIT_OVERRIDE | FEATURE_FLAG_CHANGED
  create_container_if_missing "$rg" "$cosmos" "$COSMOS_DB_NAME" "$C_ADMIN_AUDIT"  "/subscriptionId" "$RU_CONTAINER"

  # Store Cosmos connection details in Key Vault
  local endpoint key
  endpoint="$(az cosmosdb show -g "$rg" -n "$cosmos" --query documentEndpoint -o tsv)"
  key="$(az cosmosdb keys list -g "$rg" -n "$cosmos" --type keys --query primaryMasterKey -o tsv)"
  kv_set_secret_if_value "$kv" "COSMOS_ENDPOINT"  "$endpoint"
  kv_set_secret_if_value "$kv" "COSMOS_KEY"       "$key"
  kv_set_secret_if_value "$kv" "COSMOS_DB_NAME"   "$COSMOS_DB_NAME"

  # Stripe + URL secrets
  kv_set_secret_if_value "$kv" "STRIPE_SECRET_KEY"             "$STRIPE_SECRET_KEY"
  kv_set_secret_if_value "$kv" "STRIPE_WEBHOOK_SECRET"         "$STRIPE_WEBHOOK_SECRET"
  kv_set_secret_if_value "$kv" "STRIPE_PRICE_TIER2_ONE_TIME"   "$STRIPE_PRICE_TIER2_ONE_TIME"
  kv_set_secret_if_value "$kv" "STRIPE_PRICE_TIER2_SUBSCRIPTION" "$STRIPE_PRICE_TIER2_SUBSCRIPTION"
  kv_set_secret_if_value "$kv" "STRIPE_PRICE_TIER3_ONE_TIME"   "$STRIPE_PRICE_TIER3_ONE_TIME"
  kv_set_secret_if_value "$kv" "PUBLIC_APP_URL"                "$PUBLIC_APP_URL"
  kv_set_secret_if_value "$kv" "PUBLIC_API_URL"                "$PUBLIC_API_URL"
  kv_set_secret_if_value "$kv" "ENTRA_TENANT_ID"               "$ENTRA_TENANT_ID"
  kv_set_secret_if_value "$kv" "ENTRA_AUDIENCE"                "$ENTRA_AUDIENCE"

  echo "OK: ACA Cosmos schema (11 containers) + KV secrets ensured."
}

# ------------------------------------------------------------------------------
# UAMI + Key Vault RBAC
# ------------------------------------------------------------------------------
ensure_uami_and_kv_access() {
  local rg="$1" kv="$2"

  if exists_uami "$rg" "$UAMI_NAME"; then
    echo "OK: UAMI exists: $UAMI_NAME"
  else
    echo "CREATE: UAMI $UAMI_NAME"
    az identity create -g "$rg" -n "$UAMI_NAME" >/dev/null
  fi

  local principal_id kv_id
  principal_id="$(az identity show -g "$rg" -n "$UAMI_NAME" --query principalId -o tsv)"
  kv_id="$(az keyvault show -g "$rg" -n "$kv" --query id -o tsv)"

  echo "ASSIGN: Key Vault Secrets User to UAMI on KV scope"
  az role assignment create \
    --assignee-object-id "$principal_id" \
    --assignee-principal-type ServicePrincipal \
    --role "Key Vault Secrets User" \
    --scope "$kv_id" >/dev/null 2>&1 || true  # idempotent

  echo "OK: UAMI + Key Vault access wired."
}

# ------------------------------------------------------------------------------
# Container Apps: environment + API app + 3 jobs
# ------------------------------------------------------------------------------
ensure_containerapps() {
  local rg="$1" loc="$2" kv="$3" acr_name="$4"

  if [[ "$DO_CONTAINERAPPS" != "true" ]]; then
    echo "SKIP: Container Apps (DO_CONTAINERAPPS=false)"
    return 0
  fi
  require_images_if_containerapps

  az extension add --name containerapp --upgrade >/dev/null 2>&1 || true

  if ! exists_ca_env "$rg" "$CA_ENV_NAME"; then
    echo "CREATE: Container Apps env $CA_ENV_NAME"
    az containerapp env create -g "$rg" -n "$CA_ENV_NAME" -l "$loc" >/dev/null
  else
    echo "OK: Container Apps env exists: $CA_ENV_NAME"
  fi

  local uami_id kv_uri
  uami_id="$(az identity show -g "$rg" -n "$UAMI_NAME" --query id -o tsv)"
  kv_uri="$(az keyvault show -g "$rg" -n "$kv" --query properties.vaultUri -o tsv)"

  # Registry auth (ACR or public)
  local registry_server="" registry_user="" registry_pass=""
  if [[ "$USE_ACR" == "true" ]]; then
    registry_server="$(az acr show -g "$rg" -n "$acr_name" --query loginServer -o tsv 2>/dev/null || true)"
    if [[ -z "$registry_server" ]]; then
      echo "ERROR: USE_ACR=true but ACR '$acr_name' not found in RG '$rg'."
      exit 1
    fi
    az acr update -g "$rg" -n "$acr_name" --admin-enabled true >/dev/null 2>&1 || true
    registry_user="$(az acr credential show -g "$rg" -n "$acr_name" --query username -o tsv)"
    registry_pass="$(az acr credential show -g "$rg" -n "$acr_name" --query "passwords[0].value" -o tsv)"
  fi

  # Common env vars for all containers
  local env_vars=(
    KEYVAULT_URI="$kv_uri"
    COSMOS_ENDPOINT_SECRET_NAME="COSMOS_ENDPOINT"
    COSMOS_KEY_SECRET_NAME="COSMOS_KEY"
    COSMOS_DB_SECRET_NAME="COSMOS_DB_NAME"
    STRIPE_SECRET_KEY_NAME="STRIPE_SECRET_KEY"
    STRIPE_WEBHOOK_SECRET_NAME="STRIPE_WEBHOOK_SECRET"
    STRIPE_PRICE_TIER2_ONE_TIME_NAME="STRIPE_PRICE_TIER2_ONE_TIME"
    STRIPE_PRICE_TIER2_SUBSCRIPTION_NAME="STRIPE_PRICE_TIER2_SUBSCRIPTION"
    STRIPE_PRICE_TIER3_ONE_TIME_NAME="STRIPE_PRICE_TIER3_ONE_TIME"
    PUBLIC_APP_URL_NAME="PUBLIC_APP_URL"
    PUBLIC_API_URL_NAME="PUBLIC_API_URL"
    ENTRA_TENANT_ID_NAME="ENTRA_TENANT_ID"
    ENTRA_AUDIENCE_NAME="ENTRA_AUDIENCE"
  )

  # ACA API Container App
  if ! exists_ca_app "$rg" "$CA_API_NAME"; then
    echo "CREATE: Container App $CA_API_NAME"
    local ingress="external"
    [[ "$API_INGRESS_EXTERNAL" == "true" ]] || ingress="internal"

    if [[ "$USE_ACR" == "true" ]]; then
      az containerapp create \
        -g "$rg" -n "$CA_API_NAME" \
        --environment "$CA_ENV_NAME" \
        --image "$API_IMAGE" \
        --registry-server "$registry_server" \
        --registry-username "$registry_user" \
        --registry-password "$registry_pass" \
        --ingress "$ingress" \
        --target-port "$API_INGRESS_PORT" \
        --min-replicas 1 --max-replicas 2 \
        --cpu 1.0 --memory 2Gi \
        --user-assigned "$uami_id" \
        --env-vars "${env_vars[@]}" >/dev/null
    else
      az containerapp create \
        -g "$rg" -n "$CA_API_NAME" \
        --environment "$CA_ENV_NAME" \
        --image "$API_IMAGE" \
        --ingress "$ingress" \
        --target-port "$API_INGRESS_PORT" \
        --min-replicas 1 --max-replicas 2 \
        --cpu 1.0 --memory 2Gi \
        --user-assigned "$uami_id" \
        --env-vars "${env_vars[@]}" >/dev/null
    fi
  else
    echo "OK: Container App exists: $CA_API_NAME"
  fi

  # Job common vars (subset)
  local job_env_vars=(
    KEYVAULT_URI="$kv_uri"
    COSMOS_ENDPOINT_SECRET_NAME="COSMOS_ENDPOINT"
    COSMOS_KEY_SECRET_NAME="COSMOS_KEY"
    COSMOS_DB_SECRET_NAME="COSMOS_DB_NAME"
  )

  # Helper: create a manual-trigger Container Apps Job
  create_job() {
    local job="$1" image="$2"
    if exists_ca_job "$rg" "$job"; then echo "OK: CA Job exists: $job"; return 0; fi
    echo "CREATE: CA Job $job"
    if [[ "$USE_ACR" == "true" ]]; then
      az containerapp job create \
        -g "$rg" -n "$job" \
        --environment "$CA_ENV_NAME" \
        --trigger-type "manual" \
        --replica-timeout 3600 \
        --replica-retry-limit 1 \
        --replica-completion-count 1 \
        --parallelism 1 \
        --image "$image" \
        --registry-server "$registry_server" \
        --registry-username "$registry_user" \
        --registry-password "$registry_pass" \
        --cpu 1.0 --memory 2Gi \
        --user-assigned "$uami_id" \
        --env-vars "${job_env_vars[@]}" >/dev/null
    else
      az containerapp job create \
        -g "$rg" -n "$job" \
        --environment "$CA_ENV_NAME" \
        --trigger-type "manual" \
        --replica-timeout 3600 \
        --replica-retry-limit 1 \
        --replica-completion-count 1 \
        --parallelism 1 \
        --image "$image" \
        --cpu 1.0 --memory 2Gi \
        --user-assigned "$uami_id" \
        --env-vars "${job_env_vars[@]}" >/dev/null
    fi
  }

  create_job "$CA_COLLECTOR_JOB" "$COLLECTOR_IMAGE"
  create_job "$CA_ANALYSIS_JOB"  "$ANALYSIS_IMAGE"
  create_job "$CA_DELIVERY_JOB"  "$DELIVERY_IMAGE"

  echo "OK: Container Apps (env + API app + 3 jobs) ready."
  if [[ "$API_INGRESS_EXTERNAL" == "true" ]]; then
    echo "API FQDN:"
    az containerapp show -g "$rg" -n "$CA_API_NAME" \
      --query properties.configuration.ingress.fqdn -o tsv
  fi
}

# ------------------------------------------------------------------------------
# OPTIONAL: APIM provisioning
# ------------------------------------------------------------------------------
ensure_apim_optional() {
  local rg="$1" loc="$2"
  if [[ "$DO_APIM" != "true" ]]; then echo "SKIP: APIM (DO_APIM=false)"; return 0; fi

  APIM_NAME="${APIM_NAME:-aca-apim-$(date +%y%m%d%H%M)}"
  APIM_PUBLISHER_EMAIL="${APIM_PUBLISHER_EMAIL:-admin@example.com}"
  APIM_PUBLISHER_NAME="${APIM_PUBLISHER_NAME:-ACA}"

  if az apim show -g "$rg" -n "$APIM_NAME" >/dev/null 2>&1; then
    echo "OK: APIM exists: $APIM_NAME"
  else
    echo "CREATE: APIM $APIM_NAME (this takes 20-45 min on first run)"
    az apim create \
      -g "$rg" -n "$APIM_NAME" \
      --publisher-email "$APIM_PUBLISHER_EMAIL" \
      --publisher-name  "$APIM_PUBLISHER_NAME" \
      --sku-name Consumption \
      -l "$loc" >/dev/null
  fi
  echo "OK: APIM ready. Import API definitions and apply APIM policies manually."
  echo "    Policy XML: infra/phase1-marco/apim/apim-entitlements-policy.xml"
}

# ------------------------------------------------------------------------------
# Phase 1 (marco* sandbox)
# ------------------------------------------------------------------------------
run_phase1() {
  echo "=== Phase 1: EsDAICoE-Sandbox (marco* reuse) ==="
  az_set_sub "$PHASE1_SUBSCRIPTION_ID"
  echo "OK: Subscription set to $PHASE1_SUBSCRIPTION_ID"

  # Cosmos and Key Vault must already exist in Phase 1
  if ! exists_cosmos "$PHASE1_RG" "$PHASE1_COSMOS_ACCOUNT"; then
    echo "ERROR: Cosmos account '$PHASE1_COSMOS_ACCOUNT' not found in RG '$PHASE1_RG'."
    echo "  Phase 1 requires pre-existing marco* resources."
    exit 1
  fi
  if ! exists_kv "$PHASE1_RG" "$PHASE1_KV_NAME"; then
    echo "ERROR: Key Vault '$PHASE1_KV_NAME' not found in RG '$PHASE1_RG'."
    exit 1
  fi

  ensure_aca_cosmos_schema "$PHASE1_RG" "$PHASE1_COSMOS_ACCOUNT" "$PHASE1_KV_NAME"
  ensure_uami_and_kv_access "$PHASE1_RG" "$PHASE1_KV_NAME"
  ensure_containerapps "$PHASE1_RG" "$PHASE1_LOC" "$PHASE1_KV_NAME" "$PHASE1_ACR_NAME"
  ensure_apim_optional "$PHASE1_RG" "$PHASE1_LOC"
  echo "=== Phase 1 complete ==="
}

# ------------------------------------------------------------------------------
# Phase 2 (new subscription)
# ------------------------------------------------------------------------------
run_phase2() {
  echo "=== Phase 2: New subscription (commercial MVP) ==="
  [[ -n "$PHASE2_SUBSCRIPTION_ID" ]] || { echo "ERROR: PHASE2_SUBSCRIPTION_ID is required for phase2"; exit 1; }
  az_set_sub "$PHASE2_SUBSCRIPTION_ID"

  PHASE2_RG_LOC="$PHASE2_LOC"
  if ! exists_rg "$PHASE2_RG"; then
    echo "CREATE: RG $PHASE2_RG"
    az group create -n "$PHASE2_RG" -l "$PHASE2_RG_LOC" >/dev/null
  else
    echo "OK: RG exists: $PHASE2_RG"
  fi

  # Create Cosmos
  if ! exists_cosmos "$PHASE2_RG" "$PHASE2_COSMOS_ACCOUNT"; then
    echo "CREATE: Cosmos account $PHASE2_COSMOS_ACCOUNT"
    az cosmosdb create \
      -g "$PHASE2_RG" -n "$PHASE2_COSMOS_ACCOUNT" \
      --locations regionName="$PHASE2_LOC" failoverPriority=0 isZoneRedundant=false \
      --default-consistency-level "Session" \
      --enable-free-tier false \
      --backup-policy-type "Periodic" \
      --backup-interval 240 \
      --backup-retention 8 >/dev/null
  else
    echo "OK: Cosmos account exists: $PHASE2_COSMOS_ACCOUNT"
  fi

  # Create Key Vault
  if ! exists_kv "$PHASE2_RG" "$PHASE2_KV_NAME"; then
    echo "CREATE: Key Vault $PHASE2_KV_NAME"
    az keyvault create -g "$PHASE2_RG" -n "$PHASE2_KV_NAME" -l "$PHASE2_LOC" >/dev/null
  else
    echo "OK: Key Vault exists: $PHASE2_KV_NAME"
  fi

  ensure_aca_cosmos_schema "$PHASE2_RG" "$PHASE2_COSMOS_ACCOUNT" "$PHASE2_KV_NAME"
  ensure_uami_and_kv_access "$PHASE2_RG" "$PHASE2_KV_NAME"
  ensure_containerapps "$PHASE2_RG" "$PHASE2_LOC" "$PHASE2_KV_NAME" "$PHASE2_ACR_NAME"
  ensure_apim_optional "$PHASE2_RG" "$PHASE2_LOC"
  echo "=== Phase 2 complete ==="
}

# ------------------------------------------------------------------------------
# Entry point
# ------------------------------------------------------------------------------
need az

case "$MODE" in
  phase1) run_phase1 ;;
  phase2) run_phase2 ;;
  *) echo "ERROR: MODE must be phase1 or phase2 (got: $MODE)"; exit 1 ;;
esac
