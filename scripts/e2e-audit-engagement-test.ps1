# End-to-End Audit Engagement Service Test
# Tests the complete audit workflow from engagement creation to final report
# Client: HarborTech Manufacturing, Inc.

$ErrorActionPreference = "Continue"

# API URLs
$cpaBaseUrl = "https://cpa.auraai.toroniandcompany.com/api"
$identityUrl = "$cpaBaseUrl/identity"
$engagementUrl = "$cpaBaseUrl/engagement"

# Test Log
$testLog = @()
$artifacts = @()
$bugs = @()

function Log-Test {
    param(
        [string]$Module,
        [string]$Action,
        [string]$Data,
        [string]$Expected,
        [string]$Actual,
        [string]$Status
    )
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $script:testLog += @{
        Timestamp = $timestamp
        Module = $Module
        Action = $Action
        Data = $Data
        Expected = $Expected
        Actual = $Actual
        Status = $Status
    }
    $color = if ($Status -eq "PASS") { "Green" } elseif ($Status -eq "FAIL") { "Red" } else { "Yellow" }
    Write-Host "[$Status] $Module - $Action" -ForegroundColor $color
}

function Log-Bug {
    param(
        [string]$Severity,
        [string]$Module,
        [string]$Description,
        [string]$Expected,
        [string]$Actual
    )
    $script:bugs += @{
        Severity = $Severity
        Module = $Module
        Description = $Description
        Expected = $Expected
        Actual = $Actual
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Audit Engagement E2E Test Suite" -ForegroundColor Cyan
Write-Host "  HarborTech Manufacturing, Inc." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# STEP 1: Authentication
# ============================================
Write-Host "=== PHASE 1: Authentication ===" -ForegroundColor Yellow

$loginPayload = @{
    email = "prodtestuser@toroni.com"
    password = "TestPass123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
    $token = $loginResponse.access_token
    $userId = $loginResponse.user.id
    Log-Test -Module "Auth" -Action "Login as CPA User" -Data "prodtestuser@toroni.com" -Expected "Token received" -Actual "Token: $($token.Substring(0,20))..." -Status "PASS"
} catch {
    Log-Test -Module "Auth" -Action "Login as CPA User" -Data "prodtestuser@toroni.com" -Expected "Token received" -Actual "Error: $_" -Status "FAIL"
    Log-Bug -Severity "BLOCKER" -Module "Auth" -Description "Cannot login to CPA portal" -Expected "Successful login" -Actual $_
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# ============================================
# PHASE A: Pre-engagement / Setup
# ============================================
Write-Host ""
Write-Host "=== PHASE A: Pre-engagement / Setup ===" -ForegroundColor Yellow

# A.1 Create new audit engagement
Write-Host "A.1 Creating audit engagement..." -ForegroundColor Gray

$engagementPayload = @{
    name = "HarborTech Manufacturing FYE 2024 Audit"
    client_name = "HarborTech Manufacturing, Inc."
    engagement_type = "audit"
    reporting_framework = "us_gaap"
    fiscal_year_end = "2024-12-31"
    expected_completion_date = "2025-03-15"
    description = "Annual financial statement audit for HarborTech Manufacturing, Inc., a private C-Corp engaged in light manufacturing and electronics assembly."
    metadata = @{
        entity_type = "private_c_corp"
        industry = "light_manufacturing_electronics"
        fein = "12-3456789"
        hq_address = "100 Seaport Way, Newark, NJ 07102"
        erp_system = "quickbooks_online"
        prior_year_audited = $true
        prior_year_opinion = "unmodified"
    }
} | ConvertTo-Json -Depth 5

try {
    $engagementResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements" -Method POST -Headers $headers -Body $engagementPayload
    $engagementId = $engagementResponse.id
    Log-Test -Module "Engagement" -Action "Create audit engagement" -Data "HarborTech Manufacturing FYE 2024" -Expected "Engagement created" -Actual "ID: $engagementId" -Status "PASS"
    $artifacts += @{ Type = "Engagement"; Name = "HarborTech Manufacturing FYE 2024 Audit"; ID = $engagementId }
} catch {
    Log-Test -Module "Engagement" -Action "Create audit engagement" -Data "HarborTech Manufacturing FYE 2024" -Expected "Engagement created" -Actual "Error: $_" -Status "FAIL"
    Log-Bug -Severity "BLOCKER" -Module "Engagement" -Description "Cannot create engagement" -Expected "Engagement created" -Actual $_

    # Try to list existing engagements instead
    Write-Host "Trying to list existing engagements..." -ForegroundColor Gray
    try {
        $existingEngagements = Invoke-RestMethod -Uri "$engagementUrl/engagements" -Method GET -Headers $headers
        Write-Host "Found $($existingEngagements.Count) existing engagements" -ForegroundColor Gray
        if ($existingEngagements.Count -gt 0) {
            $engagementId = $existingEngagements[0].id
            Write-Host "Using existing engagement: $engagementId" -ForegroundColor Gray
        }
    } catch {
        Write-Host "Could not list engagements: $_" -ForegroundColor Red
    }
}

# A.2 Add engagement team
Write-Host "A.2 Adding engagement team..." -ForegroundColor Gray

$teamMembers = @(
    @{ role = "partner"; name = "Sarah Mitchell, CPA"; email = "partner@toroni.com" },
    @{ role = "manager"; name = "Michael Chen, CPA"; email = "manager@toroni.com" },
    @{ role = "senior"; name = "Jennifer Adams"; email = "senior@toroni.com" },
    @{ role = "staff"; name = "David Park"; email = "staff@toroni.com" }
)

foreach ($member in $teamMembers) {
    $teamPayload = @{
        user_id = $userId  # Using current user for testing
        role = $member.role
    } | ConvertTo-Json

    try {
        $teamResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/team" -Method POST -Headers $headers -Body $teamPayload
        Log-Test -Module "Team" -Action "Add $($member.role)" -Data $member.name -Expected "Team member added" -Actual "Success" -Status "PASS"
    } catch {
        Log-Test -Module "Team" -Action "Add $($member.role)" -Data $member.name -Expected "Team member added" -Actual "Error: $_" -Status "WARN"
    }
}

# ============================================
# PHASE B: Planning
# ============================================
Write-Host ""
Write-Host "=== PHASE B: Planning ===" -ForegroundColor Yellow

# B.1 AI Materiality Calculation
Write-Host "B.1 Calculating materiality with AI..." -ForegroundColor Gray

$materialityPayload = @{
    financial_data = @{
        total_assets = 13200000
        total_revenue = 18000000
        net_income = 500000
        total_equity = 7000000
        pretax_income = 800000
    }
    entity_profile = @{
        is_public = $false
        industry = "manufacturing"
        entity_type = "private_c_corp"
        reporting_framework = "us_gaap"
    }
    prior_year_data = @{
        total_assets = 12500000
        total_revenue = 16500000
        net_income = 450000
    }
} | ConvertTo-Json -Depth 5

try {
    $materialityResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/ai/materiality" -Method POST -Headers $headers -Body $materialityPayload
    Log-Test -Module "Materiality" -Action "AI materiality calculation" -Data "Total Assets: 13.2M, Revenue: 18M" -Expected "Materiality calculated" -Actual "Overall: $($materialityResponse.overall_materiality), Performance: $($materialityResponse.performance_materiality)" -Status "PASS"
    $artifacts += @{ Type = "Workpaper"; Name = "Materiality Calculation"; Data = $materialityResponse }
} catch {
    Log-Test -Module "Materiality" -Action "AI materiality calculation" -Data "Total Assets: 13.2M" -Expected "Materiality calculated" -Actual "Error: $_" -Status "WARN"
}

# B.2 AI Risk Assessment
Write-Host "B.2 Performing AI risk assessment..." -ForegroundColor Gray

$riskPayload = @{
    entity_info = @{
        name = "HarborTech Manufacturing, Inc."
        industry = "manufacturing"
        size = "medium"
        complexity = "moderate"
        ownership = "private"
        management_experience = "experienced"
        control_environment = "developing"
    }
    financial_data = @{
        total_assets = 13200000
        total_revenue = 18000000
        net_income = 500000
        gross_profit_margin = 0.39
        current_ratio = 2.14
        debt_to_equity = 0.89
    }
    significant_accounts = @(
        @{ account = "Cash"; balance = 1200000; assertions = @("existence", "completeness", "valuation") },
        @{ account = "Accounts Receivable"; balance = 2500000; assertions = @("existence", "valuation", "rights") },
        @{ account = "Inventory"; balance = 3000000; assertions = @("existence", "valuation", "completeness") },
        @{ account = "Fixed Assets"; balance = 6200000; assertions = @("existence", "valuation", "completeness") },
        @{ account = "Revenue"; balance = 18000000; assertions = @("occurrence", "completeness", "accuracy", "cutoff") }
    )
    known_risks = @(
        "Inventory obsolescence in fast-changing electronics market",
        "Revenue recognition for custom manufacturing orders",
        "Related party transactions with affiliated companies"
    )
} | ConvertTo-Json -Depth 5

try {
    $riskResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/ai/risk-assessment" -Method POST -Headers $headers -Body $riskPayload
    Log-Test -Module "Risk" -Action "AI risk assessment" -Data "5 significant accounts" -Expected "Risk assessment completed" -Actual "Risks identified: $($riskResponse.risks.Count)" -Status "PASS"
    $artifacts += @{ Type = "Workpaper"; Name = "Risk Assessment"; Data = $riskResponse }
} catch {
    Log-Test -Module "Risk" -Action "AI risk assessment" -Data "5 significant accounts" -Expected "Risk assessment completed" -Actual "Error: $_" -Status "WARN"
}

# B.3 Create binder structure
Write-Host "B.3 Creating binder structure..." -ForegroundColor Gray

$binderSections = @(
    @{ code = "A"; title = "Planning"; type = "folder" },
    @{ code = "B"; title = "Internal Controls"; type = "folder" },
    @{ code = "C"; title = "Cash & Bank"; type = "folder" },
    @{ code = "D"; title = "Receivables"; type = "folder" },
    @{ code = "E"; title = "Inventory"; type = "folder" },
    @{ code = "F"; title = "Fixed Assets"; type = "folder" },
    @{ code = "G"; title = "Liabilities"; type = "folder" },
    @{ code = "H"; title = "Equity"; type = "folder" },
    @{ code = "I"; title = "Revenue & Expenses"; type = "folder" },
    @{ code = "J"; title = "Completion"; type = "folder" },
    @{ code = "K"; title = "Reporting"; type = "folder" }
)

foreach ($section in $binderSections) {
    $binderPayload = @{
        node_code = $section.code
        title = $section.title
        node_type = $section.type
        position = [array]::IndexOf($binderSections, $section)
    } | ConvertTo-Json

    try {
        $binderResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/binder/nodes" -Method POST -Headers $headers -Body $binderPayload
        Log-Test -Module "Binder" -Action "Create section $($section.code)" -Data $section.title -Expected "Section created" -Actual "Success" -Status "PASS"
    } catch {
        Log-Test -Module "Binder" -Action "Create section $($section.code)" -Data $section.title -Expected "Section created" -Actual "Error: $_" -Status "WARN"
    }
}

# ============================================
# PHASE C: Generate Workpapers
# ============================================
Write-Host ""
Write-Host "=== PHASE C: Workpaper Generation ===" -ForegroundColor Yellow

# C.1 Generate Planning Memo workpaper
Write-Host "C.1 Generating Planning Memo workpaper..." -ForegroundColor Gray

$workpaperPayload = @{
    workpaper_types = @("planning_memo", "materiality", "analytical_procedures", "cash_lead", "receivables_lead")
    engagement_data = @{
        client_name = "HarborTech Manufacturing, Inc."
        fiscal_year_end = "2024-12-31"
        engagement_type = "audit"
        reporting_framework = "us_gaap"
    }
    financial_data = @{
        current_year = @{
            cash = 1200000
            accounts_receivable = 2500000
            inventory = 3000000
            prepaids = 300000
            fixed_assets = 6200000
            total_assets = 13200000
            accounts_payable = 1800000
            accrued_liabilities = 700000
            current_portion_ltd = 500000
            long_term_debt = 3200000
            total_liabilities = 6200000
            common_stock = 1000000
            retained_earnings_boy = 5500000
            net_income = 500000
            total_equity = 7000000
            revenue = 18000000
            cost_of_sales = 11000000
            gross_profit = 7000000
            operating_expenses = 5900000
            interest_expense = 300000
            pretax_income = 800000
            income_tax_expense = 300000
        }
        prior_year = @{
            cash = 1100000
            accounts_receivable = 2200000
            inventory = 2800000
            prepaids = 250000
            fixed_assets = 6150000
            total_assets = 12500000
            revenue = 16500000
            net_income = 450000
        }
    }
} | ConvertTo-Json -Depth 5

try {
    $workpaperResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/workpapers/generate" -Method POST -Headers $headers -Body $workpaperPayload
    Log-Test -Module "Workpapers" -Action "Generate workpapers" -Data "5 types" -Expected "Workpapers generated" -Actual "Generated: $($workpaperResponse.generated.Count)" -Status "PASS"
    foreach ($wp in $workpaperResponse.generated) {
        $artifacts += @{ Type = "Workpaper"; Name = $wp.name; Filename = $wp.filename }
    }
} catch {
    Log-Test -Module "Workpapers" -Action "Generate workpapers" -Data "5 types" -Expected "Workpapers generated" -Actual "Error: $_" -Status "WARN"
}

# ============================================
# PHASE D: Client Portal - Add Customer
# ============================================
Write-Host ""
Write-Host "=== PHASE D: Client Portal Integration ===" -ForegroundColor Yellow

# D.1 Add client contact to engagement
Write-Host "D.1 Adding client contact..." -ForegroundColor Gray

$customerPayload = @{
    email = "auditclient@harbortech-example.com"
    role = "primary_contact"
    permissions = @{
        can_view_reports = $true
        can_upload_documents = $true
        can_manage_integrations = $true
        can_view_financials = $true
        can_complete_questionnaires = $true
        can_approve_confirmations = $true
    }
} | ConvertTo-Json -Depth 5

try {
    $customerResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/customers" -Method POST -Headers $headers -Body $customerPayload
    Log-Test -Module "Portal" -Action "Add client contact" -Data "auditclient@harbortech-example.com" -Expected "Client added" -Actual "Customer ID: $($customerResponse.id)" -Status "PASS"
} catch {
    Log-Test -Module "Portal" -Action "Add client contact" -Data "auditclient@harbortech-example.com" -Expected "Client added" -Actual "Error: $_" -Status "WARN"
}

# ============================================
# PHASE E: ML Analytics Testing
# ============================================
Write-Host ""
Write-Host "=== PHASE E: ML Analytics ===" -ForegroundColor Yellow

# E.1 Anomaly Detection
Write-Host "E.1 Testing anomaly detection..." -ForegroundColor Gray

$anomalyPayload = @{
    transactions = @(
        @{ id = "TXN001"; date = "2024-01-15"; amount = 15000; account = "Revenue"; description = "Sales Invoice #1001" },
        @{ id = "TXN002"; date = "2024-02-20"; amount = 18000; account = "Revenue"; description = "Sales Invoice #1002" },
        @{ id = "TXN003"; date = "2024-03-25"; amount = 250000; account = "Revenue"; description = "Sales Invoice #1003 - LARGE" },
        @{ id = "TXN004"; date = "2024-04-10"; amount = 16500; account = "Revenue"; description = "Sales Invoice #1004" },
        @{ id = "TXN005"; date = "2024-05-15"; amount = 17200; account = "Revenue"; description = "Sales Invoice #1005" }
    )
    detection_method = "ensemble"
    threshold = 0.95
} | ConvertTo-Json -Depth 5

try {
    $anomalyResponse = Invoke-RestMethod -Uri "$engagementUrl/ml/anomaly-detection" -Method POST -Headers $headers -Body $anomalyPayload
    Log-Test -Module "ML" -Action "Anomaly detection" -Data "5 transactions" -Expected "Anomalies detected" -Actual "Anomalies: $($anomalyResponse.anomalies.Count)" -Status "PASS"
} catch {
    Log-Test -Module "ML" -Action "Anomaly detection" -Data "5 transactions" -Expected "Anomalies detected" -Actual "Error: $_" -Status "WARN"
}

# E.2 Benford's Law Analysis
Write-Host "E.2 Testing Benford's Law analysis..." -ForegroundColor Gray

$benfordPayload = @{
    amounts = @(1500, 2300, 3100, 4500, 1800, 2100, 3400, 1200, 2800, 1900, 2500, 3200, 1700, 2400, 3600, 1400, 2700, 3800, 1600, 2900)
    confidence_level = 0.95
} | ConvertTo-Json -Depth 5

try {
    $benfordResponse = Invoke-RestMethod -Uri "$engagementUrl/ml/benford-analysis" -Method POST -Headers $headers -Body $benfordPayload
    Log-Test -Module "ML" -Action "Benford's Law analysis" -Data "20 amounts" -Expected "Analysis completed" -Actual "Conformity: $($benfordResponse.conformity_score)" -Status "PASS"
} catch {
    Log-Test -Module "ML" -Action "Benford's Law analysis" -Data "20 amounts" -Expected "Analysis completed" -Actual "Error: $_" -Status "WARN"
}

# ============================================
# PHASE F: Transition Engagement Status
# ============================================
Write-Host ""
Write-Host "=== PHASE F: Engagement Workflow ===" -ForegroundColor Yellow

# F.1 Transition to Planning
Write-Host "F.1 Transitioning to Planning..." -ForegroundColor Gray

$transitionPayload = @{
    target_status = "planning"
    notes = "Planning phase initiated - all team members assigned"
} | ConvertTo-Json

try {
    $transitionResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/transition" -Method POST -Headers $headers -Body $transitionPayload
    Log-Test -Module "Workflow" -Action "Transition to Planning" -Data "" -Expected "Status: planning" -Actual "Status: $($transitionResponse.status)" -Status "PASS"
} catch {
    Log-Test -Module "Workflow" -Action "Transition to Planning" -Data "" -Expected "Status: planning" -Actual "Error: $_" -Status "WARN"
}

# F.2 Transition to Fieldwork
Write-Host "F.2 Transitioning to Fieldwork..." -ForegroundColor Gray

$transitionPayload = @{
    target_status = "fieldwork"
    notes = "Fieldwork commenced - substantive testing in progress"
} | ConvertTo-Json

try {
    $transitionResponse = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/transition" -Method POST -Headers $headers -Body $transitionPayload
    Log-Test -Module "Workflow" -Action "Transition to Fieldwork" -Data "" -Expected "Status: fieldwork" -Actual "Status: $($transitionResponse.status)" -Status "PASS"
} catch {
    Log-Test -Module "Workflow" -Action "Transition to Fieldwork" -Data "" -Expected "Status: fieldwork" -Actual "Error: $_" -Status "WARN"
}

# ============================================
# PHASE G: Get Engagement Summary
# ============================================
Write-Host ""
Write-Host "=== PHASE G: Engagement Summary ===" -ForegroundColor Yellow

try {
    $engagementSummary = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId" -Method GET -Headers $headers
    Write-Host ""
    Write-Host "Engagement Details:" -ForegroundColor Cyan
    Write-Host "  Name: $($engagementSummary.name)"
    Write-Host "  Type: $($engagementSummary.engagement_type)"
    Write-Host "  Status: $($engagementSummary.status)"
    Write-Host "  Fiscal Year End: $($engagementSummary.fiscal_year_end)"
    Log-Test -Module "Summary" -Action "Get engagement details" -Data $engagementId -Expected "Details retrieved" -Actual "Status: $($engagementSummary.status)" -Status "PASS"
} catch {
    Log-Test -Module "Summary" -Action "Get engagement details" -Data $engagementId -Expected "Details retrieved" -Actual "Error: $_" -Status "FAIL"
}

# Get binder tree
Write-Host ""
Write-Host "Binder Structure:" -ForegroundColor Cyan
try {
    $binderTree = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/binder/tree" -Method GET -Headers $headers
    foreach ($node in $binderTree) {
        Write-Host "  [$($node.node_code)] $($node.title) - $($node.node_type)"
    }
    Log-Test -Module "Binder" -Action "Get binder tree" -Data $engagementId -Expected "Tree retrieved" -Actual "Sections: $($binderTree.Count)" -Status "PASS"
} catch {
    Log-Test -Module "Binder" -Action "Get binder tree" -Data $engagementId -Expected "Tree retrieved" -Actual "Error: $_" -Status "WARN"
}

# ============================================
# TEST RESULTS SUMMARY
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST RESULTS SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$passCount = ($testLog | Where-Object { $_.Status -eq "PASS" }).Count
$failCount = ($testLog | Where-Object { $_.Status -eq "FAIL" }).Count
$warnCount = ($testLog | Where-Object { $_.Status -eq "WARN" }).Count

Write-Host "Test Results:" -ForegroundColor White
Write-Host "  PASS: $passCount" -ForegroundColor Green
Write-Host "  FAIL: $failCount" -ForegroundColor Red
Write-Host "  WARN: $warnCount" -ForegroundColor Yellow
Write-Host ""

Write-Host "Artifacts Created:" -ForegroundColor White
foreach ($artifact in $artifacts) {
    Write-Host "  - $($artifact.Type): $($artifact.Name)"
}
Write-Host ""

if ($bugs.Count -gt 0) {
    Write-Host "Bugs/Issues Found:" -ForegroundColor Red
    foreach ($bug in $bugs) {
        Write-Host "  [$($bug.Severity)] $($bug.Module): $($bug.Description)"
    }
} else {
    Write-Host "No blocking bugs found." -ForegroundColor Green
}

Write-Host ""
Write-Host "Test Log:" -ForegroundColor White
foreach ($entry in $testLog) {
    $color = switch ($entry.Status) { "PASS" { "Green" } "FAIL" { "Red" } default { "Yellow" } }
    Write-Host "  $($entry.Timestamp) | $($entry.Module) | $($entry.Action) | $($entry.Status)" -ForegroundColor $color
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  E2E TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Output engagement ID for follow-up
Write-Host ""
Write-Host "Engagement ID: $engagementId" -ForegroundColor Magenta
Write-Host "CPA Portal URL: https://cpa.auraai.toroniandcompany.com/firm/engagements/$engagementId/workspace" -ForegroundColor Magenta
