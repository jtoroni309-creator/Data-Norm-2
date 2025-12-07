$uri = "https://api.auraai.toroniandcompany.com/admin/users/1e290b7a-ee49-456d-8d8d-e7fd11c78e10/reset-password"
$body = @{
    new_password = "TempPass123!"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri $uri -Method POST -ContentType "application/json" -Body $body
    Write-Host "Password reset successful!"
    $result | ConvertTo-Json
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}
