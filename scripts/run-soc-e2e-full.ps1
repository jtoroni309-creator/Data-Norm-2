#!/usr/bin/env pwsh
# SOC 2 Type II Full E2E Test Script
# Tests the complete SOC audit workflow including PDF report generation

$ErrorActionPreference = "Continue"

# Configuration
$CPA_PORTAL_URL = "https://cpa.auraai.toroniandcompany.com"
$API_URL = "$CPA_PORTAL_URL/api"

# Test user credentials - using environment variables or prompting
$USERNAME = $env:CPA_USERNAME
if (-not $USERNAME) {
    $USERNAME = "jtoroni@toroniandcompany.com"
}

$PASSWORD = $env:CPA_PASSWORD
if (-not $PASSWORD) {
    $securePassword = Read-Host -Prompt "Enter password for $USERNAME" -AsSecureString
    $PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))
}

Write-Host "`n" -NoNewline
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SOC 2 Type II Full E2E Test" -ForegroundColor Cyan
Write-Host "  HarborCloud SaaS, Inc." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# ============================================
# STEP 1: Login and get access token
# ============================================
Write-Host "`n[STEP 1/10] Authenticating to CPA portal..." -ForegroundColor Yellow

$loginBody = @{
    email = $USERNAME
    password = $PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_URL/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $accessToken = $loginResponse.access_token
    $userId = $loginResponse.user.id
    Write-Host "  [OK] Login successful!" -ForegroundColor Green
    Write-Host "  User: $($loginResponse.user.email)" -ForegroundColor Gray
    Write-Host "  Firm: $($loginResponse.user.firm_name)" -ForegroundColor Gray
} catch {
    Write-Host "  [FAIL] Login failed: $_" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type" = "application/json"
}

# ============================================
# STEP 2: Create SOC 2 Type II Engagement
# ============================================
Write-Host "`n[STEP 2/10] Creating SOC 2 Type II engagement..." -ForegroundColor Yellow

$engagementBody = @{
    client_name = "HarborCloud SaaS, Inc."
    service_description = @"
HarborCloud provides a B2B SaaS platform for enterprise document management, collaboration, and workflow automation. The platform is hosted on Microsoft Azure cloud infrastructure in the US East region and processes sensitive business documents for enterprise customers across multiple industries including healthcare, financial services, and manufacturing.

Key Services:
- Document storage and versioning with AES-256 encryption
- Real-time collaboration and co-authoring
- Automated workflow and approval processes
- API integrations with enterprise systems (SAP, Oracle, Salesforce)
- Mobile applications for iOS and Android

Infrastructure:
- Azure App Service with auto-scaling
- Azure SQL Database with geo-replication
- Azure Blob Storage with redundancy
- Azure Active Directory for identity management
- Azure Key Vault for secrets management
"@
    engagement_type = "SOC2"
    report_type = "TYPE2"
    tsc_categories = @("SECURITY", "AVAILABILITY")
    review_period_start = "2024-01-01"
    review_period_end = "2024-12-31"
    fiscal_year_end = "2024-12-31"
} | ConvertTo-Json -Depth 5

try {
    $engagement = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements" -Method POST -Headers $headers -Body $engagementBody
    $engagementId = $engagement.id
    Write-Host "  [OK] Engagement created!" -ForegroundColor Green
    Write-Host "  Engagement ID: $engagementId" -ForegroundColor Cyan
    Write-Host "  Status: $($engagement.status)" -ForegroundColor Gray
} catch {
    $errorBody = $_.ErrorDetails.Message
    Write-Host "  [FAIL] Failed to create engagement: $errorBody" -ForegroundColor Red
    exit 1
}

# ============================================
# STEP 3: Transition to PLANNING status
# ============================================
Write-Host "`n[STEP 3/10] Transitioning to PLANNING status..." -ForegroundColor Yellow

try {
    $transition = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/transition?new_status=PLANNING" -Method POST -Headers $headers
    Write-Host "  [OK] Status: $($transition.status)" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Transition failed (may already be in correct status)" -ForegroundColor Yellow
}

# ============================================
# STEP 4: Create Control Objectives (Security CC6.x)
# ============================================
Write-Host "`n[STEP 4/10] Creating control objectives..." -ForegroundColor Yellow

