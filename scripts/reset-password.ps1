# Reset test user password
$body = @{
    new_password = "TestPass123!"
} | ConvertTo-Json

$result = Invoke-RestMethod -Uri "https://rdclient.auraai.toroniandcompany.com/api/identity/admin/users/b27ab28d-eed6-4fda-a67d-086d361d99e9/reset-password" -Method POST -ContentType "application/json" -Body $body
Write-Host "Password reset: $($result | ConvertTo-Json)"
