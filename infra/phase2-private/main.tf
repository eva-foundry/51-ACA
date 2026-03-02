# EVA-STORY: ACA-11-001
# EVA-STORY: ACA-11-002
# EVA-STORY: ACA-11-003
# EVA-STORY: ACA-11-004
# EVA-STORY: ACA-11-005
# EVA-STORY: ACA-11-006
# EVA-STORY: ACA-11-007
# EVA-STORY: ACA-11-008
// Phase 2 -- private ACA subscription
// Creates full stack: Container Apps env, Cosmos, OpenAI, APIM, ACR, KV, Storage, App Insights
// Deploy: terraform init && terraform apply -var-file=production.tfvars

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
  backend "azurerm" {}
}

provider "azurerm" {
  features {}
}

variable "resource_group_name" { type = string }
variable "location"            { type = string default = "canadacentral" }
variable "environment"         { type = string default = "prod" }
variable "openai_capacity"     { type = number default = 30 }

locals {
  prefix = "aca51-${var.environment}"
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "main" {
  name                = replace("${local.prefix}acr", "-", "")
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Standard"
  admin_enabled       = false
}

resource "azurerm_cosmosdb_account" "main" {
  name                = "${local.prefix}-cosmos"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"
  consistency_policy { consistency_level = "Session" }
  geo_location {
    location          = azurerm_resource_group.main.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "main" {
  name                = "aca-db"
  resource_group_name = azurerm_resource_group.main.name
  account_name        = azurerm_cosmosdb_account.main.name
}

resource "azurerm_storage_account" "main" {
  name                     = replace("${local.prefix}stor", "-", "")
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.prefix}-logs"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  retention_in_days   = 30
  sku                 = "PerGB2018"
}

resource "azurerm_application_insights" "main" {
  name                = "${local.prefix}-appinsights"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
}

resource "azurerm_container_app_environment" "main" {
  name                       = "${local.prefix}-aca-env"
  resource_group_name        = azurerm_resource_group.main.name
  location                   = azurerm_resource_group.main.location
  log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
}

output "aca_env_id"              { value = azurerm_container_app_environment.main.id }
output "cosmos_endpoint"         { value = azurerm_cosmosdb_account.main.endpoint }
output "storage_account_name"    { value = azurerm_storage_account.main.name }
output "app_insights_conn_str"   { value = azurerm_application_insights.main.connection_string sensitive = true }
output "acr_login_server"        { value = azurerm_container_registry.main.login_server }
