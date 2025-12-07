$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"

# Get the identity pod
$POD = kubectl get pods -n aura-audit-ai -l app=identity -o jsonpath='{.items[0].metadata.name}'
Write-Host "Using pod: $POD"
Write-Host ""

# Read script and split into chunks to avoid command line limits
$scriptPath = "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\rd-study-e2e-enterprise.py"
$scriptContent = Get-Content $scriptPath -Raw
$scriptContent = $scriptContent -replace "`r`n", "`n"

# Write temp file
$tempFile = "C:\Users\jtoroni\AppData\Local\Temp\rd_test.py"
[System.IO.File]::WriteAllText($tempFile, $scriptContent, [System.Text.Encoding]::UTF8)

Write-Host "Copying test script to pod via tar..."

# Create tar archive and pipe to kubectl
$tarFile = "C:\Users\jtoroni\AppData\Local\Temp\rd_test.tar"
tar -cf $tarFile -C "C:\Users\jtoroni\AppData\Local\Temp" rd_test.py 2>$null

Get-Content $tarFile -Raw -AsByteStream | kubectl exec -i -n aura-audit-ai $POD -- tar -xf - -C /tmp/

if ($LASTEXITCODE -eq 0) {
    Write-Host "Running enterprise R&D study E2E test..."
    Write-Host "=========================================="
    kubectl exec -n aura-audit-ai $POD -- python /tmp/rd_test.py
} else {
    Write-Host "Trying alternative method..."
    # Try direct stdin approach
    Get-Content $tempFile -Raw | kubectl exec -i -n aura-audit-ai $POD -- tee /tmp/rd_test.py > $null
    kubectl exec -n aura-audit-ai $POD -- python /tmp/rd_test.py
}

# Cleanup
Remove-Item $tempFile -ErrorAction SilentlyContinue
Remove-Item $tarFile -ErrorAction SilentlyContinue
