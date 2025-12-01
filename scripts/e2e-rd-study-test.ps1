# End-to-End R&D Study System Test
# Simulates a client going through the complete R&D Study workflow

$ErrorActionPreference = "Continue"

# API URLs
$rdStudyUrl = "https://rdclient.auraai.toroniandcompany.com/api/rd-study"
$identityUrl = "https://rdclient.auraai.toroniandcompany.com/api/identity"
$cpaUrl = "https://cpa.auraai.toroniandcompany.com/api"

# Test data
$testEmail = "e2e-test-client@toroni.com"
$testPassword = "E2ETest2024!"
$testCompany = "Advanced Tech Solutions LLC"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  R&D Study End-to-End System Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================
# STEP 1: Client Authentication
# ============================================
Write-Host "=== STEP 1: Client Authentication ===" -ForegroundColor Yellow

# Try login with existing test user
$loginPayload = @{
    email = "prodtestuser@toroni.com"
    password = "TestPass123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
    $token = $loginResponse.access_token
    Write-Host "[PASS] Login successful: $($loginResponse.user.full_name)" -ForegroundColor Green
    Write-Host "       User ID: $($loginResponse.user.id)" -ForegroundColor Gray
    Write-Host "       Email: $($loginResponse.user.email)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Login failed: $_" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# ============================================
# STEP 2: Create New R&D Study with Company Info
# ============================================
Write-Host ""
Write-Host "=== STEP 2: Create R&D Study (Client Onboarding) ===" -ForegroundColor Yellow

$studyPayload = @{
    name = "Advanced Tech Solutions R&D Study 2024"
    entity_name = $testCompany
    ein = "98-7654321"
    tax_year = 2024
    entity_type = "c_corp"
    fiscal_year_start = "2024-01-01"
    fiscal_year_end = "2024-12-31"
    states = @("CA", "TX", "NY", "FL")
    is_controlled_group = $false
    current_year_gross_receipts = 12500000
    naics_code = "541512"
    description = "Software development and AI/ML solutions for enterprise clients"
} | ConvertTo-Json

try {
    $studyResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies" -Method POST -Headers $headers -Body $studyPayload
    $studyId = $studyResponse.id
    Write-Host "[PASS] Study created successfully" -ForegroundColor Green
    Write-Host "       Study ID: $studyId" -ForegroundColor Gray
    Write-Host "       Entity: $($studyResponse.entity_name)" -ForegroundColor Gray
    Write-Host "       Tax Year: $($studyResponse.tax_year)" -ForegroundColor Gray
} catch {
    Write-Host "[FAIL] Study creation failed: $_" -ForegroundColor Red
    exit 1
}

# ============================================
# STEP 3: Add R&D Projects
# ============================================
Write-Host ""
Write-Host "=== STEP 3: Add R&D Projects ===" -ForegroundColor Yellow

$projects = @(
    @{
        name = "AI-Powered Document Intelligence Platform"
        code = "PROJ-AI-001"
        description = "Development of a novel machine learning system that uses transformer-based neural networks to automatically extract, classify, and analyze structured and unstructured data from complex financial documents. The system employs custom attention mechanisms and domain-specific pre-training to achieve unprecedented accuracy in entity extraction and relationship mapping. Key technical challenges include handling multi-format documents, maintaining context across hundreds of pages, and developing novel algorithms for table structure recognition."
        department = "AI Research"
        business_component = "Document Analysis Engine"
        start_date = "2024-01-15"
        end_date = "2024-12-31"
    },
    @{
        name = "Real-Time Fraud Detection System"
        code = "PROJ-FRD-002"
        description = "Research and development of an advanced fraud detection system utilizing graph neural networks and anomaly detection algorithms. The project involves developing novel techniques for identifying fraudulent patterns in high-velocity transaction streams. Technical uncertainties include real-time processing of millions of transactions per second, development of adaptive learning algorithms that evolve with new fraud patterns, and creating explainable AI models for regulatory compliance."
        department = "Security Engineering"
        business_component = "Transaction Monitoring"
        start_date = "2024-02-01"
        end_date = "2024-12-31"
    },
    @{
        name = "Cloud-Native Infrastructure Automation"
        code = "PROJ-CLD-003"
        description = "Development of innovative infrastructure-as-code solutions for automated cloud resource management. This project explores new approaches to declarative infrastructure definition, self-healing systems, and predictive scaling algorithms. Technical challenges include developing consistent abstraction layers across multiple cloud providers, creating novel optimization algorithms for cost-performance tradeoffs, and implementing zero-downtime deployment strategies for complex distributed systems."
        department = "Platform Engineering"
        business_component = "DevOps Platform"
        start_date = "2024-03-01"
        end_date = "2024-12-31"
    }
)

$projectIds = @()
foreach ($proj in $projects) {
    $projPayload = $proj | ConvertTo-Json
    try {
        $projResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/projects" -Method POST -Headers $headers -Body $projPayload
        $projectIds += $projResponse.id
        Write-Host "[PASS] Project added: $($proj.name)" -ForegroundColor Green
        Write-Host "       Project ID: $($projResponse.id)" -ForegroundColor Gray
    } catch {
        Write-Host "[WARN] Project creation failed for $($proj.name): $_" -ForegroundColor Yellow
    }
}

# ============================================
# STEP 4: Add Employee Expenses (W-2 Wages)
# ============================================
Write-Host ""
Write-Host "=== STEP 4: Add Employee Expenses ===" -ForegroundColor Yellow

$employees = @(
    @{ employee_id = "EMP-001"; name = "Dr. James Chen"; title = "Chief AI Scientist"; department = "AI Research"; total_wages = 285000; w2_wages = 285000; qualified_time_percentage = 85; qualified_time_source = "time_study"; project_id = $projectIds[0] },
    @{ employee_id = "EMP-002"; name = "Dr. Maria Santos"; title = "Senior ML Engineer"; department = "AI Research"; total_wages = 225000; w2_wages = 225000; qualified_time_percentage = 90; qualified_time_source = "time_study"; project_id = $projectIds[0] },
    @{ employee_id = "EMP-003"; name = "Robert Williams"; title = "Principal Software Architect"; department = "Platform Engineering"; total_wages = 245000; w2_wages = 245000; qualified_time_percentage = 75; qualified_time_source = "project_records"; project_id = $projectIds[2] },
    @{ employee_id = "EMP-004"; name = "Sarah Johnson"; title = "Senior Security Engineer"; department = "Security Engineering"; total_wages = 195000; w2_wages = 195000; qualified_time_percentage = 80; qualified_time_source = "time_study"; project_id = $projectIds[1] },
    @{ employee_id = "EMP-005"; name = "David Park"; title = "Research Engineer"; department = "AI Research"; total_wages = 175000; w2_wages = 175000; qualified_time_percentage = 95; qualified_time_source = "time_study"; project_id = $projectIds[0] },
    @{ employee_id = "EMP-006"; name = "Emily Thompson"; title = "Software Engineer"; department = "Platform Engineering"; total_wages = 155000; w2_wages = 155000; qualified_time_percentage = 70; qualified_time_source = "project_records"; project_id = $projectIds[2] },
    @{ employee_id = "EMP-007"; name = "Michael Brown"; title = "Data Scientist"; department = "AI Research"; total_wages = 185000; w2_wages = 185000; qualified_time_percentage = 88; qualified_time_source = "time_study"; project_id = $projectIds[0] },
    @{ employee_id = "EMP-008"; name = "Jennifer Lee"; title = "DevOps Engineer"; department = "Platform Engineering"; total_wages = 165000; w2_wages = 165000; qualified_time_percentage = 65; qualified_time_source = "project_records"; project_id = $projectIds[2] }
)

$totalWageQRE = 0
foreach ($emp in $employees) {
    $empPayload = $emp | ConvertTo-Json
    try {
        $empResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/employees" -Method POST -Headers $headers -Body $empPayload
        $qualifiedWages = [decimal]$empResponse.qualified_wages
        $totalWageQRE += $qualifiedWages
        Write-Host "[PASS] Employee added: $($emp.name) - QRE: $([string]::Format('{0:C0}', $qualifiedWages))" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Employee add failed for $($emp.name): $_" -ForegroundColor Yellow
    }
}
Write-Host "       Total Wage QRE: $([string]::Format('{0:C0}', $totalWageQRE))" -ForegroundColor Cyan

# ============================================
# STEP 5: Add Subcontractor Expenses (Contract Research)
# ============================================
Write-Host ""
Write-Host "=== STEP 5: Add Subcontractor Expenses ===" -ForegroundColor Yellow

$contractors = @(
    @{
        category = "contract_research"
        subcategory = "Third-party contractor"
        gross_amount = 185000
        qualified_percentage = 65
        contractor_name = "DeepMind Consulting LLC"
        is_qualified_research_org = $false
        contract_percentage = 65
        project_id = $projectIds[0]
        supply_description = "AI Model Architecture Consulting and Development"
    },
    @{
        category = "contract_research"
        subcategory = "University research"
        gross_amount = 250000
        qualified_percentage = 100
        contractor_name = "Stanford University AI Lab"
        is_qualified_research_org = $true
        contract_percentage = 100
        project_id = $projectIds[0]
        supply_description = "Collaborative Research on Transformer Architectures"
    },
    @{
        category = "contract_research"
        subcategory = "Third-party contractor"
        gross_amount = 125000
        qualified_percentage = 65
        contractor_name = "CyberDefense Research Inc."
        is_qualified_research_org = $false
        contract_percentage = 65
        project_id = $projectIds[1]
        supply_description = "Advanced Threat Detection Algorithm Development"
    },
    @{
        category = "contract_research"
        subcategory = "Third-party contractor"
        gross_amount = 95000
        qualified_percentage = 65
        contractor_name = "CloudOps Innovations"
        is_qualified_research_org = $false
        contract_percentage = 65
        project_id = $projectIds[2]
        supply_description = "Multi-Cloud Infrastructure Optimization Research"
    }
)

$totalContractQRE = 0
foreach ($contractor in $contractors) {
    $qrePayload = $contractor | ConvertTo-Json
    try {
        $qreResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/qres" -Method POST -Headers $headers -Body $qrePayload
        $qualifiedAmount = [decimal]$qreResponse.qualified_amount
        $totalContractQRE += $qualifiedAmount
        Write-Host "[PASS] Contractor added: $($contractor.contractor_name) - QRE: $([string]::Format('{0:C0}', $qualifiedAmount))" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Contractor add failed: $_" -ForegroundColor Yellow
    }
}
Write-Host "       Total Contract QRE: $([string]::Format('{0:C0}', $totalContractQRE))" -ForegroundColor Cyan

# ============================================
# STEP 6: Add Supplies Expenses
# ============================================
Write-Host ""
Write-Host "=== STEP 6: Add Supplies Expenses ===" -ForegroundColor Yellow

$supplies = @(
    @{
        category = "supplies"
        subcategory = "Computing hardware"
        gross_amount = 145000
        qualified_percentage = 100
        supply_description = "NVIDIA H100 GPUs and high-performance server components for AI training clusters"
        supply_vendor = "NVIDIA Corporation"
        project_id = $projectIds[0]
    },
    @{
        category = "supplies"
        subcategory = "Development equipment"
        gross_amount = 85000
        qualified_percentage = 90
        supply_description = "High-end workstations, development servers, and specialized testing equipment"
        supply_vendor = "Dell Technologies"
        project_id = $projectIds[2]
    },
    @{
        category = "supplies"
        subcategory = "Laboratory supplies"
        gross_amount = 35000
        qualified_percentage = 100
        supply_description = "Prototype hardware components, sensors, and testing materials for IoT integration"
        supply_vendor = "Various Vendors"
        project_id = $projectIds[1]
    },
    @{
        category = "supplies"
        subcategory = "Software licenses"
        gross_amount = 65000
        qualified_percentage = 85
        supply_description = "Specialized ML frameworks, development tools, and research software licenses"
        supply_vendor = "Multiple Software Vendors"
        project_id = $projectIds[0]
    }
)

$totalSupplyQRE = 0
foreach ($supply in $supplies) {
    $qrePayload = $supply | ConvertTo-Json
    try {
        $qreResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/qres" -Method POST -Headers $headers -Body $qrePayload
        $qualifiedAmount = [decimal]$qreResponse.qualified_amount
        $totalSupplyQRE += $qualifiedAmount
        Write-Host "[PASS] Supply added: $($supply.supply_description.Substring(0, [Math]::Min(50, $supply.supply_description.Length)))... - QRE: $([string]::Format('{0:C0}', $qualifiedAmount))" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Supply add failed: $_" -ForegroundColor Yellow
    }
}
Write-Host "       Total Supply QRE: $([string]::Format('{0:C0}', $totalSupplyQRE))" -ForegroundColor Cyan

# ============================================
# STEP 7: Add Computer Rental Expenses (Cloud Computing)
# ============================================
Write-Host ""
Write-Host "=== STEP 7: Add Computer Rental Expenses ===" -ForegroundColor Yellow

$computerRentals = @(
    @{
        category = "supplies"
        subcategory = "Cloud computing"
        gross_amount = 285000
        qualified_percentage = 85
        supply_description = "AWS SageMaker and EC2 instances for distributed model training and inference workloads"
        supply_vendor = "Amazon Web Services"
        project_id = $projectIds[0]
    },
    @{
        category = "supplies"
        subcategory = "Cloud computing"
        gross_amount = 195000
        qualified_percentage = 80
        supply_description = "Google Cloud TPU clusters and Vertex AI platform for advanced ML experiments"
        supply_vendor = "Google Cloud Platform"
        project_id = $projectIds[0]
    },
    @{
        category = "supplies"
        subcategory = "Cloud computing"
        gross_amount = 165000
        qualified_percentage = 90
        supply_description = "Azure Kubernetes Service and Azure ML for cloud-native platform development"
        supply_vendor = "Microsoft Azure"
        project_id = $projectIds[2]
    },
    @{
        category = "supplies"
        subcategory = "Cloud computing"
        gross_amount = 75000
        qualified_percentage = 85
        supply_description = "Specialized GPU cloud instances for security testing and threat simulation"
        supply_vendor = "Various Cloud Providers"
        project_id = $projectIds[1]
    }
)

$totalCloudQRE = 0
foreach ($rental in $computerRentals) {
    $qrePayload = $rental | ConvertTo-Json
    try {
        $qreResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/qres" -Method POST -Headers $headers -Body $qrePayload
        $qualifiedAmount = [decimal]$qreResponse.qualified_amount
        $totalCloudQRE += $qualifiedAmount
        Write-Host "[PASS] Cloud compute added: $($rental.supply_vendor) - QRE: $([string]::Format('{0:C0}', $qualifiedAmount))" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Cloud compute add failed: $_" -ForegroundColor Yellow
    }
}
Write-Host "       Total Cloud Computing QRE: $([string]::Format('{0:C0}', $totalCloudQRE))" -ForegroundColor Cyan

# ============================================
# STEP 8: Summary Before AI Analysis
# ============================================
Write-Host ""
Write-Host "=== QRE Summary Before AI Analysis ===" -ForegroundColor Magenta
$totalQRE = $totalWageQRE + $totalContractQRE + $totalSupplyQRE + $totalCloudQRE
Write-Host "  Employee Wages QRE:    $([string]::Format('{0:C0}', $totalWageQRE))"
Write-Host "  Contract Research QRE: $([string]::Format('{0:C0}', $totalContractQRE))"
Write-Host "  Supplies QRE:          $([string]::Format('{0:C0}', $totalSupplyQRE))"
Write-Host "  Cloud Computing QRE:   $([string]::Format('{0:C0}', $totalCloudQRE))"
Write-Host "  -----------------------------------"
Write-Host "  TOTAL ESTIMATED QRE:   $([string]::Format('{0:C0}', $totalQRE))" -ForegroundColor Cyan
Write-Host ""

# ============================================
# STEP 9: Run AI Complete Study (GPT-4 Turbo)
# ============================================
Write-Host "=== STEP 9: Running AI Complete Study (GPT-4 Turbo) ===" -ForegroundColor Yellow
Write-Host "       This may take 30-60 seconds..." -ForegroundColor Gray

try {
    $aiStartTime = Get-Date
    $aiResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/ai/complete-study" -Method POST -Headers $headers -TimeoutSec 300
    $aiEndTime = Get-Date
    $aiDuration = ($aiEndTime - $aiStartTime).TotalSeconds

    Write-Host "[PASS] AI Study Completed in $([math]::Round($aiDuration, 1)) seconds" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== AI Study Results ===" -ForegroundColor Magenta
    Write-Host "  Total QRE:              $($aiResponse.total_qre)"
    Write-Host "  Federal Credit (Regular): $($aiResponse.federal_credit_regular)"
    Write-Host "  Federal Credit (ASC):     $($aiResponse.federal_credit_asc)"
    Write-Host "  Selected Method:          $($aiResponse.selected_method)"
    Write-Host "  Final Federal Credit:     $($aiResponse.federal_credit_final)"
    Write-Host "  Total State Credits:      $($aiResponse.total_state_credits)"
    Write-Host "  -----------------------------------"
    Write-Host "  TOTAL CREDITS:            $($aiResponse.total_credits)" -ForegroundColor Green
} catch {
    Write-Host "[FAIL] AI Complete Study failed: $_" -ForegroundColor Red
}

# ============================================
# STEP 10: Check Project Qualification Results
# ============================================
Write-Host ""
Write-Host "=== STEP 10: Project Qualification Results ===" -ForegroundColor Yellow

try {
    $projectsResult = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/projects" -Headers $headers
    foreach ($proj in $projectsResult) {
        Write-Host ""
        Write-Host "Project: $($proj.name)" -ForegroundColor Cyan
        Write-Host "  Status: $($proj.qualification_status)" -ForegroundColor $(if ($proj.qualification_status -eq "qualified") { "Green" } else { "Yellow" })
        Write-Host "  Overall Score: $($proj.overall_score)"

        if ($proj.permitted_purpose_score) {
            Write-Host "  IRS 4-Part Test Scores:" -ForegroundColor Gray
            Write-Host "    - Permitted Purpose:     $($proj.permitted_purpose_score)"
            Write-Host "    - Technological Nature:  $($proj.technological_nature_score)"
            Write-Host "    - Uncertainty:           $($proj.uncertainty_score)"
            Write-Host "    - Experimentation:       $($proj.experimentation_score)"
        }
    }
} catch {
    Write-Host "[WARN] Could not fetch project results: $_" -ForegroundColor Yellow
}

# ============================================
# STEP 11: Generate Output Files
# ============================================
Write-Host ""
Write-Host "=== STEP 11: Generate Output Files ===" -ForegroundColor Yellow

$outputPayload = @{
    output_types = @("pdf", "excel", "form_6765")
    include_draft_watermark = $false
} | ConvertTo-Json

try {
    $outputResponse = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/outputs/generate" -Method POST -Headers $headers -Body $outputPayload
    Write-Host "[PASS] Generated $($outputResponse.files.Count) output files" -ForegroundColor Green

    foreach ($file in $outputResponse.files) {
        $sizeKB = [math]::Round($file.file_size / 1024, 2)
        Write-Host "       - $($file.filename) ($sizeKB KB)" -ForegroundColor Gray
    }
} catch {
    Write-Host "[WARN] Output generation issue: $_" -ForegroundColor Yellow
}

# ============================================
# STEP 12: Download and Save Outputs
# ============================================
Write-Host ""
Write-Host "=== STEP 12: Download Output Files ===" -ForegroundColor Yellow

$outputDir = "C:\Users\jtoroni\Downloads\RD_Study_E2E_Test"
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

try {
    $outputsList = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/outputs" -Method GET -Headers $headers

    foreach ($output in $outputsList) {
        Write-Host "  Downloading: $($output.filename)..." -ForegroundColor Gray
        $downloadUrl = "$rdStudyUrl/studies/$studyId/outputs/$($output.id)/download"
        $outputPath = Join-Path $outputDir $output.filename

        try {
            Invoke-WebRequest -Uri $downloadUrl -Headers $headers -OutFile $outputPath
            $fileSize = (Get-Item $outputPath).Length / 1024
            Write-Host "  [PASS] Saved: $($output.filename) ($([math]::Round($fileSize, 2)) KB)" -ForegroundColor Green
        } catch {
            Write-Host "  [WARN] Download failed: $_" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "[WARN] Could not list outputs: $_" -ForegroundColor Yellow
}

# ============================================
# FINAL SUMMARY
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  END-TO-END TEST COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Study ID: $studyId" -ForegroundColor White
Write-Host "Entity:   $testCompany" -ForegroundColor White
Write-Host "Tax Year: 2024" -ForegroundColor White
Write-Host ""
Write-Host "Output Files Location:" -ForegroundColor White
Write-Host "  $outputDir" -ForegroundColor Gray
Write-Host ""
Write-Host "CPA Workspace URL:" -ForegroundColor White
Write-Host "  https://cpa.auraai.toroniandcompany.com" -ForegroundColor Gray
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review downloaded PDF and Excel files for quality" -ForegroundColor Gray
Write-Host "  2. Check CPA workspace for complete data visibility" -ForegroundColor Gray
Write-Host "  3. Verify Form 6765 contains correct credit calculations" -ForegroundColor Gray
Write-Host ""
