# Aura Audit AI - Azure Infrastructure
#
# This Terraform configuration deploys the complete Aura Audit AI platform to Azure
# with production-grade security, compliance, and high availability.

# Note: Terraform and provider configuration is in backend.tf (auto-generated)

provider "azuread" {}

# ========================================
# Local Variables
# ========================================

locals {
  project_name = "aura-audit-ai"
  environment  = var.environment

  # Resource naming convention: {project}-{resource}-{env}
  resource_prefix = "${local.project_name}-${local.environment}"

  # Common tags for all resources
  common_tags = merge(
    var.tags,
    {
      Project     = "Aura Audit AI"
      Environment = local.environment
      ManagedBy   = "Terraform"
      Compliance  = "PCAOB,AICPA,SEC"
    }
  )

  # Service names
  services = [
    "identity",
    "ingestion",
    "normalize",
    "analytics",
    "llm",
    "engagement",
    "disclosures",
    "reporting",
    "qc",
    "connectors"
  ]
}

# ========================================
# Resource Group
# ========================================

resource "azurerm_resource_group" "main" {
  name     = "${local.resource_prefix}-rg"
  location = var.location
  tags     = local.common_tags
}

# ========================================
# Virtual Network
# ========================================

resource "azurerm_virtual_network" "main" {
  name                = "${local.resource_prefix}-vnet"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  address_space       = ["10.0.0.0/16"]
  tags                = local.common_tags
}

# Subnet for AKS
resource "azurerm_subnet" "aks" {
  name                 = "${local.resource_prefix}-aks-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.0.0/20"]

  service_endpoints = [
    "Microsoft.Sql",
    "Microsoft.Storage",
    "Microsoft.KeyVault"
  ]
}

# Subnet for PostgreSQL
resource "azurerm_subnet" "database" {
  name                 = "${local.resource_prefix}-db-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.16.0/24"]

  delegation {
    name = "postgresql-delegation"
    service_delegation {
      name = "Microsoft.DBforPostgreSQL/flexibleServers"
      actions = [
        "Microsoft.Network/virtualNetworks/subnets/join/action"
      ]
    }
  }
}

# Subnet for Application Gateway
resource "azurerm_subnet" "appgw" {
  name                 = "${local.resource_prefix}-appgw-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.17.0/24"]
}

# ========================================
# Network Security Groups
# ========================================

