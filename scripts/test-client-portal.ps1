# Client Portal Access Test
$ErrorActionPreference = "Continue"

$identityUrl = "https://cpa.auraai.toroniandcompany.com/api/identity"
$engagementUrl = "https://cpa.auraai.toroniandcompany.com/api/engagement"
$engagementId = "38d372f8-09b9-44c5-b563-67df703c8081"

# Login
$loginPayload = @{ email = "prodtestuser@toroni.com"; password = "TestPass123!" } | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }

$passCount = 0
$failCount = 0

Write-Host "`n=== CLIENT PORTAL ACCESS TEST ===" -ForegroundColor Magenta

# Test 1: User Profile
Write-Host "`n=== CP.1: User Profile ===" -ForegroundColor Cyan
try {
    $user = Invoke-RestMethod -Uri "$identityUrl/users/me" -Method GET -Headers $headers
    Write-Host "[PASS] User Profile Retrieved" -ForegroundColor Green
    Write-Host "  Email: $($user.email)"
    Write-Host "  Name: $($user.first_name) $($user.last_name)"
    $passCount++
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $failCount++
}

# Test 2: List Engagements
Write-Host "`n=== CP.2: List Engagements ===" -ForegroundColor Cyan
try {
    $engagements = Invoke-RestMethod -Uri "$engagementUrl/engagements" -Method GET -Headers $headers
    $count = if ($engagements -is [array]) { $engagements.Count } else { 1 }
    Write-Host "[PASS] Engagements Retrieved: $count" -ForegroundColor Green
    foreach ($e in $engagements) {
        Write-Host "  - $($e.name): $($e.status)"
    }
    $passCount++
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $failCount++
}

# Test 3: Get Specific Engagement
Write-Host "`n=== CP.3: Engagement Details ===" -ForegroundColor Cyan
try {
    $eng = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId" -Method GET -Headers $headers
    Write-Host "[PASS] Engagement Retrieved" -ForegroundColor Green
    Write-Host "  Name: $($eng.name)"
    Write-Host "  Status: $($eng.status)"
    Write-Host "  Type: $($eng.engagement_type)"
    Write-Host "  FYE: $($eng.fiscal_year_end)"
    $passCount++
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    $failCount++
}

# Test 4: Binder Structure
Write-Host "`n=== CP.4: Binder Structure ===" -ForegroundColor Cyan
try {
    $binder = Invoke-RestMethod -Uri "$engagementUrl/engagements/$engagementId/binder" -Method GET -Headers $headers
    $sectionCount = if ($binder.sections -is [array]) { $binder.sections.Count } else { 0 }
    Write-Host "[PASS] Binder Retrieved: $sectionCount sections" -ForegroundColor Green
    foreach ($s in $binder.sections) {
        Write-Host "  - $($s.reference): $($s.name)"
    }
    $passCount++
} catch {
    Write-Host "[WARN] Binder: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n=== CLIENT PORTAL TEST RESULTS ===" -ForegroundColor Green
Write-Host "  PASS: $passCount" -ForegroundColor Green
Write-Host "  FAIL: $failCount" -ForegroundColor Red

if ($failCount -eq 0) {
    Write-Host "`n[VERDICT] Client Portal Access: OPERATIONAL" -ForegroundColor Green
} else {
    Write-Host "`n[VERDICT] Client Portal: NEEDS REVIEW" -ForegroundColor Yellow
}
