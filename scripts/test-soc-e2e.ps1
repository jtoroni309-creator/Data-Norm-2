#!/usr/bin/env pwsh
# SOC 2 Type II End-to-End Test Script
# Tests the SOC Copilot service at https://cpa.auraai.toroniandcompany.com

$ErrorActionPreference = "Stop"

# Configuration
$CPA_PORTAL_URL = "https://cpa.auraai.toroniandcompany.com"
$API_URL = "$CPA_PORTAL_URL/api"

# Test credentials (you'll need to provide these)
$USERNAME = "jtoroni@toroniandcompany.com"
$PASSWORD = Read-Host -Prompt "Enter password for $USERNAME" -AsSecureString
$PASSWORD_PLAIN = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($PASSWORD))

Write-Host "`n=== SOC 2 Type II E2E Test ===" -ForegroundColor Cyan

# Step 1: Login and get access token
Write-Host "`n[1/8] Logging in to CPA portal..." -ForegroundColor Yellow
$loginBody = @{
    username = $USERNAME
    password = $PASSWORD_PLAIN
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $accessToken = $loginResponse.access_token
    Write-Host "  Login successful!" -ForegroundColor Green
    Write-Host "  Token: $($accessToken.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "  Login failed: $_" -ForegroundColor Red
    exit 1
}

# Create auth headers
$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

# Step 2: Create SOC 2 Type II Engagement for HarborCloud SaaS
Write-Host "`n[2/8] Creating SOC 2 Type II engagement for HarborCloud SaaS..." -ForegroundColor Yellow
$engagementBody = @{
    client_name = "HarborCloud SaaS, Inc."
    service_description = "HarborCloud provides a B2B SaaS platform for enterprise document management, collaboration, and workflow automation. The platform is hosted on Azure cloud infrastructure in the US East region and processes sensitive business documents for enterprise customers across multiple industries."
    engagement_type = "SOC2"
    report_type = "TYPE2"
    tsc_categories = @("SECURITY", "AVAILABILITY")
    review_period_start = "2024-01-01"
    review_period_end = "2024-12-31"
    fiscal_year_end = "2024-12-31"
} | ConvertTo-Json

try {
    $engagementResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements" -Method POST -Headers $headers -Body $engagementBody
    $engagementId = $engagementResponse.id
    Write-Host "  Engagement created successfully!" -ForegroundColor Green
    Write-Host "  Engagement ID: $engagementId" -ForegroundColor Cyan
    Write-Host "  Status: $($engagementResponse.status)" -ForegroundColor Gray
} catch {
    $errorBody = $_.ErrorDetails.Message
    Write-Host "  Failed to create engagement: $_" -ForegroundColor Red
    Write-Host "  Error details: $errorBody" -ForegroundColor Red
    exit 1
}

# Step 3: List all engagements
Write-Host "`n[3/8] Listing all SOC engagements..." -ForegroundColor Yellow
try {
    $engagements = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements" -Method GET -Headers $headers
    Write-Host "  Found $($engagements.Count) engagement(s)" -ForegroundColor Green
    foreach ($eng in $engagements) {
        Write-Host "    - $($eng.client_name) ($($eng.engagement_type) $($eng.report_type)) - Status: $($eng.status)" -ForegroundColor Gray
    }
} catch {
    Write-Host "  Failed to list engagements: $_" -ForegroundColor Red
}

# Step 4: Get engagement details
Write-Host "`n[4/8] Getting engagement details..." -ForegroundColor Yellow
try {
    $engagementDetails = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId" -Method GET -Headers $headers
    Write-Host "  Client: $($engagementDetails.client_name)" -ForegroundColor Cyan
    Write-Host "  Type: $($engagementDetails.engagement_type) $($engagementDetails.report_type)" -ForegroundColor Cyan
    Write-Host "  TSC Categories: $($engagementDetails.tsc_categories -join ', ')" -ForegroundColor Cyan
    Write-Host "  Review Period: $($engagementDetails.review_period_start) to $($engagementDetails.review_period_end)" -ForegroundColor Cyan
} catch {
    Write-Host "  Failed to get engagement details: $_" -ForegroundColor Red
}

# Step 5: Transition to PLANNING status
Write-Host "`n[5/8] Transitioning engagement to PLANNING status..." -ForegroundColor Yellow
try {
    $transitionResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/transition?new_status=PLANNING" -Method POST -Headers $headers
    Write-Host "  Transition successful!" -ForegroundColor Green
    Write-Host "  New status: $($transitionResponse.status)" -ForegroundColor Cyan
} catch {
    $errorBody = $_.ErrorDetails.Message
    Write-Host "  Transition failed: $_" -ForegroundColor Red
    Write-Host "  Error details: $errorBody" -ForegroundColor Red
}