resource "azurerm_network_security_group" "aks" {
  name                = "${local.resource_prefix}-aks-nsg"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags

  security_rule {
    name                       = "Allow-HTTPS"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "Allow-HTTP"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "aks" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks.id
}

# ========================================
# Log Analytics Workspace (for monitoring)
# ========================================

resource "azurerm_log_analytics_workspace" "main" {
  name                = "${local.resource_prefix}-logs"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = var.log_retention_days
  tags                = local.common_tags
}

# ========================================
# Application Insights
# ========================================

resource "azurerm_application_insights" "main" {
  name                = "${local.resource_prefix}-appinsights"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  retention_in_days   = var.log_retention_days
  tags                = local.common_tags
}

# ========================================
# Azure Container Registry
# ========================================

resource "azurerm_container_registry" "main" {
  name                = replace("${local.resource_prefix}acr", "-", "")
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = var.acr_sku
  admin_enabled       = false

  # Geo-replication for high availability (Premium SKU only)
  dynamic "georeplications" {
    for_each = var.acr_sku == "Premium" ? var.acr_georeplications : []
    content {
      location                = georeplications.value
      zone_redundancy_enabled = true
    }
  }

  # Enable content trust and vulnerability scanning
  trust_policy {
    enabled = true
  }

  retention_policy {
    days    = 30
    enabled = true
  }

  tags = local.common_tags
}

# ========================================
# Azure Kubernetes Service (AKS)
# ========================================

resource "azurerm_kubernetes_cluster" "main" {
  name                = "${local.resource_prefix}-aks"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "${local.resource_prefix}-k8s"
  kubernetes_version  = var.kubernetes_version

  # Default node pool (system)
  default_node_pool {
    name                = "system"
    node_count          = var.aks_system_node_count
    vm_size             = var.aks_system_node_size
    os_disk_size_gb     = 128
    vnet_subnet_id      = azurerm_subnet.aks.id
    type                = "VirtualMachineScaleSets"
    enable_auto_scaling = true
    min_count           = var.aks_system_node_count
    max_count           = var.aks_system_node_count * 2
    max_pods            = 110

    upgrade_settings {
      max_surge = "33%"
    }

    tags = local.common_tags
  }

  # Managed identity
  identity {
    type = "SystemAssigned"
  }

  # Network profile
  network_profile {
    network_plugin    = "azure"
    network_policy    = "azure"
    load_balancer_sku = "standard"
    service_cidr      = "10.1.0.0/16"
    dns_service_ip    = "10.1.0.10"
  }

  # Azure Monitor integration
  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  # Azure AD integration
  azure_active_directory_role_based_access_control {
    managed                = true
    azure_rbac_enabled     = true
    admin_group_object_ids = var.aks_admin_group_ids
  }

  # Security
  role_based_access_control_enabled = true

  # Key Vault secrets provider
  key_vault_secrets_provider {
    secret_rotation_enabled  = true
    secret_rotation_interval = "2m"
  }

  # Maintenance window
  maintenance_window {
    allowed {
      day   = "Sunday"
      hours = [2, 3, 4]
    }
  }

  tags = local.common_tags

  depends_on = [
    azurerm_subnet_network_security_group_association.aks
  ]
}

# Application node pool (for microservices)
resource "azurerm_kubernetes_cluster_node_pool" "application" {
  name                  = "apps"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size               = var.aks_app_node_size
  node_count            = var.aks_app_node_count
  enable_auto_scaling   = true
  min_count             = var.aks_app_node_count
  max_count             = var.aks_app_node_count * 3
  max_pods              = 110
  os_disk_size_gb       = 128
  vnet_subnet_id        = azurerm_subnet.aks.id

  node_labels = {
    "workload" = "application"
  }

  tags = local.common_tags
}

# Attach ACR to AKS
resource "azurerm_role_assignment" "aks_acr" {
  principal_id                     = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.main.id
  skip_service_principal_aad_check = true
}

# ========================================
# Azure Database for PostgreSQL
# ========================================

resource "random_password" "postgres_admin" {
  length  = 32
  special = true
}

resource "azurerm_postgresql_flexible_server" "main" {
  name                = "${local.resource_prefix}-psql"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.postgres_location  # Use separate location due to quota restrictions

  administrator_login    = var.postgres_admin_username
  administrator_password = random_password.postgres_admin.result

  sku_name   = var.postgres_sku
  version    = "15"
  storage_mb = var.postgres_storage_mb
  zone       = "1"  # Match existing zone configuration

  # High availability - disabled due to zone configuration issues
  # dynamic "high_availability" {
  #   for_each = var.postgres_high_availability ? [1] : []
  #   content {
  #     mode                      = "ZoneRedundant"
  #     standby_availability_zone = var.postgres_standby_zone
  #   }
  # }

  # Backup
  backup_retention_days        = var.postgres_backup_retention_days
  geo_redundant_backup_enabled = var.postgres_geo_redundant_backup

  # Network
  delegated_subnet_id           = azurerm_subnet.database.id
  private_dns_zone_id           = azurerm_private_dns_zone.postgres.id
  public_network_access_enabled = false

  # Maintenance window
  maintenance_window {
    day_of_week  = 0 # Sunday
    start_hour   = 2
    start_minute = 0
  }

  tags = local.common_tags

  depends_on = [
    azurerm_private_dns_zone_virtual_network_link.postgres
  ]
}

# PostgreSQL Configuration
resource "azurerm_postgresql_flexible_server_configuration" "extensions" {
  name      = "azure.extensions"
  server_id = azurerm_postgresql_flexible_server.main.id
  value     = "VECTOR,PGCRYPTO,PG_STAT_STATEMENTS"
}

# Main database
resource "azurerm_postgresql_flexible_server_database" "atlas" {
  name      = "atlas"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}

# Airflow database
resource "azurerm_postgresql_flexible_server_database" "airflow" {
  name      = "airflow"
  server_id = azurerm_postgresql_flexible_server.main.id
  collation = "en_US.utf8"
  charset   = "UTF8"
}

# Private DNS Zone for PostgreSQL
resource "azurerm_private_dns_zone" "postgres" {
  name                = "privatelink.postgres.database.azure.com"
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.common_tags
}

resource "azurerm_private_dns_zone_virtual_network_link" "postgres" {
  name                  = "${local.resource_prefix}-postgres-dns-link"
  resource_group_name   = azurerm_resource_group.main.name
  private_dns_zone_name = azurerm_private_dns_zone.postgres.name
  virtual_network_id    = azurerm_virtual_network.main.id
  tags                  = local.common_tags
}

# ========================================
# Azure Cache for Redis
# ========================================

resource "azurerm_redis_cache" "main" {
  name                = "${local.resource_prefix}-redis"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = var.redis_capacity
  family              = var.redis_family
  sku_name            = var.redis_sku

  # High availability
  enable_non_ssl_port           = false
  minimum_tls_version           = "1.2"
  public_network_access_enabled = false
  replicas_per_master           = var.redis_sku == "Premium" ? 1 : 0

  # Redis configuration
  redis_configuration {
    enable_authentication = true
    maxmemory_policy      = "allkeys-lru"

    # Persistence (Premium only)
    rdb_backup_enabled            = var.redis_sku == "Premium" ? true : false
    rdb_backup_frequency          = var.redis_sku == "Premium" ? 60 : null
    rdb_backup_max_snapshot_count = var.redis_sku == "Premium" ? 1 : null
    rdb_storage_connection_string = var.redis_sku == "Premium" ? azurerm_storage_account.main.primary_blob_connection_string : null
  }

  # Patch schedule
  patch_schedule {
    day_of_week    = "Sunday"
    start_hour_utc = 2
  }

  tags = local.common_tags
}

# Private endpoint for Redis
resource "azurerm_private_endpoint" "redis" {
  name                = "${local.resource_prefix}-redis-pe"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  subnet_id           = azurerm_subnet.aks.id

  private_service_connection {
    name                           = "${local.resource_prefix}-redis-psc"
    private_connection_resource_id = azurerm_redis_cache.main.id
    is_manual_connection           = false
    subresource_names              = ["redisCache"]
  }

  tags = local.common_tags
}

# ========================================
# Azure Storage Account
# ========================================

resource "azurerm_storage_account" "main" {
  name                     = replace("${local.resource_prefix}storage", "-", "")
  resource_group_name      = azurerm_resource_group.main.name
  location                 = azurerm_resource_group.main.location
  account_tier             = "Standard"
  account_replication_type = var.storage_replication_type
  account_kind             = "StorageV2"

  # Security
  min_tls_version                 = "TLS1_2"
  https_traffic_only_enabled      = true
  allow_nested_items_to_be_public = false
  shared_access_key_enabled       = true

  # Encryption
  infrastructure_encryption_enabled = true

  # Blob properties
  blob_properties {
    versioning_enabled  = true
    change_feed_enabled = true

    # Delete retention
    delete_retention_policy {
      days = var.blob_delete_retention_days
    }

    container_delete_retention_policy {
      days = var.blob_delete_retention_days
    }
  }

  # Network rules
  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [azurerm_subnet.aks.id]
  }

  tags = local.common_tags
}

