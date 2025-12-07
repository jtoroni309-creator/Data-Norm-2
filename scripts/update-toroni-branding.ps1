# Update Fred J. Toroni & Company Branding
$baseUrl = "https://api.auraai.toroniandcompany.com"
$firmId = "4751d3f9-c33c-46a9-86ab-cba9caaedf9c"

# Based on the logo: Dark green primary color
$brandingBody = @{
    primary_color = "#1B5E20"
    secondary_color = "#4CAF50"
    enabled_services = @{
        audit = $true
        tax = $true
        rd_study = $true
        analytics = $true
        financial = $true
    }
} | ConvertTo-Json -Depth 5

Write-Host "Updating firm branding..."
try {
    $result = Invoke-RestMethod -Uri "$baseUrl/admin/organizations/$firmId" -Method PATCH -ContentType "application/json" -Body $brandingBody
    Write-Host "Branding updated successfully!"
    Write-Host "Primary Color: $($result.primary_color)"
    Write-Host "Secondary Color: $($result.secondary_color)"
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}
