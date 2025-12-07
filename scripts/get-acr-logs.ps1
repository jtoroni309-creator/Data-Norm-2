$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$runId = "cc6c"
$logFile = "c:\Users\jtoroni\Data Norm\Data-Norm-2\acr-build-logs.txt"

# Get logs and save to file
try {
    $logs = az acr task logs -r auraauditaiprodacr --run-id $runId --output tsv 2>&1
    $logs | Out-File -FilePath $logFile -Encoding utf8
    Write-Host "Logs saved to: $logFile"
    Write-Host "Last 50 lines:"
    Get-Content $logFile -Tail 50
} catch {
    Write-Host "Error: $_"
}