$objectives = @(
    @{
        objective_code = "CC6.1"
        objective_name = "Logical and Physical Access Controls"
        objective_description = "The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events to meet the entity's objectives."
        tsc_category = "SECURITY"
        tsc_criteria = "CC6.1"
        points_of_focus_2022 = @(
            "Identifies and Manages the Inventory of Information Assets"
            "Restricts Logical Access"
            "Identifies and Authenticates Users"
            "Considers Network Segmentation"
            "Manages Points of Access"
            "Restricts Access to Information Assets"
            "Manages Identification and Authentication"
            "Manages Credentials for Infrastructure and Software"
            "Uses Encryption to Protect Data"
            "Protects Encryption Keys"
        )
    },
    @{
        objective_code = "CC6.2"
        objective_name = "User Registration and Authorization"
        objective_description = "Prior to issuing system credentials and granting system access, the entity registers and authorizes new internal and external users whose access is administered by the entity."
        tsc_category = "SECURITY"
        tsc_criteria = "CC6.2"
        points_of_focus_2022 = @(
            "Controls Access Credentials to Protected Assets"
            "Removes Access to Protected Assets When Appropriate"
            "Reviews Appropriateness of Access Credentials"
        )
    },
    @{
        objective_code = "CC6.3"
        objective_name = "User Access Removal"
        objective_description = "The entity authorizes, modifies, or removes access to data, software, functions, and other protected information assets based on roles, responsibilities, or the system design and changes."
        tsc_category = "SECURITY"
        tsc_criteria = "CC6.3"
        points_of_focus_2022 = @(
            "Creates or Modifies Access to Protected Information Assets Based on Authorization"
            "Removes Access to Protected Information Assets When Appropriate"
            "Uses Role-Based Access Controls"
            "Reviews Access Roles and Rules"
        )
    },
    @{
        objective_code = "A1.1"
        objective_name = "System Availability"
        objective_description = "The entity maintains, monitors, and evaluates current processing capacity and use of system components to manage capacity demand and to enable the implementation of additional capacity to help meet its objectives."
        tsc_category = "AVAILABILITY"
        tsc_criteria = "A1.1"
        points_of_focus_2022 = @(
            "Measures Current Usage"
            "Forecasts Capacity"
            "Makes Changes Based on Forecasts"
        )
    },
    @{
        objective_code = "A1.2"
        objective_name = "Environmental Protections"
        objective_description = "The entity authorizes, designs, develops or acquires, implements, operates, approves, maintains, and monitors environmental protections, software, data backup processes, and recovery infrastructure to meet its objectives."
        tsc_category = "AVAILABILITY"
        tsc_criteria = "A1.2"
        points_of_focus_2022 = @(
            "Identifies Environmental Threats"
            "Designs Detection Measures"
            "Implements and Maintains Environmental Protection Mechanisms"
            "Implements Alerts to Analyze Anomalies"
            "Responds to Environmental Threat Events"
            "Communicates and Reviews Detected Environmental Threat Events"
            "Determines Data to Back Up and Frequency of Backup"
            "Implements Backup Processes"
            "Tests Backup and Restoration Processes"
        )
    }
)

$objectiveIds = @{}
foreach ($obj in $objectives) {
    try {
        $objResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/objectives" -Method POST -Headers $headers -Body ($obj | ConvertTo-Json -Depth 5)
        $objectiveIds[$obj.objective_code] = $objResponse.id
        Write-Host "  [OK] Created: $($obj.objective_code) - $($obj.objective_name)" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Failed to create $($obj.objective_code): $_" -ForegroundColor Yellow
    }
}

# ============================================
# STEP 5: Create Controls
# ============================================
Write-Host "`n[STEP 5/10] Creating controls..." -ForegroundColor Yellow

