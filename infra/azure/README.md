# Aura Audit AI - Azure Infrastructure

This directory contains Terraform configuration for deploying the Aura Audit AI platform to Microsoft Azure.

## Quick Start

### Prerequisites

```bash
# Install required tools
az login
terraform init
```

### Deploy

```bash
# Automated deployment
./deploy.sh prod

# Manual deployment
terraform init
terraform plan -var="environment=prod" -out=tfplan
terraform apply tfplan
```

## Resources Created

- **AKS Cluster**: Kubernetes cluster with system and application node pools
- **PostgreSQL Flexible Server**: Database with pgvector extension
- **Azure Cache for Redis**: In-memory cache with persistence
- **Blob Storage**: Object storage with WORM compliance
- **Container Registry**: Docker image registry
- **Key Vault**: Secrets management
- **Application Gateway**: WAF-enabled ingress controller
- **Log Analytics**: Centralized logging
- **Application Insights**: APM and monitoring

## File Structure

```
infra/azure/
├── main.tf              # Main infrastructure configuration
├── variables.tf         # Input variables
├── terraform.tfvars     # Variable values (create this)
├── deploy.sh            # Automated deployment script
└── README.md            # This file
```

## Configuration

Create `terraform.tfvars`:

```hcl
location    = "eastus"
environment = "prod"

aks_system_node_count = 3
aks_app_node_count    = 3

postgres_high_availability = true
redis_sku                  = "Premium"
storage_replication_type   = "GRS"
```

## Cost Estimate

Production environment: ~$2,500/month

See [AZURE_DEPLOYMENT.md](../../AZURE_DEPLOYMENT.md) for details.

## Outputs

```bash
# View all outputs
terraform output

# Get specific values
terraform output postgres_fqdn
terraform output acr_login_server
terraform output key_vault_name
```

## Destroy

```bash
# Destroy all resources (use with caution!)
terraform destroy -var="environment=prod"
```

## Support

See [AZURE_DEPLOYMENT.md](../../AZURE_DEPLOYMENT.md) for comprehensive documentation.
