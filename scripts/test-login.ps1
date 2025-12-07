$uri = "https://api.auraai.toroniandcompany.com/auth/login"
$body = @{
    email = "jtoroni@toroniandcompany.com"
    password = "Bonred10*"
} | ConvertTo-Json

try {
    $result = Invoke-RestMethod -Uri $uri -Method POST -ContentType "application/json" -Body $body
    Write-Host "Login successful!"
    Write-Host "Access Token (first 50 chars): $($result.access_token.Substring(0, 50))..."
    Write-Host "Token Type: $($result.token_type)"
} catch {
    Write-Host "Login failed!"
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
}
