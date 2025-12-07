$svgPath = "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\toroni-logo.svg"
$svgContent = Get-Content $svgPath -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($svgContent)
$base64 = [Convert]::ToBase64String($bytes)
$dataUrl = "data:image/svg+xml;base64,$base64"
Write-Output $dataUrl