# Step 6: Create Control Objective (Security - CC6.1)
Write-Host "`n[6/8] Creating control objective CC6.1 (Logical Access)..." -ForegroundColor Yellow
$objectiveBody = @{
    objective_code = "CC6.1"
    objective_name = "Logical Access Security Controls"
    objective_description = "The entity implements logical access security controls to protect information assets from unauthorized access, including authentication mechanisms, access authorization processes, and access removal procedures."
    tsc_category = "SECURITY"
    tsc_criteria = "CC6.1"
    points_of_focus_2022 = @(
        "Identifies and authenticates users",
        "Considers network segmentation",
        "Manages credentials for infrastructure and software",
        "Restricts access credentials to authorized personnel"
    )
} | ConvertTo-Json

try {
    $objectiveResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/objectives" -Method POST -Headers $headers -Body $objectiveBody
    $objectiveId = $objectiveResponse.id
    Write-Host "  Control objective created!" -ForegroundColor Green
    Write-Host "  Objective ID: $objectiveId" -ForegroundColor Cyan
} catch {
    $errorBody = $_.ErrorDetails.Message
    Write-Host "  Failed to create objective: $_" -ForegroundColor Red
    Write-Host "  Error details: $errorBody" -ForegroundColor Red
    $objectiveId = $null
}

# Step 7: Create Control
if ($objectiveId) {
    Write-Host "`n[7/8] Creating control for CC6.1..." -ForegroundColor Yellow
    $controlBody = @{
        objective_id = $objectiveId
        control_code = "CC6.1-01"
        control_name = "Multi-Factor Authentication"
        control_description = "The organization requires multi-factor authentication (MFA) for all user access to production systems, administrative interfaces, and VPN connections."
        control_type = "Preventive"
        control_owner = "IT Security Team"
        frequency = "Continuous"
        automation_level = "Automated"
    } | ConvertTo-Json

    try {
        $controlResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/controls" -Method POST -Headers $headers -Body $controlBody
        $controlId = $controlResponse.id
        Write-Host "  Control created!" -ForegroundColor Green
        Write-Host "  Control ID: $controlId" -ForegroundColor Cyan
    } catch {
        $errorBody = $_.ErrorDetails.Message
        Write-Host "  Failed to create control: $_" -ForegroundColor Red
        Write-Host "  Error details: $errorBody" -ForegroundColor Red
        $controlId = $null
    }
}

# Step 8: Create Test Plan
if ($controlId) {
    Write-Host "`n[8/8] Creating test plan for control..." -ForegroundColor Yellow
    $testPlanBody = @{
        control_id = $controlId
        test_type = "OPERATING_EFFECTIVENESS"
        test_objective = "Verify that MFA is enforced for all user access to production systems throughout the examination period."
        test_procedures = "1. Obtain population of all users with production access.`n2. Select sample of 25 users.`n3. For each sample item, verify MFA enrollment and login activity.`n4. Review MFA bypass logs for any exceptions."
        sample_size = 25
        sampling_method = "Random"
        population_size = 150
        required_evidence_types = @("User access list", "MFA enrollment report", "Login audit logs", "Exception reports")
    } | ConvertTo-Json

    try {
        $testPlanResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/test-plans" -Method POST -Headers $headers -Body $testPlanBody
        Write-Host "  Test plan created!" -ForegroundColor Green
        Write-Host "  Test Plan ID: $($testPlanResponse.id)" -ForegroundColor Cyan
    } catch {
        $errorBody = $_.ErrorDetails.Message
        Write-Host "  Failed to create test plan: $_" -ForegroundColor Red
        Write-Host "  Error details: $errorBody" -ForegroundColor Red
    }
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Cyan
Write-Host "CPA Portal URL: $CPA_PORTAL_URL" -ForegroundColor White
Write-Host "Engagement ID: $engagementId" -ForegroundColor White
Write-Host "Client: HarborCloud SaaS, Inc." -ForegroundColor White
Write-Host "Type: SOC 2 Type II" -ForegroundColor White
Write-Host "Criteria: Security + Availability" -ForegroundColor White
Write-Host "Period: 2024-01-01 to 2024-12-31" -ForegroundColor White
Write-Host "`nWorkspace URL: $CPA_PORTAL_URL/firm/soc-engagements/$engagementId/workspace" -ForegroundColor Green
Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "1. Navigate to the workspace URL above" -ForegroundColor Gray
Write-Host "2. Complete all audit phases in the UI" -ForegroundColor Gray
Write-Host "3. Upload PBC evidence documents" -ForegroundColor Gray
Write-Host "4. Apply CPA e-signature" -ForegroundColor Gray
Write-Host "5. Download final PDF report" -ForegroundColor Gray