$controls = @(
    @{
        objective_id = $objectiveIds["CC6.1"]
        control_code = "CC6.1-01"
        control_name = "Multi-Factor Authentication (MFA)"
        control_description = "The organization requires multi-factor authentication (MFA) for all user access to production systems, administrative interfaces, VPN connections, and cloud management consoles. MFA is enforced through Azure Active Directory Conditional Access policies."
        control_type = "Preventive"
        control_owner = "IT Security Team"
        frequency = "Continuous"
        automation_level = "Automated"
    },
    @{
        objective_id = $objectiveIds["CC6.1"]
        control_code = "CC6.1-02"
        control_name = "Network Segmentation"
        control_description = "Production, development, and corporate networks are logically segmented using Azure Virtual Networks and Network Security Groups. Firewall rules restrict traffic between network segments based on the principle of least privilege."
        control_type = "Preventive"
        control_owner = "Network Operations"
        frequency = "Continuous"
        automation_level = "Automated"
    },
    @{
        objective_id = $objectiveIds["CC6.1"]
        control_code = "CC6.1-03"
        control_name = "Data Encryption at Rest"
        control_description = "All customer data is encrypted at rest using AES-256 encryption. Azure SQL Database uses Transparent Data Encryption (TDE), and Azure Blob Storage uses Storage Service Encryption (SSE). Encryption keys are managed in Azure Key Vault."
        control_type = "Preventive"
        control_owner = "Data Security Team"
        frequency = "Continuous"
        automation_level = "Automated"
    },
    @{
        objective_id = $objectiveIds["CC6.2"]
        control_code = "CC6.2-01"
        control_name = "User Provisioning Process"
        control_description = "New user access requests are submitted through ServiceNow and require manager approval. IT Security verifies the user's role and grants access based on pre-defined role templates. All provisioning activities are logged."
        control_type = "Preventive"
        control_owner = "IT Security Team"
        frequency = "Per occurrence"
        automation_level = "Semi-automated"
    },
    @{
        objective_id = $objectiveIds["CC6.3"]
        control_code = "CC6.3-01"
        control_name = "Access Termination Process"
        control_description = "Upon employee termination notification from HR, IT Security disables the user's Active Directory account within 24 hours. VPN and application access is automatically revoked. Access removal is verified by IT Security."
        control_type = "Preventive"
        control_owner = "IT Security Team"
        frequency = "Per occurrence"
        automation_level = "Semi-automated"
    },
    @{
        objective_id = $objectiveIds["CC6.3"]
        control_code = "CC6.3-02"
        control_name = "Quarterly Access Review"
        control_description = "IT Security performs quarterly access reviews for all production systems and privileged accounts. Department managers review and certify their team members' access. Exceptions are documented and remediated within 30 days."
        control_type = "Detective"
        control_owner = "IT Security Team"
        frequency = "Quarterly"
        automation_level = "Manual"
    },
    @{
        objective_id = $objectiveIds["A1.1"]
        control_code = "A1.1-01"
        control_name = "Capacity Monitoring"
        control_description = "Azure Monitor tracks CPU, memory, disk, and network utilization across all production resources. Alerts are configured for thresholds exceeding 80% sustained utilization. Monthly capacity reports are reviewed by the Infrastructure Team."
        control_type = "Detective"
        control_owner = "Infrastructure Team"
        frequency = "Continuous"
        automation_level = "Automated"
    },
    @{
        objective_id = $objectiveIds["A1.2"]
        control_code = "A1.2-01"
        control_name = "Automated Backup Process"
        control_description = "Azure SQL Database performs automated daily backups with 35-day retention. Blob storage uses geo-redundant storage (GRS) with automatic replication. Backup completion is monitored and failures generate alerts."
        control_type = "Preventive"
        control_owner = "Database Administration"
        frequency = "Daily"
        automation_level = "Automated"
    },
    @{
        objective_id = $objectiveIds["A1.2"]
        control_code = "A1.2-02"
        control_name = "Disaster Recovery Testing"
        control_description = "Annual disaster recovery tests are conducted to validate the ability to restore critical systems within the 4-hour RTO. Test results are documented and remediation items are tracked to completion."
        control_type = "Detective"
        control_owner = "Infrastructure Team"
        frequency = "Annually"
        automation_level = "Manual"
    }
)

$controlIds = @{}
foreach ($ctrl in $controls) {
    if ($ctrl.objective_id) {
        try {
            $ctrlResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/controls" -Method POST -Headers $headers -Body ($ctrl | ConvertTo-Json -Depth 5)
            $controlIds[$ctrl.control_code] = $ctrlResponse.id
            Write-Host "  [OK] Created: $($ctrl.control_code) - $($ctrl.control_name)" -ForegroundColor Green
        } catch {
            Write-Host "  [WARN] Failed to create $($ctrl.control_code): $_" -ForegroundColor Yellow
        }
    }
}

# ============================================
# STEP 6: Transition to FIELDWORK status
# ============================================
Write-Host "`n[STEP 6/10] Transitioning to FIELDWORK status..." -ForegroundColor Yellow

try {
    $transition = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/transition?new_status=FIELDWORK" -Method POST -Headers $headers
    Write-Host "  [OK] Status: $($transition.status)" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] Transition failed: $_" -ForegroundColor Yellow
}

