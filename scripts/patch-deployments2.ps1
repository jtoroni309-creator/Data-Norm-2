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

    # Create a temp file with the patch JSON
    $patchFile = [System.IO.Path]::GetTempFileName()
    $patchJson = @"
{"spec":{"template":{"spec":{"containers":[{"name":"$deployment","imagePullPolicy":"Always"}]}}}}
"@
    $patchJson | Out-File -FilePath $patchFile -Encoding ascii -NoNewline

    # Apply the patch
    & $kubectl patch deployment $deployment -n $namespace --patch-file $patchFile

    # Clean up
    Remove-Item $patchFile
}

Write-Host "Done!"
