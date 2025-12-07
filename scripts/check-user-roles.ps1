$uri = "https://api.auraai.toroniandcompany.com/admin/users?limit=100"

try {
    $users = Invoke-RestMethod -Uri $uri -Method GET

    Write-Host "Found $($users.Count) users"
    Write-Host ""

    $emptyRoles = $users | Where-Object { -not $_.role -or $_.role -eq '' -or $_.role -eq $null }

    if ($emptyRoles.Count -gt 0) {
        Write-Host "Users with empty roles:"
        foreach ($user in $emptyRoles) {
            Write-Host "  - $($user.email) (ID: $($user.id))"
        }
    } else {
        Write-Host "All users have roles assigned!"
    }

    Write-Host ""
    Write-Host "All users and their roles:"
    foreach ($user in $users) {
        $role = if ($user.role) { $user.role } else { "(EMPTY)" }
        Write-Host "  - $($user.email): $role"
    }
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
