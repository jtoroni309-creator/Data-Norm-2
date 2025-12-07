#!/usr/bin/env pwsh
# SOC 2 Type II E2E Test Runner with hardcoded credentials
$env:CPA_PASSWORD = 'Antonio1977$$'
& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\run-soc-e2e-full.ps1"
