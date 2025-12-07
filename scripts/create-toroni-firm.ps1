# Create Fred J. Toroni & Company CPA Firm and Users
$baseUrl = "https://api.auraai.toroniandcompany.com"

# Step 1: Create the CPA Firm
Write-Host "Creating CPA Firm: Fred J. Toroni & Company..."
$firmBody = @{
    firm_name = "Fred J. Toroni & Company Certified Public Accountants"
    legal_name = "Fred J. Toroni & Company, CPA"
    primary_contact_name = "Fred Toroni"
    primary_contact_email = "fred@toronicpa.com"
    primary_contact_phone = ""
    subscription_tier = "enterprise"
    subscription_status = "active"
    max_users = 20
} | ConvertTo-Json

try {
    $firm = Invoke-RestMethod -Uri "$baseUrl/admin/organizations" -Method POST -ContentType "application/json" -Body $firmBody
    Write-Host "Firm created successfully!"
    Write-Host "Firm ID: $($firm.id)"
    $firmId = $firm.id
} catch {
    Write-Host "Error creating firm: $($_.Exception.Message)"
    if ($_.ErrorDetails) {
        Write-Host "Details: $($_.ErrorDetails.Message)"
    }
    exit 1
}

# Step 2: Create the 4 users
$users = @(
    @{ email = "fred@toronicpa.com"; full_name = "Fred Toroni"; role = "partner" },
    @{ email = "bonnie@toronicpa.com"; full_name = "Bonnie Toroni"; role = "partner" },
    @{ email = "jtoroni@toronicpa.com"; full_name = "James Toroni"; role = "partner" },
    @{ email = "blaise@toronicpa.com"; full_name = "Blaise Toroni"; role = "partner" }
)

$createdUsers = @()
foreach ($user in $users) {
    Write-Host "Creating user: $($user.email)..."
    $userBody = @{
        email = $user.email
        full_name = $user.full_name
        password = "Bonred10"
        role = $user.role
        organization_id = $firmId
    } | ConvertTo-Json

    try {
        $newUser = Invoke-RestMethod -Uri "$baseUrl/admin/users" -Method POST -ContentType "application/json" -Body $userBody
        Write-Host "  User created: $($newUser.email) (ID: $($newUser.id))"
        $createdUsers += $newUser
    } catch {
        Write-Host "  Error creating user: $($_.Exception.Message)"
        if ($_.ErrorDetails) {
            Write-Host "  Details: $($_.ErrorDetails.Message)"
        }
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host "Summary:"
Write-Host "=========================================="
Write-Host "Firm: Fred J. Toroni & Company Certified Public Accountants"
Write-Host "Firm ID: $firmId"
Write-Host ""
Write-Host "Users created:"
foreach ($user in $createdUsers) {
    Write-Host "  - $($user.email)"
}
Write-Host ""
Write-Host "All users have password: Bonred10"
Write-Host "All users have role: partner (firm administrator)"
