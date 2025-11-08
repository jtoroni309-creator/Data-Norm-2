# Terraform Backend Configuration for Azure Blob Storage
#
# This configuration stores Terraform state in Azure Blob Storage for:
# - Team collaboration
# - State locking
# - Disaster recovery
#
# SETUP REQUIRED:
#
# 1. Create a storage account for Terraform state:
#
#    az group create --name aura-tfstate-rg --location eastus
#
#    STORAGE_ACCOUNT_NAME="auratfstate$(date +%s)"
#
#    az storage account create \
#      --resource-group aura-tfstate-rg \
#      --name $STORAGE_ACCOUNT_NAME \
#      --sku Standard_LRS \
#      --encryption-services blob
#
#    az storage container create \
#      --name tfstate \
#      --account-name $STORAGE_ACCOUNT_NAME
#
# 2. Get the storage account key:
#
#    az storage account keys list \
#      --resource-group aura-tfstate-rg \
#      --account-name $STORAGE_ACCOUNT_NAME \
#      --query '[0].value' -o tsv
#
# 3. Set environment variable for backend authentication:
#
#    export ARM_ACCESS_KEY="<storage-account-key>"
#
# 4. Update the storage_account_name below with your actual storage account name
#
# 5. Initialize Terraform:
#
#    terraform init

terraform {
  backend "azurerm" {
    resource_group_name  = "aura-tfstate-rg"
    storage_account_name = "REPLACE_WITH_YOUR_STORAGE_ACCOUNT_NAME"  # Update this!
    container_name       = "tfstate"
    key                  = "prod.terraform.tfstate"
  }
}
