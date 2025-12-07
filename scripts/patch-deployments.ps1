$kubectl = "C:\Users\jtoroni\.azure-kubectl\kubectl.exe"
$namespace = "aura-audit-ai"

$deployments = @(
    "ai-orchestrator",
    "analytics",
    "connectors",
    "disclosures",
    "engagement",
    "marketing",
    "qc",
    "reporting"
)

foreach ($deployment in $deployments) {
    Write-Host "Patching $deployment..."
    $patch = @{
        spec = @{
            template = @{
                spec = @{
                    containers = @(
                        @{
                            name = $deployment
                            imagePullPolicy = "Always"
                        }
                    )
                }
            }
        }
    } | ConvertTo-Json -Depth 10 -Compress

    & $kubectl patch deployment $deployment -n $namespace -p $patch
}

Write-Host "Done!"
