# Test individual audit API endpoints with correct payloads
$ErrorActionPreference = "Continue"

$identityUrl = "https://cpa.auraai.toroniandcompany.com/api/identity"
$engagementUrl = "https://cpa.auraai.toroniandcompany.com/api/engagement"
$engagementId = "38d372f8-09b9-44c5-b563-67df703c8081"

# Login
$loginPayload = @{ email = "prodtestuser@toroni.com"; password = "TestPass123!" } | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }

Write-Host "=== Test 1: AI Materiality Calculation ===" -ForegroundColor Cyan
try {
    $materialityPayload = @{
        financial_statements = @{
            total_assets = 13200000
            total_revenue = 18000000
            net_income = 500000
            total_equity = 5200000
            total_liabilities = 8000000
        }
        industry = "manufacturing"
        entity_type = "private_company"
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/ai/materiality" -Method POST -Headers $headers -ContentType "application/json" -Body $materialityPayload
    Write-Host "[PASS] AI Materiality" -ForegroundColor Green
    Write-Host "Recommended Materiality: $($response.recommended_materiality)"
} catch {
    Write-Host "[FAIL] AI Materiality: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}

Write-Host ""
Write-Host "=== Test 2: AI Risk Assessment ===" -ForegroundColor Cyan
try {
    $riskPayload = @{
        financial_statements = @{
            total_assets = 13200000
            total_revenue = 18000000
            net_income = 500000
            total_equity = 5200000
            total_liabilities = 8000000
        }
        industry = "manufacturing"
        entity_type = "private_company"
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/ai/risk-assessment" -Method POST -Headers $headers -ContentType "application/json" -Body $riskPayload
    Write-Host "[PASS] AI Risk Assessment" -ForegroundColor Green
    Write-Host "Risk Level: $($response.overall_risk_assessment.risk_level)"
} catch {
    Write-Host "[FAIL] AI Risk Assessment: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}

Write-Host ""
Write-Host "=== Test 3: ML Anomaly Detection ===" -ForegroundColor Cyan
try {
    $anomalyPayload = @{
        transactions = @(
            @{ id = 1; amount = 1000; description = "Normal sale" }
            @{ id = 2; amount = 1200; description = "Normal sale" }
            @{ id = 3; amount = 150000; description = "Large unusual txn" }
            @{ id = 4; amount = 900; description = "Normal sale" }
        )
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/ml/anomaly-detection" -Method POST -Headers $headers -ContentType "application/json" -Body $anomalyPayload
    Write-Host "[PASS] ML Anomaly Detection" -ForegroundColor Green
    Write-Host "Anomalies Found: $($response.summary.total_anomalies)"
} catch {
    Write-Host "[FAIL] ML Anomaly Detection: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}

Write-Host ""
Write-Host "=== Test 4: ML Benford Analysis ===" -ForegroundColor Cyan
try {
    $benfordPayload = @{
        values = @(1234.5, 2345.6, 1567.8, 8901.2, 4567.8, 2134.5, 1456.7, 3456.7)
        analysis_type = "first_digit"
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/ml/benford-analysis" -Method POST -Headers $headers -ContentType "application/json" -Body $benfordPayload
    Write-Host "[PASS] ML Benford Analysis" -ForegroundColor Green
    Write-Host "Conformity: $($response.conformity_level)"
} catch {
    Write-Host "[FAIL] ML Benford Analysis: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}

Write-Host ""
Write-Host "=== Test 5: Engagement Transition to Planning ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/transition?new_status=planning" -Method POST -Headers $headers -ContentType "application/json"
    Write-Host "[PASS] Transition to Planning" -ForegroundColor Green
    Write-Host $response.message
} catch {
    Write-Host "[INFO] Transition: $($_.Exception.Message)" -ForegroundColor Yellow
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}

Write-Host ""
Write-Host "=== Test 6: Get Engagement Status ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId" -Method GET -Headers $headers
    Write-Host "[PASS] Get Engagement" -ForegroundColor Green
    Write-Host "Name: $($response.name)"
    Write-Host "Status: $($response.status)"
} catch {
    Write-Host "[FAIL] Get Engagement: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test 7: Workpaper Types List ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/workpapers/types" -Method GET -Headers $headers
    Write-Host "[PASS] Workpaper Types" -ForegroundColor Green
    Write-Host "Available Types: $($response.workpaper_types.Count)"
    foreach ($wp in $response.workpaper_types) {
        Write-Host "  - $($wp.reference): $($wp.name)"
    }
} catch {
    Write-Host "[FAIL] Workpaper Types: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test 8: ML Capabilities ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/ml/capabilities" -Method GET -Headers $headers
    Write-Host "[PASS] ML Capabilities" -ForegroundColor Green
    Write-Host "Engine: $($response.ml_engine)"
    Write-Host "Capabilities: $($response.capabilities.Keys -join ', ')"
} catch {
    Write-Host "[FAIL] ML Capabilities: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test 9: AI Agents List ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/ai/agents" -Method GET -Headers $headers
    Write-Host "[PASS] AI Agents" -ForegroundColor Green
    Write-Host "Active Agents: $($response.agents.Count)"
    foreach ($agent in $response.agents) {
        Write-Host "  - $($agent.name): $($agent.success_rate * 100)% success rate"
    }
} catch {
    Write-Host "[FAIL] AI Agents: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Green
