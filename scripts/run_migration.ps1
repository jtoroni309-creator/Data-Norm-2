$scriptContent = Get-Content -Raw "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\create_enum_types.py"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($scriptContent)
$b64 = [Convert]::ToBase64String($bytes)

# Run in pod
$kubectlPath = "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat"
& $kubectlPath exec -n aura-audit-ai deployment/engagement -- /bin/sh -c "echo '$b64' | base64 -d > /tmp/create_enum_types.py && python3 /tmp/create_enum_types.py"
