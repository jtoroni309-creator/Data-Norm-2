# Check study details
$baseUrl = "https://rdclient.auraai.toroniandcompany.com/api/rd-study"
$identityUrl = "https://rdclient.auraai.toroniandcompany.com/api/identity"
$studyId = "c1388d49-8b20-403d-a22b-de8b98456bef"

# Login
$loginPayload = @{
    email = "prodtestuser@toroni.com"
    password = "TestPass123!"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
$token = $loginResponse.access_token

$headers = @{
    "Authorization" = "Bearer $token"
}

# Get study
Write-Host "=== Study Details ===" -ForegroundColor Cyan
$study = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId" -Headers $headers
Write-Host "Name: $($study.name)"
Write-Host "Entity: $($study.entity_name)"
Write-Host "Tax Year: $($study.tax_year)"
Write-Host "Status: $($study.status)"
Write-Host ""

# Get projects
Write-Host "=== Projects ===" -ForegroundColor Cyan
$projects = Invoke-RestMethod -Uri "$baseUrl/studies/$studyId/projects" -Headers $headers
foreach ($proj in $projects) {
    Write-Host "Project: $($proj.name)" -ForegroundColor Yellow
    Write-Host "  Qualification Status: $($proj.qualification_status)"
    Write-Host "  Overall Score: $($proj.overall_score)"
    Write-Host ""
    Write-Host "=== IRS 4-Part Test Scores ===" -ForegroundColor Green
    Write-Host "  Permitted Purpose Score: $($proj.permitted_purpose_score)"
    Write-Host "  Technological Nature Score: $($proj.technological_nature_score)"
    Write-Host "  Uncertainty Score: $($proj.uncertainty_score)"
    Write-Host "  Experimentation Score: $($proj.experimentation_score)"
    Write-Host ""
    Write-Host "=== IRS 4-Part Test Narratives ===" -ForegroundColor Green
    Write-Host "PERMITTED PURPOSE:"
    Write-Host "$($proj.permitted_purpose_narrative)"
    Write-Host ""
    Write-Host "TECHNOLOGICAL NATURE:"
    Write-Host "$($proj.technological_nature_narrative)"
    Write-Host ""
    Write-Host "UNCERTAINTY:"
    Write-Host "$($proj.uncertainty_narrative)"
    Write-Host ""
    Write-Host "EXPERIMENTATION:"
    Write-Host "$($proj.experimentation_narrative)"
    Write-Host ""
    Write-Host "OVERALL QUALIFICATION:"
    Write-Host "$($proj.qualification_narrative)"
}