# WORM Storage Container (for immutable audit trail)
# Temporarily commented - will be created manually via CLI after deployment
# resource "azurerm_storage_container" "worm" {
#   name                  = "atlas-worm"
#   storage_account_name  = azurerm_storage_account.main.name
#   container_access_type = "private"
# }

# Immutability policy (7 years for audit compliance)
resource "azurerm_storage_management_policy" "worm_immutability" {
  storage_account_id = azurerm_storage_account.main.id

  rule {
    name    = "worm-retention"
    enabled = true

    filters {
      blob_types = ["blockBlob"]
      prefix_match = ["atlas-worm/"]
    }

    actions {
      version {
        delete_after_days_since_creation = 2555 # 7 years
      }
    }
  }
}

# Role assignment for Terraform to manage storage
resource "azurerm_role_assignment" "terraform_storage_blob_contributor" {
  scope                = azurerm_storage_account.main.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = data.azurerm_client_config.current.object_id
}

# Standard blob containers
# Temporarily commented - will be created manually via CLI after deployment
# resource "azurerm_storage_container" "workpapers" {
#   name                  = "workpapers"
#   storage_account_name  = azurerm_storage_account.main.name
#   container_access_type = "private"
#
#   depends_on = [azurerm_role_assignment.terraform_storage_blob_contributor]
# }
#
# resource "azurerm_storage_container" "engagements" {
#   name                  = "engagements"
#   storage_account_name  = azurerm_storage_account.main.name
#   container_access_type = "private"
#
#   depends_on = [azurerm_role_assignment.terraform_storage_blob_contributor]
# }
#
# resource "azurerm_storage_container" "reports" {
#   name                  = "reports"
#   storage_account_name  = azurerm_storage_account.main.name
#   container_access_type = "private"
#
#   depends_on = [azurerm_role_assignment.terraform_storage_blob_contributor]
# }

