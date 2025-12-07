# Test all Toroni CPA firm user logins
$baseUrl = "https://api.auraai.toroniandcompany.com"

$users = @(
    @{ email = "fred@toronicpa.com"; name = "Fred Toroni" },
    @{ email = "bonnie@toronicpa.com"; name = "Bonnie Toroni" },
    @{ email = "jtoroni@toronicpa.com"; name = "James Toroni" },
    @{ email = "blaise@toronicpa.com"; name = "Blaise Toroni" }
)

Write-Host "Testing logins for Fred J. Toroni & Company users..."
Write-Host ""

$successCount = 0
$failCount = 0

foreach ($user in $users) {
    $body = @{
        email = $user.email
        password = "Bonred10"
    } | ConvertTo-Json

    Write-Host "Testing $($user.email)..."
    try {
        $result = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -ContentType "application/json" -Body $body
        Write-Host "  SUCCESS - Login works for $($user.name)"
        $successCount++
    } catch {
        Write-Host "  FAILED - $($_.Exception.Message)"
        $failCount++
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Results: $successCount successful, $failCount failed"
Write-Host "=========================================="
