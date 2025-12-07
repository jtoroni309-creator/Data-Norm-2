$env:CPA_PASSWORD = "Testing123!"
$env:CPA_USERNAME = "jtoroni@toroniandcompany.com"
Set-Location "c:\Users\jtoroni\Data Norm\Data-Norm-2"
& ".\scripts\run-soc-e2e-full.ps1"
