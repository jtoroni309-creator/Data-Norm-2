/**
 * Azure AI/ML Training Environment - Terraform Infrastructure
 *
 * Creates complete Azure infrastructure for training CPA-level audit models
 *
 * Resources:
 * - Azure Machine Learning Workspace with compute clusters
 * - Azure OpenAI Service with GPT-4 and embeddings
 * - Azure AI Document Intelligence
 * - Azure Cognitive Search
 * - Azure PostgreSQL Flexible Server
 * - Azure Storage Account (Blob Storage)
 * - Azure Key Vault
 * - Azure Virtual Network (network isolation)
 * - Azure Monitor
 */

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47"
    }
  }

  # Store state in Azure Storage
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "sttfstate"
    container_name       = "tfstate"
    key                  = "aura-ml-training.tfstate"
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
}

# Variables
variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "aura-ml"
}

variable "enable_network_isolation" {
  description = "Enable VNet isolation for all services"
  type        = bool
  default     = true
}

# Locals
locals {
  resource_prefix = "${var.project_name}-${var.environment}"

  common_tags = {
    Project     = "Aura Audit AI - ML Training"
    Environment = var.environment
    ManagedBy   = "Terraform"
    Purpose     = "CPA-Level AI Model Training"
    Compliance  = "PCAOB,AICPA,SEC"
  }
}

# Resource Group
resource "azurerm_resource_group" "ml" {
  name     = "rg-${local.resource_prefix}"
  location = var.location
  tags     = local.common_tags
}

# Virtual Network (for network isolation)
resource "azurerm_virtual_network" "ml" {
  count               = var.enable_network_isolation ? 1 : 0
  name                = "vnet-${local.resource_prefix}"
  location            = azurerm_resource_group.ml.location
  resource_group_name = azurerm_resource_group.ml.name
  address_space       = ["10.0.0.0/16"]
  tags                = local.common_tags
}

resource "azurerm_subnet" "ml_compute" {
  count                = var.enable_network_isolation ? 1 : 0
  name                 = "snet-ml-compute"
  resource_group_name  = azurerm_resource_group.ml.name
  virtual_network_name = azurerm_virtual_network.ml[0].name
  address_prefixes     = ["10.0.1.0/24"]

  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.KeyVault",
    "Microsoft.Sql",
  ]
}

resource "azurerm_subnet" "data" {
  count                = var.enable_network_isolation ? 1 : 0
  name                 = "snet-data"
  resource_group_name  = azurerm_resource_group.ml.name
  virtual_network_name = azurerm_virtual_network.ml[0].name
  address_prefixes     = ["10.0.2.0/24"]

  service_endpoints = [
    "Microsoft.Storage",
    "Microsoft.Sql",
  ]

  delegation {
    name = "postgres-delegation"

    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action",
      ]
    }
  }
}

resource "azurerm_subnet" "private_endpoints" {
  count                = var.enable_network_isolation ? 1 : 0
  name                 = "snet-private-endpoints"
  resource_group_name  = azurerm_resource_group.ml.name
  virtual_network_name = azurerm_virtual_network.ml[0].name
  address_prefixes     = ["10.0.3.0/24"]
}

# Storage Account for training data and models
resource "azurerm_storage_account" "ml" {
  name                     = "st${replace(local.resource_prefix, "-", "")}ml"
  resource_group_name      = azurerm_resource_group.ml.name
  location                 = azurerm_resource_group.ml.location
  account_tier             = "Premium"
  account_replication_type = "LRS"
  account_kind             = "BlockBlobStorage"

  # Security
  enable_https_traffic_only       = true
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false

  # Network rules
  network_rules {
    default_action = var.enable_network_isolation ? "Deny" : "Allow"
    bypass         = ["AzureServices"]

    virtual_network_subnet_ids = var.enable_network_isolation ? [
      azurerm_subnet.ml_compute[0].id,
      azurerm_subnet.data[0].id,
    ] : []
  }

  tags = local.common_tags
}