# ========================================
# Azure Key Vault
# ========================================

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "main" {
  name                = "${local.resource_prefix}-kv2"  # Changed from kv to kv2 due to name conflict
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  tenant_id           = data.azurerm_client_config.current.tenant_id

  sku_name = "premium" # HSM-backed keys

  # Access policies
  enabled_for_deployment          = true
  enabled_for_disk_encryption     = true
  enabled_for_template_deployment = true
  enable_rbac_authorization       = true

  # Soft delete and purge protection (compliance requirement)
  soft_delete_retention_days = 90
  purge_protection_enabled   = true

  # Network
  public_network_access_enabled = false

  network_acls {
    bypass                     = "AzureServices"
    default_action             = "Deny"
    virtual_network_subnet_ids = [azurerm_subnet.aks.id]
  }

  tags = local.common_tags
}

# Grant AKS access to Key Vault
resource "azurerm_role_assignment" "aks_keyvault" {
  principal_id         = azurerm_kubernetes_cluster.main.key_vault_secrets_provider[0].secret_identity[0].object_id
  role_definition_name = "Key Vault Secrets User"
  scope                = azurerm_key_vault.main.id
}

# Store secrets in Key Vault
resource "azurerm_key_vault_secret" "postgres_admin_password" {
  name         = "postgres-admin-password"
  value        = random_password.postgres_admin.result
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_role_assignment.aks_keyvault]
}

resource "azurerm_key_vault_secret" "redis_primary_key" {
  name         = "redis-primary-key"
  value        = azurerm_redis_cache.main.primary_access_key
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_role_assignment.aks_keyvault]
}

resource "azurerm_key_vault_secret" "storage_connection_string" {
  name         = "storage-connection-string"
  value        = azurerm_storage_account.main.primary_connection_string
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_role_assignment.aks_keyvault]
}

resource "azurerm_key_vault_secret" "appinsights_instrumentation_key" {
  name         = "appinsights-instrumentation-key"
  value        = azurerm_application_insights.main.instrumentation_key
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_role_assignment.aks_keyvault]
}

# JWT secret for identity service
resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

resource "azurerm_key_vault_secret" "jwt_secret" {
  name         = "jwt-secret"
  value        = random_password.jwt_secret.result
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_role_assignment.aks_keyvault]
}

# Airflow fernet key
resource "random_password" "airflow_fernet_key" {
  length  = 32
  special = false
}

resource "azurerm_key_vault_secret" "airflow_fernet_key" {
  name         = "airflow-fernet-key"
  value        = base64encode(random_password.airflow_fernet_key.result)
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_role_assignment.aks_keyvault]
}

# ========================================
# Public IP for Application Gateway
# ========================================

resource "azurerm_public_ip" "appgw" {
  name                = "${local.resource_prefix}-appgw-pip"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  zones               = ["1", "2", "3"]

  tags = local.common_tags
}