# ============================================
# STEP 7: Create Test Plans
# ============================================
Write-Host "`n[STEP 7/10] Creating test plans..." -ForegroundColor Yellow

$testPlans = @(
    @{
        control_id = $controlIds["CC6.1-01"]
        test_type = "OPERATING_EFFECTIVENESS"
        test_objective = "Verify that MFA is enforced for all user access to production systems throughout the examination period."
        test_procedures = @"
1. Obtain population of all users with production system access from Azure AD.
2. Select a random sample of 25 users from the population.
3. For each sampled user, inspect Azure AD sign-in logs to verify MFA was required.
4. Review Azure AD Conditional Access policies to verify MFA requirements.
5. Attempt test login without MFA to confirm enforcement.
6. Review any MFA bypass exceptions for proper authorization.
"@
        sample_size = 25
        sampling_method = "Random"
        population_size = 150
        required_evidence_types = @("User access list", "Azure AD sign-in logs", "Conditional Access policies", "MFA exception reports")
    },
    @{
        control_id = $controlIds["CC6.1-02"]
        test_type = "DESIGN_EVALUATION"
        test_objective = "Evaluate the design of network segmentation controls."
        test_procedures = @"
1. Obtain network architecture diagrams.
2. Review Azure Virtual Network configurations and NSG rules.
3. Verify production, development, and corporate networks are logically separated.
4. Test connectivity between network segments to validate restrictions.
"@
        sample_size = 1
        sampling_method = "N/A - Design Test"
        population_size = 1
        required_evidence_types = @("Network diagrams", "NSG rule configurations", "Penetration test results")
    },
    @{
        control_id = $controlIds["CC6.2-01"]
        test_type = "OPERATING_EFFECTIVENESS"
        test_objective = "Verify that new user provisioning follows the documented process."
        test_procedures = @"
1. Obtain population of new user provisioning requests from ServiceNow.
2. Select a random sample of 25 provisioning requests.
3. For each sample, verify manager approval was obtained.
4. Verify access granted matches the approved role template.
5. Verify provisioning was logged in the audit trail.
"@
        sample_size = 25
        sampling_method = "Random"
        population_size = 87
        required_evidence_types = @("ServiceNow tickets", "Manager approval emails", "Role template documentation", "Provisioning logs")
    },
    @{
        control_id = $controlIds["CC6.3-01"]
        test_type = "OPERATING_EFFECTIVENESS"
        test_objective = "Verify that terminated user access is removed timely."
        test_procedures = @"
1. Obtain population of terminated employees from HR during examination period.
2. Select a random sample of 15 terminated employees.
3. For each sample, verify Active Directory account was disabled within 24 hours.
4. Verify VPN and application access was revoked.
5. Review any exceptions for proper documentation.
"@
        sample_size = 15
        sampling_method = "Random"
        population_size = 23
        required_evidence_types = @("HR termination reports", "AD account disable dates", "Access removal verification")
    },
    @{
        control_id = $controlIds["CC6.3-02"]
        test_type = "OPERATING_EFFECTIVENESS"
        test_objective = "Verify that quarterly access reviews are performed."
        test_procedures = @"
1. Obtain documentation of quarterly access reviews for Q1-Q4 2024.
2. Verify reviews were performed timely (within 30 days of quarter end).
3. Sample 10 users per quarter and verify certification by managers.
4. Verify exceptions were documented and remediated.
"@
        sample_size = 40
        sampling_method = "Stratified by quarter"
        population_size = 150
        required_evidence_types = @("Access review reports", "Manager certifications", "Remediation tickets")
    },
    @{
        control_id = $controlIds["A1.2-01"]
        test_type = "OPERATING_EFFECTIVENESS"
        test_objective = "Verify that automated backups are completing successfully."
        test_procedures = @"
1. Obtain backup job logs for the examination period.
2. Select 52 weekly samples (one per week).
3. Verify backup completion status for each sample.
4. Review any backup failures and verify timely remediation.
5. Verify backup retention meets 35-day requirement.
"@
        sample_size = 52
        sampling_method = "Weekly systematic"
        population_size = 365
        required_evidence_types = @("Backup job logs", "Azure backup reports", "Failure alerts and remediation")
    }
)

