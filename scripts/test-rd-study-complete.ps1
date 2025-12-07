# Test R&D Study Complete Workflow
# Creates a study, adds data, runs AI, downloads outputs

$ErrorActionPreference = "Stop"
$baseUrl = "https://rdclient.auraai.toroniandcompany.com/api/rd-study"
$identityUrl = "https://rdclient.auraai.toroniandcompany.com/api/identity"

# Use production test user (password was reset via admin endpoint)
$testEmail = "prodtestuser@toroni.com"
$testPassword = "TestPass123!"

# Login
Write-Host "Getting authentication token for $testEmail..." -ForegroundColor Yellow
$loginPayload = @{
    email = $testEmail
    password = $testPassword
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
    $token = $loginResponse.access_token
    Write-Host "Login successful! User: $($loginResponse.user.full_name)" -ForegroundColor Green
} catch {
    Write-Host "Login failed: $_" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 1: Create a new R&D Study
Write-Host "`n=== Step 1: Creating R&D Study ===" -ForegroundColor Cyan
$studyPayload = @{
    name = "Tech Innovation R&D Study 2024"
    entity_name = "Tech Innovations Inc."
    ein = "12-3456789"
    tax_year = 2024
    entity_type = "c_corp"
    fiscal_year_start = "2024-01-01"
    fiscal_year_end = "2024-12-31"
    states = @("CA", "TX", "NY")
    is_controlled_group = $false
    current_year_gross_receipts = 5000000
} | ConvertTo-Json

try {
    $studyResponse = Invoke-RestMethod -Uri "$baseUrl/studies" -Method POST -Headers $headers -Body $studyPayload
    $studyId = $studyResponse.id
    Write-Host "Study created with ID: $studyId" -ForegroundColor Green
} catch {
    Write-Host "Failed to create study: $_" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Yellow
    exit 1
}

# Step 2: Add a Project
Write-Host "`n=== Step 2: Adding R&D Project ===" -ForegroundColor Cyan
$projectPayload = @{
    name = "AI-Powered Analytics Platform"
    code = "PROJ-001"
    description = "Development of machine learning algorithms for real-time financial data analysis and fraud detection. The project involves creating novel neural network architectures for pattern recognition in large-scale transaction datasets."
    department = "Engineering"
    business_component = "Analytics Engine"
    start_date = "2024-01-15"
    end_date = "2024-12-31"
} | ConvertTo-Json

try {
    $projectResponse = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId/projects" -Method POST -Headers $headers -Body $projectPayload
    $projectId = $projectResponse.id
    Write-Host "Project created with ID: $projectId" -ForegroundColor Green
} catch {
    Write-Host "Failed to create project: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Add Employees (Wages)
Write-Host "`n=== Step 3: Adding Employees ===" -ForegroundColor Cyan
$employees = @(
    @{
        employee_id = "EMP001"
        name = "Dr. Sarah Chen"
        title = "Lead Data Scientist"
        department = "Engineering"
        total_wages = 180000
        w2_wages = 180000
        qualified_time_percentage = 75
        qualified_time_source = "time_study"
        project_id = $projectId
    },
    @{
        employee_id = "EMP002"
        name = "Michael Rodriguez"
        title = "Senior ML Engineer"
        department = "Engineering"
        total_wages = 160000
        w2_wages = 160000
        qualified_time_percentage = 80
        qualified_time_source = "time_study"
        project_id = $projectId
    },
    @{
        employee_id = "EMP003"
        name = "Jennifer Walsh"
        title = "Software Architect"
        department = "Engineering"
        total_wages = 150000
        w2_wages = 150000
        qualified_time_percentage = 65
        qualified_time_source = "project_records"
        project_id = $projectId
    },
    @{
        employee_id = "EMP004"
        name = "David Kim"
        title = "Research Engineer"
        department = "R&D"
        total_wages = 140000
        w2_wages = 140000
        qualified_time_percentage = 90
        qualified_time_source = "time_study"
        project_id = $projectId
    }
)

foreach ($emp in $employees) {
    $empPayload = $emp | ConvertTo-Json
    try {
        $empResponse = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId/employees" -Method POST -Headers $headers -Body $empPayload
        Write-Host "Added employee: $($emp.name) - Qualified Wages: $($empResponse.qualified_wages)" -ForegroundColor Green
    } catch {
        Write-Host "Failed to add employee $($emp.name): $_" -ForegroundColor Red
    }
}

# Step 4: Add QREs (Contractors, Supplies, Computer Rental)
Write-Host "`n=== Step 4: Adding Qualified Research Expenses ===" -ForegroundColor Cyan

# QRE expenses - note: use /qres endpoint
$qres = @(
    # Contract Research
    @{
        category = "contract_research"
        subcategory = "Third-party contractor"
        gross_amount = 85000
        qualified_percentage = 65
        contractor_name = "AWS Professional Services"
        is_qualified_research_org = $false
        contract_percentage = 65
        project_id = $projectId
        supply_description = "ML Infrastructure Setup"
    },
    @{
        category = "contract_research"
        subcategory = "University research"
        gross_amount = 120000
        qualified_percentage = 100
        contractor_name = "Stanford University"
        is_qualified_research_org = $true
        contract_percentage = 100
        project_id = $projectId
        supply_description = "Algorithm Development"
    },
    # Supplies
    @{
        category = "supplies"
        subcategory = "Computing hardware"
        gross_amount = 45000
        qualified_percentage = 100
        supply_description = "NVIDIA A100 GPUs and server components"
        supply_vendor = "Dell Technologies"
        project_id = $projectId
    },
    @{
        category = "supplies"
        subcategory = "Development equipment"
        gross_amount = 28000
        qualified_percentage = 85
        supply_description = "High-performance workstations and networking equipment"
        supply_vendor = "HP Enterprise"
        project_id = $projectId
    },
    # Cloud Computing (as supplies - computer rental treated as supplies per IRS guidance)
    @{
        category = "supplies"
        subcategory = "Cloud computing"
        gross_amount = 95000
        qualified_percentage = 80
        supply_description = "Azure ML compute clusters for model training"
        supply_vendor = "Microsoft Azure"
        project_id = $projectId
    },
    @{
        category = "supplies"
        subcategory = "Cloud computing"
        gross_amount = 72000
        qualified_percentage = 85
        supply_description = "SageMaker instances for distributed training"
        supply_vendor = "Amazon Web Services"
        project_id = $projectId
    }
)

foreach ($qre in $qres) {
    $qrePayload = $qre | ConvertTo-Json
    try {
        $qreResponse = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId/qres" -Method POST -Headers $headers -Body $qrePayload
        Write-Host "Added QRE: $($qre.supply_description) - Qualified: $($qreResponse.qualified_amount)" -ForegroundColor Green
    } catch {
        Write-Host "Failed to add QRE $($qre.supply_description): $_" -ForegroundColor Red
    }
}

# Step 5: Run AI Complete Study
Write-Host "`n=== Step 5: Running AI Complete Study ===" -ForegroundColor Cyan
try {
    $aiResponse = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId/ai/complete-study" -Method POST -Headers $headers -TimeoutSec 300
    Write-Host "AI Analysis Complete!" -ForegroundColor Green
    Write-Host "Total QRE: $($aiResponse.total_qre)" -ForegroundColor White
    Write-Host "Federal Credit (Regular): $($aiResponse.federal_credit_regular)" -ForegroundColor White
    Write-Host "Federal Credit (ASC): $($aiResponse.federal_credit_asc)" -ForegroundColor White
    Write-Host "Total State Credits: $($aiResponse.total_state_credits)" -ForegroundColor White
    Write-Host "Selected Method: $($aiResponse.selected_method)" -ForegroundColor White
    Write-Host "Final Federal Credit: $($aiResponse.federal_credit_final)" -ForegroundColor White
    Write-Host "Total Credits: $($aiResponse.total_credits)" -ForegroundColor White
} catch {
    Write-Host "AI Complete failed: $_" -ForegroundColor Red
    Write-Host "Response: $($_.Exception.Response)" -ForegroundColor Yellow
}

# Step 6: Generate PDF and Excel Outputs
Write-Host "`n=== Step 6: Generating Output Files ===" -ForegroundColor Cyan
$outputPayload = @{
    output_types = @("pdf", "excel", "form_6765")
    include_draft_watermark = $true
} | ConvertTo-Json

try {
    $outputResponse = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId/outputs/generate" -Method POST -Headers $headers -Body $outputPayload
    Write-Host "Generated $($outputResponse.files.Count) output files!" -ForegroundColor Green

    foreach ($file in $outputResponse.files) {
        Write-Host "  - $($file.filename) ($($file.file_type)) - $([math]::Round($file.file_size/1024, 2)) KB" -ForegroundColor White
    }
} catch {
    Write-Host "Output generation failed: $_" -ForegroundColor Red
}

# Step 7: List and Download Outputs
Write-Host "`n=== Step 7: Downloading Output Files ===" -ForegroundColor Cyan
try {
    $outputsList = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId/outputs" -Method GET -Headers $headers

    $outputDir = "C:\Users\jtoroni\Downloads\RD_Study_Outputs"
    if (-not (Test-Path $outputDir)) {
        New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    }

    foreach ($output in $outputsList) {
        Write-Host "Downloading: $($output.filename)..." -ForegroundColor Yellow
        $downloadUrl = "$baseUrl/studies/$studyId/outputs/$($output.id)/download"
        $outputPath = Join-Path $outputDir $output.filename

        try {
            Invoke-WebRequest -Uri $downloadUrl -Headers $headers -OutFile $outputPath
            Write-Host "  Saved to: $outputPath" -ForegroundColor Green
        } catch {
            Write-Host "  Download failed: $_" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "Failed to list outputs: $_" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "Study ID: $studyId" -ForegroundColor White
Write-Host "Output files saved to: $outputDir" -ForegroundColor White
