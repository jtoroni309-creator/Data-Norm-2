# Test AI materiality endpoint using Python inside container
$pythonCode = @'
import httpx
r = httpx.post("http://localhost:8000/ai/materiality", json={
    "financial_data": {"total_assets": 10000000, "total_revenue": 5000000, "pretax_income": 500000, "total_equity": 3000000},
    "industry": "manufacturing"
})
print(r.text)
'@

& "c:\Users\jtoroni\Data Norm\Data-Norm-2\scripts\kubectl.bat" exec -n aura-audit-ai deployment/audit-planning -- python3 -c $pythonCode