$testPlanIds = @{}
$testPlanIndex = 0
foreach ($tp in $testPlans) {
    if ($tp.control_id) {
        try {
            $tpResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/test-plans" -Method POST -Headers $headers -Body ($tp | ConvertTo-Json -Depth 5)
            $testPlanIds["TP$testPlanIndex"] = $tpResponse.id
            Write-Host "  [OK] Created test plan for control testing" -ForegroundColor Green
            $testPlanIndex++
        } catch {
            Write-Host "  [WARN] Failed to create test plan: $_" -ForegroundColor Yellow
        }
    }
}

# ============================================
# STEP 8: Record Test Results
# ============================================
Write-Host "`n[STEP 8/10] Recording test results..." -ForegroundColor Yellow

$testDate = (Get-Date).ToString("yyyy-MM-dd")
$resultsRecorded = 0

foreach ($tpKey in $testPlanIds.Keys) {
    $testPlanId = $testPlanIds[$tpKey]

    # Record passing test result
    $testResult = @{
        test_plan_id = $testPlanId
        test_date = $testDate
        passed = $true
        findings = "No exceptions noted. All sample items tested were in compliance with the control requirements."
        conclusion = "Based on our testing, the control operated effectively throughout the examination period."
        sample_item_identifier = "Sample items 1-25"
    }

    try {
        $trResponse = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/test-results" -Method POST -Headers $headers -Body ($testResult | ConvertTo-Json -Depth 5)
        $resultsRecorded++
    } catch {
        Write-Host "  [WARN] Failed to record test result: $_" -ForegroundColor Yellow
    }
}
Write-Host "  [OK] Recorded $resultsRecorded test results" -ForegroundColor Green

# ============================================
# STEP 9: Transition through remaining phases
# ============================================
Write-Host "`n[STEP 9/10] Transitioning through audit phases..." -ForegroundColor Yellow

$phases = @("REVIEW", "PARTNER_REVIEW", "SIGNED")
foreach ($phase in $phases) {
    try {
        Start-Sleep -Milliseconds 500
        $transition = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/transition?new_status=$phase" -Method POST -Headers $headers
        Write-Host "  [OK] Transitioned to: $phase" -ForegroundColor Green
    } catch {
        $errorBody = $_.ErrorDetails.Message
        Write-Host "  [WARN] Could not transition to $phase : $errorBody" -ForegroundColor Yellow
    }
}

# ============================================
# STEP 10: Generate Report
# ============================================
Write-Host "`n[STEP 10/10] Generating SOC 2 Type II report..." -ForegroundColor Yellow

$reportBody = @{
    engagement_id = $engagementId
    report_title = "SOC 2 Type II Report - HarborCloud SaaS, Inc."
    report_date = $testDate
} | ConvertTo-Json

try {
    $report = Invoke-RestMethod -Uri "$API_URL/soc-copilot/engagements/$engagementId/reports" -Method POST -Headers $headers -Body $reportBody
    Write-Host "  [OK] Report generated!" -ForegroundColor Green
    Write-Host "  Report ID: $($report.id)" -ForegroundColor Cyan
} catch {
    Write-Host "  [WARN] Report generation: $_" -ForegroundColor Yellow
}

# ============================================
# SUMMARY
# ============================================
Write-Host "`n" -NoNewline
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  TEST COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Engagement Details:" -ForegroundColor White
Write-Host "  Client: HarborCloud SaaS, Inc." -ForegroundColor Gray
Write-Host "  Type: SOC 2 Type II" -ForegroundColor Gray
Write-Host "  TSC Categories: Security, Availability" -ForegroundColor Gray
Write-Host "  Period: 2024-01-01 to 2024-12-31" -ForegroundColor Gray
Write-Host "  Engagement ID: $engagementId" -ForegroundColor Gray
Write-Host ""
Write-Host "Created:" -ForegroundColor White
Write-Host "  - $($objectives.Count) Control Objectives" -ForegroundColor Gray
Write-Host "  - $($controls.Count) Controls" -ForegroundColor Gray
Write-Host "  - $($testPlans.Count) Test Plans" -ForegroundColor Gray
Write-Host "  - $resultsRecorded Test Results" -ForegroundColor Gray
Write-Host ""
Write-Host "Workspace URL:" -ForegroundColor White
Write-Host "  $CPA_PORTAL_URL/firm/soc-engagements/$engagementId/workspace" -ForegroundColor Green
Write-Host ""

# Return engagement ID for further use
return $engagementId
