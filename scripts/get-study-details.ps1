# Get study details
$identityUrl = "https://rdclient.auraai.toroniandcompany.com/api/identity"
$rdStudyUrl = "https://rdclient.auraai.toroniandcompany.com/api/rd-study"
$studyId = "0dab28a8-fe44-455a-9af9-bb51177fadf2"

$loginPayload = @{ email = "prodtestuser@toroni.com"; password = "TestPass123!" } | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Uri "$identityUrl/auth/login" -Method POST -ContentType "application/json" -Body $loginPayload
$token = $loginResponse.access_token
$headers = @{ "Authorization" = "Bearer $token" }

Write-Host "=== Full Study Details ===" -ForegroundColor Cyan
$study = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId" -Headers $headers
Write-Host "Entity: $($study.entity_name)"
Write-Host "Status: $($study.status)"
Write-Host "Total QRE: $($study.total_qre)"
Write-Host "Federal Credit Regular: $($study.federal_credit_regular)"
Write-Host "Federal Credit ASC: $($study.federal_credit_asc)"
Write-Host "Selected Method: $($study.selected_method)"
Write-Host "Federal Credit Final: $($study.federal_credit_final)"
Write-Host ""

# Get projects with 4-part test scores
Write-Host "=== Project Details ===" -ForegroundColor Cyan
$projects = Invoke-RestMethod -Uri "$rdStudyUrl/studies/$studyId/projects" -Headers $headers
foreach ($proj in $projects) {
    Write-Host ""
    Write-Host "Project: $($proj.name)" -ForegroundColor Yellow
    Write-Host "  Status: $($proj.qualification_status)"
    Write-Host "  Overall Score: $($proj.overall_score)"
    Write-Host "  --- IRS 4-Part Test ---"
    Write-Host "  Permitted Purpose Score: $($proj.permitted_purpose_score)"
    Write-Host "  Permitted Purpose Narrative: $($proj.permitted_purpose_narrative)"
    Write-Host ""
    Write-Host "  Technological Nature Score: $($proj.technological_nature_score)"
    Write-Host "  Technological Nature Narrative: $($proj.technological_nature_narrative)"
    Write-Host ""
    Write-Host "  Uncertainty Score: $($proj.uncertainty_score)"
    Write-Host "  Uncertainty Narrative: $($proj.uncertainty_narrative)"
    Write-Host ""
    Write-Host "  Experimentation Score: $($proj.experimentation_score)"
    Write-Host "  Experimentation Narrative: $($proj.experimentation_narrative)"
}
