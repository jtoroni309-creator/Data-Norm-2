$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"

$POD = kubectl get pods -n aura-audit-ai -l app=identity -o jsonpath='{.items[0].metadata.name}'
$scriptPath = "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\test-computer-rental.py"
$scriptContent = Get-Content $scriptPath -Raw
$scriptContent = $scriptContent -replace "`r`n", "`n"

$tempFile = "C:\Users\jtoroni\AppData\Local\Temp\test_cr.py"
[System.IO.File]::WriteAllText($tempFile, $scriptContent, [System.Text.Encoding]::UTF8)

Get-Content $tempFile -Raw | kubectl exec -i -n aura-audit-ai $POD -- tee /tmp/test_cr.py > $null
kubectl exec -n aura-audit-ai $POD -- python /tmp/test_cr.py

Remove-Item $tempFile -ErrorAction SilentlyContinue