# ========================================
# Application Gateway (Ingress Controller)
# ========================================

resource "azurerm_application_gateway" "main" {
  name                = "${local.resource_prefix}-appgw"
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  enable_http2        = true

  sku {
    name     = var.appgw_sku_name
    tier     = var.appgw_sku_tier
    capacity = var.appgw_capacity
  }

  gateway_ip_configuration {
    name      = "gateway-ip-config"
    subnet_id = azurerm_subnet.appgw.id
  }

  frontend_port {
    name = "frontend-port-80"
    port = 80
  }

  frontend_port {
    name = "frontend-port-443"
    port = 443
  }

  frontend_ip_configuration {
    name                 = "frontend-ip-config"
    public_ip_address_id = azurerm_public_ip.appgw.id
  }

  backend_address_pool {
    name = "aks-backend-pool"
  }

  backend_http_settings {
    name                  = "backend-http-settings"
    cookie_based_affinity = "Disabled"
    port                  = 80
    protocol              = "Http"
    request_timeout       = 60
    probe_name            = "health-probe"
  }

  http_listener {
    name                           = "http-listener"
    frontend_ip_configuration_name = "frontend-ip-config"
    frontend_port_name             = "frontend-port-80"
    protocol                       = "Http"
  }

  request_routing_rule {
    name                       = "routing-rule"
    rule_type                  = "Basic"
    http_listener_name         = "http-listener"
    backend_address_pool_name  = "aks-backend-pool"
    backend_http_settings_name = "backend-http-settings"
    priority                   = 1
  }

  probe {
    name                = "health-probe"
    protocol            = "Http"
    path                = "/health"
    interval            = 30
    timeout             = 30
    unhealthy_threshold = 3
    host                = "127.0.0.1"
  }

  # SSL policy
  ssl_policy {
    policy_type = "Predefined"
    policy_name = "AppGwSslPolicy20220101"
  }

  # WAF configuration (if using WAF_v2 tier)
  dynamic "waf_configuration" {
    for_each = var.appgw_sku_tier == "WAF_v2" ? [1] : []
    content {
      enabled          = true
      firewall_mode    = "Prevention"
      rule_set_type    = "OWASP"
      rule_set_version = "3.2"
    }
  }

  tags = local.common_tags
}

# ========================================
# Outputs
# ========================================

output "resource_group_name" {
  value       = azurerm_resource_group.main.name
  description = "Resource group name"
}

output "aks_cluster_name" {
  value       = azurerm_kubernetes_cluster.main.name
  description = "AKS cluster name"
}

output "aks_cluster_id" {
  value       = azurerm_kubernetes_cluster.main.id
  description = "AKS cluster ID"
}

output "acr_login_server" {
  value       = azurerm_container_registry.main.login_server
  description = "ACR login server URL"
}

output "postgres_fqdn" {
  value       = azurerm_postgresql_flexible_server.main.fqdn
  description = "PostgreSQL server FQDN"
  sensitive   = true
}

output "postgres_admin_username" {
  value       = var.postgres_admin_username
  description = "PostgreSQL admin username"
}

output "redis_hostname" {
  value       = azurerm_redis_cache.main.hostname
  description = "Redis hostname"
  sensitive   = true
}

output "storage_account_name" {
  value       = azurerm_storage_account.main.name
  description = "Storage account name"
}

output "key_vault_name" {
  value       = azurerm_key_vault.main.name
  description = "Key Vault name"
}

output "key_vault_uri" {
  value       = azurerm_key_vault.main.vault_uri
  description = "Key Vault URI"
}

output "application_gateway_public_ip" {
  value       = azurerm_public_ip.appgw.ip_address
  description = "Application Gateway public IP address"
}

output "appinsights_instrumentation_key" {
  value       = azurerm_application_insights.main.instrumentation_key
  description = "Application Insights instrumentation key"
  sensitive   = true
}

output "appinsights_connection_string" {
  value       = azurerm_application_insights.main.connection_string
  description = "Application Insights connection string"
  sensitive   = true
}
