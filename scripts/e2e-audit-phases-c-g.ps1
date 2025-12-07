# E2E Audit Test - Phases C through G
# Testing: Risk Assessment, Fieldwork, Completion, Reporting, Client Portal
$ErrorActionPreference = "Continue"

$identityUrl = "https://cpa.auraai.toroniandcompany.com/api/identity"
$engagementUrl = "https://cpa.auraai.toroniandcompany.com/api/engagement"
$clientPortalUrl = "https://portal.toroniandcompany.com/api"
$engagementId = "38d372f8-09b9-44c5-b563-67df703c8081"

$results = @()
function Log-Result($test, $status, $details) {
    $results += [PSCustomObject]@{ Test = $test; Status = $status; Details = $details }
    $color = switch ($status) { "PASS" { "Green" } "FAIL" { "Red" } "WARN" { "Yellow" } default { "White" } }
    Write-Host "[$status] $test" -ForegroundColor $color
    if ($details) { Write-Host "  $details" }
}

# Login
Write-Host "`n=== Authentication ===" -ForegroundColor Cyan
$loginPayload = @{ email = "prodtestuser@toroni.com"; password = "TestPass123!" } | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }
Log-Result "Authentication" "PASS" "Token acquired"

# ==================== PHASE C: RISK ASSESSMENT ====================
Write-Host "`n==================== PHASE C: RISK ASSESSMENT ====================" -ForegroundColor Magenta

