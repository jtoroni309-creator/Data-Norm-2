# Azure Shutdown Script - Reduce Spend to Zero
# This script stops/scales down all Azure resources to minimize costs

param(
    [string]$ResourceGroup = "aura-audit-ai-prod-rg",
    [string]$Environment = "prod",
    [switch]$DryRun = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Azure Cost Reduction Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($DryRun) {
    Write-Host "[DRY RUN MODE] - No changes will be made" -ForegroundColor Yellow
    Write-Host ""
}

# Check if logged into Azure
Write-Host "Checking Azure login status..." -ForegroundColor Yellow
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged into Azure. Please run 'az login' first." -ForegroundColor Red
    exit 1
}
Write-Host "Logged in as: $($account.user.name)" -ForegroundColor Green
Write-Host "Subscription: $($account.name)" -ForegroundColor Green
Write-Host ""

# List all resource groups to find the right one
Write-Host "Finding resource groups..." -ForegroundColor Yellow
$resourceGroups = az group list --query "[?contains(name, 'aura')].name" -o tsv
if ($resourceGroups) {
    Write-Host "Found resource groups:" -ForegroundColor Green
    $resourceGroups | ForEach-Object { Write-Host "  - $_" }
    Write-Host ""
}

# Function to execute or show command
function Invoke-AzCommand {
    param([string]$Description, [string]$Command)

    Write-Host "[$Description]" -ForegroundColor Cyan
    if ($DryRun) {
        Write-Host "  Would run: $Command" -ForegroundColor Gray
    } else {
        Write-Host "  Running: $Command" -ForegroundColor Gray
        Invoke-Expression $Command
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 1: Stop AKS Cluster" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Find and stop AKS clusters
$aksClusters = az aks list --query "[].{name:name, resourceGroup:resourceGroup}" -o json 2>$null | ConvertFrom-Json
if ($aksClusters) {
    foreach ($cluster in $aksClusters) {
        Write-Host "Found AKS cluster: $($cluster.name) in $($cluster.resourceGroup)" -ForegroundColor Yellow

        # Stop the AKS cluster (this deallocates all nodes)
        Invoke-AzCommand -Description "Stopping AKS cluster $($cluster.name)" `
            -Command "az aks stop --name $($cluster.name) --resource-group $($cluster.resourceGroup) --no-wait"
    }
} else {
    Write-Host "No AKS clusters found" -ForegroundColor Gray
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 2: Stop PostgreSQL Flexible Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Find and stop PostgreSQL Flexible Servers
$pgServers = az postgres flexible-server list --query "[].{name:name, resourceGroup:resourceGroup}" -o json 2>$null | ConvertFrom-Json
if ($pgServers) {
    foreach ($server in $pgServers) {
        Write-Host "Found PostgreSQL server: $($server.name) in $($server.resourceGroup)" -ForegroundColor Yellow

        Invoke-AzCommand -Description "Stopping PostgreSQL server $($server.name)" `
            -Command "az postgres flexible-server stop --name $($server.name) --resource-group $($server.resourceGroup) --no-wait"
    }
} else {
    Write-Host "No PostgreSQL Flexible Servers found" -ForegroundColor Gray
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 3: Stop Redis Cache" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Note: Azure Redis Cache cannot be "stopped" - it must be deleted to stop charges
# We'll just report what exists
$redisCaches = az redis list --query "[].{name:name, resourceGroup:resourceGroup, sku:sku.name}" -o json 2>$null | ConvertFrom-Json
if ($redisCaches) {
    foreach ($cache in $redisCaches) {
        Write-Host "Found Redis cache: $($cache.name) (SKU: $($cache.sku)) in $($cache.resourceGroup)" -ForegroundColor Yellow
        Write-Host "  WARNING: Redis Cache cannot be stopped - must be deleted to save costs" -ForegroundColor Red
        Write-Host "  To delete, run: az redis delete --name $($cache.name) --resource-group $($cache.resourceGroup)" -ForegroundColor Yellow
    }
} else {
    Write-Host "No Redis Caches found" -ForegroundColor Gray
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 4: Stop Application Gateway" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Application Gateway can be stopped
$appGateways = az network application-gateway list --query "[].{name:name, resourceGroup:resourceGroup}" -o json 2>$null | ConvertFrom-Json
if ($appGateways) {
    foreach ($gw in $appGateways) {
        Write-Host "Found Application Gateway: $($gw.name) in $($gw.resourceGroup)" -ForegroundColor Yellow

        Invoke-AzCommand -Description "Stopping Application Gateway $($gw.name)" `
            -Command "az network application-gateway stop --name $($gw.name) --resource-group $($gw.resourceGroup) --no-wait"
    }
} else {
    Write-Host "No Application Gateways found" -ForegroundColor Gray
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 5: Check for VMs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Find and deallocate any standalone VMs
$vms = az vm list --query "[].{name:name, resourceGroup:resourceGroup, powerState:powerState}" -o json 2>$null | ConvertFrom-Json
if ($vms) {
    foreach ($vm in $vms) {
        Write-Host "Found VM: $($vm.name) in $($vm.resourceGroup)" -ForegroundColor Yellow

        Invoke-AzCommand -Description "Deallocating VM $($vm.name)" `
            -Command "az vm deallocate --name $($vm.name) --resource-group $($vm.resourceGroup) --no-wait"
    }
} else {
    Write-Host "No standalone VMs found" -ForegroundColor Gray
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STEP 6: Check Container Apps" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Scale down Container Apps if any
$containerApps = az containerapp list --query "[].{name:name, resourceGroup:resourceGroup}" -o json 2>$null | ConvertFrom-Json
if ($containerApps) {
    foreach ($app in $containerApps) {
        Write-Host "Found Container App: $($app.name) in $($app.resourceGroup)" -ForegroundColor Yellow

        Invoke-AzCommand -Description "Scaling Container App $($app.name) to 0" `
            -Command "az containerapp update --name $($app.name) --resource-group $($app.resourceGroup) --min-replicas 0 --max-replicas 0"
    }
} else {
    Write-Host "No Container Apps found" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SUMMARY" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Resources that CAN be stopped (no ongoing charges when stopped):" -ForegroundColor Green
Write-Host "  - AKS Cluster (compute costs stop)" -ForegroundColor White
Write-Host "  - PostgreSQL Flexible Server" -ForegroundColor White
Write-Host "  - Application Gateway" -ForegroundColor White
Write-Host "  - Virtual Machines" -ForegroundColor White
Write-Host ""
Write-Host "Resources that STILL incur charges when stopped:" -ForegroundColor Yellow
Write-Host "  - Storage Account (data storage costs)" -ForegroundColor White
Write-Host "  - Redis Cache (must DELETE to stop charges)" -ForegroundColor White
Write-Host "  - Log Analytics workspace (data retention costs)" -ForegroundColor White
Write-Host "  - Key Vault (minimal but exists)" -ForegroundColor White
Write-Host "  - Public IPs (if reserved)" -ForegroundColor White
Write-Host ""
Write-Host "To FULLY eliminate costs, you would need to DELETE these resources." -ForegroundColor Red
Write-Host "Run with -DryRun to preview commands without executing." -ForegroundColor Cyan
Write-Host ""

if (-not $DryRun) {
    Write-Host "Commands have been submitted. Some operations run asynchronously." -ForegroundColor Green
    Write-Host "Check Azure Portal for status: https://portal.azure.com" -ForegroundColor Cyan
}