# Storage containers
resource "azurerm_storage_container" "edgar_filings" {
  name                  = "edgar-filings"
  storage_account_name  = azurerm_storage_account.ml.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "training_data" {
  name                  = "training-data"
  storage_account_name  = azurerm_storage_account.ml.name
  container_access_type = "private"
}

resource "azurerm_storage_container" "models" {
  name                  = "models"
  storage_account_name  = azurerm_storage_account.ml.name
  container_access_type = "private"
}

# Key Vault for secrets
resource "azurerm_key_vault" "ml" {
  name                = "kv-${local.resource_prefix}"
  location            = azurerm_resource_group.ml.location
  resource_group_name = azurerm_resource_group.ml.name
  tenant_id           = data.azurerm_client_config.current.tenant_id
  sku_name            = "premium"

  purge_protection_enabled   = true
  soft_delete_retention_days = 90

  # Network ACLs
  network_acls {
    default_action = var.enable_network_isolation ? "Deny" : "Allow"
    bypass         = "AzureServices"

    virtual_network_subnet_ids = var.enable_network_isolation ? [
      azurerm_subnet.ml_compute[0].id,
    ] : []
  }

  tags = local.common_tags
}

# Key Vault access policy for current user/service principal
data "azurerm_client_config" "current" {}

resource "azurerm_key_vault_access_policy" "current" {
  key_vault_id = azurerm_key_vault.ml.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = [
    "Get", "List", "Set", "Delete", "Purge", "Recover",
  ]

  key_permissions = [
    "Get", "List", "Create", "Delete", "Purge", "Recover",
  ]
}

# Azure PostgreSQL Flexible Server
resource "azurerm_postgresql_flexible_server" "ml" {
  name                   = "psql-${local.resource_prefix}"
  resource_group_name    = azurerm_resource_group.ml.name
  location               = azurerm_resource_group.ml.location
  version                = "15"
  administrator_login    = "auradmin"
  administrator_password = random_password.postgres.result

  storage_mb   = 524288  # 512 GB
  storage_tier = "P30"

  sku_name = "GP_Standard_D8s_v3"  # 8 vCPU, 32 GB RAM

  # Network
  delegated_subnet_id = var.enable_network_isolation ? azurerm_subnet.data[0].id : null
  private_dns_zone_id = var.enable_network_isolation ? azurerm_private_dns_zone.postgres[0].id : null

  # Backup
  backup_retention_days        = 35
  geo_redundant_backup_enabled = true

  # High availability
  high_availability {
    mode = "ZoneRedundant"
  }

  tags = local.common_tags

  depends_on = [azurerm_private_dns_zone_virtual_network_link.postgres]
}

# PostgreSQL extensions
resource "azurerm_postgresql_flexible_server_configuration" "extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.ml.id
  value     = "VECTOR,PG_TRGM,BTREE_GIN,BTREE_GIST"
}