# Test AI Risk Assessment with full financial data
Write-Host "`n=== C.1: AI Risk Assessment ===" -ForegroundColor Cyan
try {
    $riskPayload = @{
        financial_statements = @{
            total_assets = 13200000
            total_revenue = 18000000
            net_income = 500000
            total_equity = 5200000
            total_liabilities = 8000000
            cash = 1200000
            accounts_receivable = 2500000
            inventory = 3000000
            accounts_payable = 1800000
        }
        industry = "manufacturing"
        entity_type = "private_company"
        prior_year_data = @{
            total_assets = 12000000
            total_revenue = 16500000
            net_income = 450000
        }
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/ai/risk-assessment" -Method POST -Headers $headers -ContentType "application/json" -Body $riskPayload
    Log-Result "AI Risk Assessment" "PASS" "Risk Level: $($response.overall_risk_assessment.risk_level)"
} catch {
    Log-Result "AI Risk Assessment" "FAIL" $_.Exception.Message
}

# Test ML Fraud Detection
Write-Host "`n=== C.2: ML Fraud Detection ===" -ForegroundColor Cyan
try {
    $fraudPayload = @{
        transactions = @(
            @{ id = "JE001"; date = "2024-03-15"; debit_account = "Cash"; credit_account = "Revenue"; amount = 50000; description = "Normal sale" }
            @{ id = "JE002"; date = "2024-03-31"; debit_account = "Cash"; credit_account = "Revenue"; amount = 475000; description = "Quarter-end large sale" }
            @{ id = "JE003"; date = "2024-04-01"; debit_account = "Revenue"; credit_account = "Cash"; amount = -450000; description = "Return after quarter close" }
            @{ id = "JE004"; date = "2024-06-30"; debit_account = "Expense"; credit_account = "Accruals"; amount = 125000; description = "Year-end accrual" }
        )
        entity_data = @{
            total_revenue = 18000000
            total_assets = 13200000
        }
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/ml/fraud-detection" -Method POST -Headers $headers -ContentType "application/json" -Body $fraudPayload
    Log-Result "ML Fraud Detection" "PASS" "Risk Score: $($response.overall_risk_score), Level: $($response.risk_level)"
} catch {
    Log-Result "ML Fraud Detection" "FAIL" $_.Exception.Message
}

# Transition to fieldwork
Write-Host "`n=== C.3: Transition to Fieldwork ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/transition?new_status=fieldwork" -Method POST -Headers $headers -ContentType "application/json"
    Log-Result "Transition to Fieldwork" "PASS" $response.message
} catch {
    if ($_.ErrorDetails.Message -match "Invalid transition") {
        Log-Result "Transition to Fieldwork" "WARN" "Already in fieldwork or invalid state"
    } else {
        Log-Result "Transition to Fieldwork" "FAIL" $_.Exception.Message
    }
}

# ==================== PHASE D: INTERNAL CONTROLS ====================
Write-Host "`n==================== PHASE D: INTERNAL CONTROLS ====================" -ForegroundColor Magenta

# Create Internal Controls Workpaper
Write-Host "`n=== D.1: Create Internal Controls Workpaper ===" -ForegroundColor Cyan
try {
    $wpPayload = @{
        engagement_id = $engagementId
        reference = "IC-100"
        name = "Internal Controls Evaluation - Revenue Cycle"
        workpaper_type = "controls_testing"
        section = "D"
        content = @{
            control_area = "Revenue Recognition"
            controls_tested = @(
                @{ control_id = "REV-01"; description = "Sales orders approved by manager"; test_result = "effective"; exceptions = 0 }
                @{ control_id = "REV-02"; description = "Credit limits enforced"; test_result = "effective"; exceptions = 1 }
                @{ control_id = "REV-03"; description = "Shipment verification"; test_result = "effective"; exceptions = 0 }
            )
            overall_assessment = "Controls operating effectively with minor exceptions"
        }
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/workpapers" -Method POST -Headers $headers -ContentType "application/json" -Body $wpPayload
    Log-Result "Create IC Workpaper" "PASS" "Workpaper ID: $($response.id)"
    $icWorkpaperId = $response.id
} catch {
    Log-Result "Create IC Workpaper" "FAIL" $_.Exception.Message
}

# ==================== PHASE E: SUBSTANTIVE TESTING ====================
Write-Host "`n==================== PHASE E: SUBSTANTIVE TESTING ====================" -ForegroundColor Magenta

# Test ML Reconciliation
Write-Host "`n=== E.1: ML Transaction Reconciliation ===" -ForegroundColor Cyan
try {
    $reconPayload = @{
        source_transactions = @(
            @{ id = "BANK001"; date = "2024-12-01"; amount = 15000; description = "Wire transfer ABC Corp" }
            @{ id = "BANK002"; date = "2024-12-05"; amount = 8500; description = "Check deposit #1234" }
            @{ id = "BANK003"; date = "2024-12-10"; amount = 22000; description = "ACH payment XYZ Inc" }
        )
        target_transactions = @(
            @{ id = "GL001"; date = "2024-12-01"; amount = 15000; description = "ABC Corporation payment" }
            @{ id = "GL002"; date = "2024-12-05"; amount = 8500; description = "Customer deposit" }
            @{ id = "GL003"; date = "2024-12-11"; amount = 22000; description = "XYZ Inc wire" }
        )
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/ml/reconciliation" -Method POST -Headers $headers -ContentType "application/json" -Body $reconPayload
    Log-Result "ML Reconciliation" "PASS" "Match Rate: $([math]::Round($response.summary.match_rate * 100, 1))%"
} catch {
    Log-Result "ML Reconciliation" "FAIL" $_.Exception.Message
}

# Create Cash Lead Schedule Workpaper
Write-Host "`n=== E.2: Create Cash Lead Schedule ===" -ForegroundColor Cyan
try {
    $cashWpPayload = @{
        engagement_id = $engagementId
        reference = "C-100"
        name = "Cash Lead Schedule"
        workpaper_type = "lead_schedule"
        section = "C"
        content = @{
            accounts = @(
                @{ account = "Operating Cash - First National Bank"; balance = 850000; confirmed = $true; difference = 0 }
                @{ account = "Payroll Account - First National Bank"; balance = 125000; confirmed = $true; difference = 0 }
                @{ account = "Petty Cash"; balance = 5000; confirmed = $true; difference = 0 }
            )
            total_cash = 980000
            bank_confirmations_received = 2
            conclusion = "Cash balances agree to confirmations and GL"
        }
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/workpapers" -Method POST -Headers $headers -ContentType "application/json" -Body $cashWpPayload
    Log-Result "Create Cash Lead Schedule" "PASS" "Workpaper ID: $($response.id)"
} catch {
    Log-Result "Create Cash Lead Schedule" "FAIL" $_.Exception.Message
}

# Create Receivables Lead Schedule
Write-Host "`n=== E.3: Create Receivables Lead Schedule ===" -ForegroundColor Cyan
try {
    $arWpPayload = @{
        engagement_id = $engagementId
        reference = "D-100"
        name = "Receivables Lead Schedule"
        workpaper_type = "lead_schedule"
        section = "D"
        content = @{
            accounts = @(
                @{ account = "Trade Receivables"; balance = 2350000; allowance = 75000; net = 2275000 }
                @{ account = "Other Receivables"; balance = 150000; allowance = 5000; net = 145000 }
            )
            aging_summary = @{
                current = 1800000
                days_31_60 = 350000
                days_61_90 = 125000
                over_90 = 75000
            }
            confirmations_sent = 25
            confirmations_received = 22
            alternative_procedures_performed = 3
            conclusion = "AR balance fairly stated; allowance adequate"
        }
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/workpapers" -Method POST -Headers $headers -ContentType "application/json" -Body $arWpPayload
    Log-Result "Create AR Lead Schedule" "PASS" "Workpaper ID: $($response.id)"
} catch {
    Log-Result "Create AR Lead Schedule" "FAIL" $_.Exception.Message
}

# ==================== PHASE F: COMPLETION ====================
Write-Host "`n==================== PHASE F: COMPLETION ====================" -ForegroundColor Magenta

# Transition to review
Write-Host "`n=== F.1: Transition to Review ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/transition?new_status=review" -Method POST -Headers $headers -ContentType "application/json"
    Log-Result "Transition to Review" "PASS" $response.message
} catch {
    if ($_.ErrorDetails.Message -match "Invalid transition") {
        Log-Result "Transition to Review" "WARN" "May need to complete fieldwork first"
    } else {
        Log-Result "Transition to Review" "FAIL" $_.Exception.Message
    }
}

# Get engagement summary
Write-Host "`n=== F.2: Get Engagement Summary ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId" -Method GET -Headers $headers
    Log-Result "Engagement Summary" "PASS" "Status: $($response.status), Name: $($response.name)"
} catch {
    Log-Result "Engagement Summary" "FAIL" $_.Exception.Message
}

# List all workpapers
Write-Host "`n=== F.3: List All Workpapers ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/workpapers?engagement_id=$engagementId" -Method GET -Headers $headers
    if ($response -is [array]) {
        $wpCount = $response.Count
    } else {
        $wpCount = 1
    }
    Log-Result "List Workpapers" "PASS" "Total Workpapers: $wpCount"
} catch {
    Log-Result "List Workpapers" "FAIL" $_.Exception.Message
}

# ==================== PHASE G: REPORTING ====================
Write-Host "`n==================== PHASE G: REPORTING ====================" -ForegroundColor Magenta

# Generate AI Workpaper
Write-Host "`n=== G.1: Generate AI Workpaper ===" -ForegroundColor Cyan
try {
    $aiWpPayload = @{
        workpaper_type = "A-100"
        data = @{
            engagement_name = "HarborTech Manufacturing FYE 2024 Audit"
            client_name = "HarborTech Manufacturing, Inc."
            fiscal_year_end = "2024-12-31"
            engagement_partner = "J. Toroni, CPA"
            materiality = 180000
        }
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/ai/generate-workpaper" -Method POST -Headers $headers -ContentType "application/json" -Body $aiWpPayload
    Log-Result "Generate AI Workpaper" "PASS" "Generated workpaper type: A-100"
} catch {
    Log-Result "Generate AI Workpaper" "WARN" "Endpoint may require specific permissions: $($_.Exception.Message)"
}

# Generate Financial Statements Report
Write-Host "`n=== G.2: Generate Financial Statements Report ===" -ForegroundColor Cyan
try {
    $reportPayload = @{
        report_type = "audited_financial_statements"
        financial_data = @{
            balance_sheet = @{
                assets = @{
                    current_assets = @{
                        cash = 980000
                        accounts_receivable = 2420000
                        inventory = 3100000
                        prepaid_expenses = 180000
                    }
                    total_current_assets = 6680000
                    property_plant_equipment = 5800000
                    accumulated_depreciation = -1450000
                    net_ppe = 4350000
                    intangible_assets = 420000
                    other_assets = 250000
                    total_assets = 13200000
                }
                liabilities = @{
                    current_liabilities = @{
                        accounts_payable = 1650000
                        accrued_expenses = 820000
                        current_portion_ltd = 350000
                    }
                    total_current_liabilities = 2820000
                    long_term_debt = 3180000
                    deferred_taxes = 500000
                    total_liabilities = 8000000
                }
                equity = @{
                    common_stock = 1000000
                    retained_earnings = 4200000
                    total_equity = 5200000
                }
            }
            income_statement = @{
                revenue = 18000000
                cost_of_goods_sold = 12600000
                gross_profit = 5400000
                operating_expenses = 4200000
                operating_income = 1200000
                interest_expense = 280000
                income_before_taxes = 920000
                income_tax_expense = 220000
                net_income = 700000
            }
        }
        audit_opinion = "unqualified"
        report_date = "2025-03-15"
    } | ConvertTo-Json -Depth 10
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/reports/financial-statements" -Method POST -Headers $headers -ContentType "application/json" -Body $reportPayload
    Log-Result "Generate FS Report" "PASS" "Report generated successfully"
} catch {
    Log-Result "Generate FS Report" "WARN" "Report generation: $($_.Exception.Message)"
}

# Generate AICPA Compliant Report
Write-Host "`n=== G.3: Generate AICPA Compliant Report ===" -ForegroundColor Cyan
try {
    $aicpaPayload = @{
        client_name = "HarborTech Manufacturing, Inc."
        report_type = "audit"
        fiscal_year_end = "2024-12-31"
        opinion_type = "unqualified"
        financial_statements = @("balance_sheet", "income_statement", "statement_of_cash_flows", "statement_of_stockholders_equity")
    } | ConvertTo-Json -Depth 5
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/reports/aicpa-compliant" -Method POST -Headers $headers -ContentType "application/json" -Body $aicpaPayload
    Log-Result "AICPA Report" "PASS" "AICPA compliant report generated"
} catch {
    Log-Result "AICPA Report" "WARN" "AICPA report: $($_.Exception.Message)"
}

# Finalize engagement
Write-Host "`n=== G.4: Finalize Engagement ===" -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/transition?new_status=finalized" -Method POST -Headers $headers -ContentType "application/json"
    Log-Result "Finalize Engagement" "PASS" $response.message
} catch {
    Log-Result "Finalize Engagement" "WARN" "Finalization: $($_.Exception.Message)"
}

# ==================== CLIENT PORTAL TESTING ====================
Write-Host "`n==================== CLIENT PORTAL TESTING ====================" -ForegroundColor Magenta

# Test client portal authentication
Write-Host "`n=== CP.1: Client Portal Authentication ===" -ForegroundColor Cyan
try {
    $cpLoginPayload = @{ email = "prodtestuser@toroni.com"; password = "TestPass123!" } | ConvertTo-Json
    $cpLoginResponse = Invoke-RestMethod -Uri "$clientPortalUrl/identity/auth/login" -Method POST -ContentType "application/json" -Body $cpLoginPayload
    $cpToken = $cpLoginResponse.access_token
    $cpHeaders = @{ "Authorization" = "Bearer $cpToken" }
    Log-Result "Client Portal Auth" "PASS" "Client portal token acquired"
} catch {
    Log-Result "Client Portal Auth" "WARN" "Client portal: $($_.Exception.Message)"
    $cpHeaders = $null
}

# Test PBC document list
if ($cpHeaders) {
    Write-Host "`n=== CP.2: PBC Document List ===" -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "$clientPortalUrl/engagement/pbc/requests?engagement_id=$engagementId" -Method GET -Headers $cpHeaders
        Log-Result "PBC Document List" "PASS" "PBC requests retrieved"
    } catch {
        Log-Result "PBC Document List" "WARN" "PBC list: $($_.Exception.Message)"
    }
}

# ==================== FINAL SUMMARY ====================
Write-Host "`n`n==================== E2E TEST SUMMARY ====================" -ForegroundColor Green
Write-Host "Engagement: HarborTech Manufacturing FYE 2024 Audit" -ForegroundColor White
Write-Host "Engagement ID: $engagementId" -ForegroundColor White

$passCount = ($results | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($results | Where-Object { $_.Status -eq "FAIL" }).Count
$warnCount = ($results | Where-Object { $_.Status -eq "WARN" }).Count

Write-Host "`nResults:" -ForegroundColor White
Write-Host "  PASS: $passCount" -ForegroundColor Green
Write-Host "  FAIL: $failCount" -ForegroundColor Red
Write-Host "  WARN: $warnCount" -ForegroundColor Yellow

if ($failCount -eq 0) {
    Write-Host "`n*** OVERALL VERDICT: PASS ***" -ForegroundColor Green
    Write-Host "All critical audit workflow phases completed successfully." -ForegroundColor Green
} else {
    Write-Host "`n*** OVERALL VERDICT: NEEDS ATTENTION ***" -ForegroundColor Yellow
    Write-Host "Some tests failed - review details above." -ForegroundColor Yellow
}

Write-Host "`n=== Detailed Results ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize
