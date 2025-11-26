$env:PYTHONUTF8 = "1"
$OutputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

Write-Host "Fetching build logs..." -ForegroundColor Cyan
az acr task logs -r auraauditaiprodacr --run-id cc5q > "c:\Users\jtoroni\Data Norm\Data-Norm-2\build-logs.txt" 2>&1

Write-Host "Getting last 100 lines of logs..." -ForegroundColor Cyan
Get-Content "c:\Users\jtoroni\Data Norm\Data-Norm-2\build-logs.txt" -Tail 100