# PostgreSQL database
resource "azurerm_postgresql_flexible_server_database" "ml_training" {
  name      = "aura_ml_training"
  server_id = azurerm_postgresql_flexible_server.ml.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Random password for PostgreSQL
resource "random_password" "postgres" {
  length  = 32
  special = true
}

# Store PostgreSQL password in Key Vault
resource "azurerm_key_vault_secret" "postgres_password" {
  name         = "postgres-password"
  value        = random_password.postgres.result
  key_vault_id = azurerm_key_vault.ml.id

  depends_on = [azurerm_key_vault_access_policy.current]
}

# Private DNS zone for PostgreSQL
resource "azurerm_private_dns_zone" "postgres" {
  count               = var.enable_network_isolation ? 1 : 0
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.ml.name
  tags                = local.common_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  count                 = var.enable_network_isolation ? 1 : 0
  name                  = "postgres-vnet-link"
  resource_group_name   = azurerm_resource_group.ml.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres[0].name
  virtual_network_id    = azurerm_virtual_network.ml[0].id
  tags                  = local.common_tags
}

# Azure Machine Learning Workspace
resource "azurerm_application_insights" "ml" {
  name                = "appi-${local.resource_prefix}"
  location            = azurerm_resource_group.ml.location
  resource_group_name = azurerm_resource_group.ml.name
  application_type    = "web"
  tags                = local.common_tags
}

resource "azurerm_container_registry" "ml" {
  name                = "cr${replace(local.resource_prefix, "-", "")}"
  resource_group_name = azurerm_resource_group.ml.name
  location            = azurerm_resource_group.ml.location
  sku                 = "Premium"
  admin_enabled       = true

  # Network
  network_rule_set {
    default_action = var.enable_network_isolation ? "Deny" : "Allow"

    virtual_network {
      action    = "Allow"
      subnet_id = var.enable_network_isolation ? azurerm_subnet.ml_compute[0].id : null
    }
  }

  tags = local.common_tags
}

resource "azurerm_machine_learning_workspace" "ml" {
  name                    = "mlw-${local.resource_prefix}"
  location                = azurerm_resource_group.ml.location
  resource_group_name     = azurerm_resource_group.ml.name
  application_insights_id = azurerm_application_insights.ml.id
  key_vault_id            = azurerm_key_vault.ml.id
  storage_account_id      = azurerm_storage_account.ml.id
  container_registry_id   = azurerm_container_registry.ml.id

  identity {
    type = "SystemAssigned"
  }

  # Network isolation
  public_network_access_enabled = !var.enable_network_isolation

  tags = local.common_tags
}

# Azure OpenAI Service
resource "azurerm_cognitive_account" "openai" {
  name                = "oai-${local.resource_prefix}"
  location            = "eastus"  # OpenAI available in limited regions
  resource_group_name = azurerm_resource_group.ml.name
  kind                = "OpenAI"
  sku_name            = "S0"

  custom_subdomain_name = "oai-${local.resource_prefix}"

  # Network
  network_acls {
    default_action = var.enable_network_isolation ? "Deny" : "Allow"

    virtual_network_rules {
      subnet_id = var.enable_network_isolation ? azurerm_subnet.ml_compute[0].id : null
    }
  }

  tags = local.common_tags
}

# OpenAI Deployments
resource "azurerm_cognitive_deployment" "gpt4_turbo" {
  name                 = "gpt-4-turbo"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4"
    version = "turbo-2024-04-09"
  }

  scale {
    type     = "Standard"
    capacity = 100  # Provisioned throughput units
  }
}

resource "azurerm_cognitive_deployment" "embeddings" {
  name                 = "text-embedding-3-large"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-3-large"
    version = "1"
  }

  scale {
    type     = "Standard"
    capacity = 50
  }
}

# Azure AI Document Intelligence (Form Recognizer)
resource "azurerm_cognitive_account" "form_recognizer" {
  name                = "fmr-${local.resource_prefix}"
  location            = azurerm_resource_group.ml.location
  resource_group_name = azurerm_resource_group.ml.name
  kind                = "FormRecognizer"
  sku_name            = "S0"

  tags = local.common_tags
}

# Azure Cognitive Search
resource "azurerm_search_service" "ml" {
  name                = "srch-${local.resource_prefix}"
  resource_group_name = azurerm_resource_group.ml.name
  location            = azurerm_resource_group.ml.location
  sku                 = "standard"
  replica_count       = 3
  partition_count     = 1

  # Network
  public_network_access_enabled = !var.enable_network_isolation

  tags = local.common_tags
}

# Azure Monitor Log Analytics
resource "azurerm_log_analytics_workspace" "ml" {
  name                = "log-${local.resource_prefix}"
  location            = azurerm_resource_group.ml.location
  resource_group_name = azurerm_resource_group.ml.name
  sku                 = "PerGB2018"
  retention_in_days   = 90

  tags = local.common_tags
}

# Outputs
output "resource_group_name" {
  value = azurerm_resource_group.ml.name
}

output "ml_workspace_name" {
  value = azurerm_machine_learning_workspace.ml.name
}

output "openai_endpoint" {
  value = azurerm_cognitive_account.openai.endpoint
}

output "storage_account_name" {
  value = azurerm_storage_account.ml.name
}

output "postgres_host" {
  value = azurerm_postgresql_flexible_server.ml.fqdn
}

output "search_endpoint" {
  value = "https://${azurerm_search_service.ml.name}.search.windows.net"
}

output "key_vault_url" {
  value = azurerm_key_vault.ml.vault_uri
}
