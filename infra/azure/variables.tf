# Aura Audit AI - Azure Infrastructure Variables

# ========================================
# General Configuration
# ========================================

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "eastus"
}

variable "postgres_location" {
  description = "Azure region for PostgreSQL (may differ due to quota restrictions)"
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

variable "log_retention_days" {
  description = "Log retention in days"
  type        = number
  default     = 90
}

# ========================================
# Azure Container Registry (ACR)
# ========================================

variable "acr_sku" {
  description = "ACR SKU tier"
  type        = string
  default     = "Premium"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.acr_sku)
    error_message = "ACR SKU must be Basic, Standard, or Premium."
  }
}

variable "acr_georeplications" {
  description = "ACR geo-replication locations (Premium only)"
  type        = list(string)
  default     = ["westus2"]
}

# ========================================
# Azure Kubernetes Service (AKS)
# ========================================

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "aks_admin_group_ids" {
  description = "Azure AD group IDs for AKS cluster admins"
  type        = list(string)
  default     = []
}

variable "aks_system_node_count" {
  description = "Number of system nodes"
  type        = number
  default     = 3

  validation {
    condition     = var.aks_system_node_count >= 1
    error_message = "System node count must be at least 1."
  }
}

variable "aks_system_node_size" {
  description = "VM size for system nodes"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "aks_app_node_count" {
  description = "Number of application nodes"
  type        = number
  default     = 3

  validation {
    condition     = var.aks_app_node_count >= 1
    error_message = "Application node count must be at least 1."
  }
}

variable "aks_app_node_size" {
  description = "VM size for application nodes"
  type        = string
  default     = "Standard_D8s_v3"
}

# ========================================
# Azure Database for PostgreSQL
# ========================================

variable "postgres_admin_username" {
  description = "PostgreSQL administrator username"
  type        = string
  default     = "atlasadmin"
}

variable "postgres_sku" {
  description = "PostgreSQL SKU name"
  type        = string
  default     = "GP_Standard_D4s_v3"
}

variable "postgres_storage_mb" {
  description = "PostgreSQL storage in MB"
  type        = number
  default     = 131072 # 128 GB
}

variable "postgres_high_availability" {
  description = "Enable PostgreSQL high availability"
  type        = bool
  default     = true
}

variable "postgres_standby_zone" {
  description = "Availability zone for PostgreSQL standby"
  type        = string
  default     = "2"
}

variable "postgres_backup_retention_days" {
  description = "PostgreSQL backup retention in days"
  type        = number
  default     = 35
}

variable "postgres_geo_redundant_backup" {
  description = "Enable geo-redundant backup for PostgreSQL"
  type        = bool
  default     = true
}

# ========================================
# Azure Cache for Redis
# ========================================

variable "redis_sku" {
  description = "Redis SKU (Basic, Standard, Premium)"
  type        = string
  default     = "Premium"

  validation {
    condition     = contains(["Basic", "Standard", "Premium"], var.redis_sku)
    error_message = "Redis SKU must be Basic, Standard, or Premium."
  }
}

variable "redis_family" {
  description = "Redis family (C for Basic/Standard, P for Premium)"
  type        = string
  default     = "P"

  validation {
    condition     = contains(["C", "P"], var.redis_family)
    error_message = "Redis family must be C or P."
  }
}

variable "redis_capacity" {
  description = "Redis capacity (0-6 for C/P family)"
  type        = number
  default     = 1
}

# ========================================
# Azure Storage
# ========================================

variable "storage_replication_type" {
  description = "Storage replication type"
  type        = string
  default     = "GRS" # Geo-redundant storage

  validation {
    condition     = contains(["LRS", "GRS", "RAGRS", "ZRS", "GZRS", "RAGZRS"], var.storage_replication_type)
    error_message = "Invalid storage replication type."
  }
}

variable "blob_delete_retention_days" {
  description = "Blob soft delete retention in days"
  type        = number
  default     = 30
}

# ========================================
# Application Gateway
# ========================================

variable "appgw_sku_name" {
  description = "Application Gateway SKU name"
  type        = string
  default     = "WAF_v2"

  validation {
    condition     = contains(["Standard_v2", "WAF_v2"], var.appgw_sku_name)
    error_message = "Application Gateway SKU must be Standard_v2 or WAF_v2."
  }
}

variable "appgw_sku_tier" {
  description = "Application Gateway SKU tier"
  type        = string
  default     = "WAF_v2"

  validation {
    condition     = contains(["Standard_v2", "WAF_v2"], var.appgw_sku_tier)
    error_message = "Application Gateway tier must be Standard_v2 or WAF_v2."
  }
}

variable "appgw_capacity" {
  description = "Application Gateway capacity units"
  type        = number
  default     = 2

  validation {
    condition     = var.appgw_capacity >= 1 && var.appgw_capacity <= 125
    error_message = "Application Gateway capacity must be between 1 and 125."
  }
}
