$env:PATH += ";C:\Users\jtoroni\.azure-kubectl"

# Get the identity pod name
$POD = kubectl get pods -n aura-audit-ai -l app=identity -o jsonpath='{.items[0].metadata.name}'
Write-Host "Using pod: $POD"

# Create Python test script inline and run it directly via exec
$testScript = @"
import asyncio
import httpx
from datetime import date, datetime

BASE_URL = 'http://identity:80'
ENGAGEMENT_URL = 'http://engagement:80'
RD_STUDY_URL = 'http://rd-study-automation:8000'
SOC_URL = 'http://soc-copilot:80'

async def main():
    print('=' * 60)
    print('E2E Test: CPA Portal Functionality')
    print('=' * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        print('\\n[1] Testing CPA Portal Login...')
        login_response = await client.post(
            f'{BASE_URL}/auth/login',
            json={'email': 'admin@example.com', 'password': 'Admin123!'}
        )

        if login_response.status_code != 200:
            print(f'   FAILED: Login returned {login_response.status_code}')
            print(f'   Response: {login_response.text}')
            return

        login_data = login_response.json()
        token = login_data.get('access_token')
        print(f'   SUCCESS: Got access token')

        headers = {'Authorization': f'Bearer {token}'}

        print('\\n[2] Testing Audit Engagement Creation...')
        engagement_data = {
            'name': f'E2E Audit Test {datetime.now().strftime(\"%H%M%S\")}',
            'engagement_type': 'audit',
            'fiscal_year_end': str(date.today().replace(month=12, day=31)),
            'client_name': 'E2E Test Client'
        }

        eng_response = await client.post(
            f'{ENGAGEMENT_URL}/engagements',
            json=engagement_data,
            headers=headers
        )

        if eng_response.status_code in [200, 201]:
            eng_result = eng_response.json()
            print(f'   SUCCESS: Created engagement ID: {eng_result.get(\"id\")}')
        else:
            print(f'   Status: {eng_response.status_code}')
            print(f'   Response: {eng_response.text[:500]}')

        print('\\n[3] Testing R&D Study Creation...')
        try:
            health_resp = await client.get(f'{RD_STUDY_URL}/health', timeout=5.0)
            print(f'   R&D Service health: {health_resp.status_code}')
        except Exception as e:
            print(f'   R&D Service not responding: {e}')
        else:
            rd_study_data = {
                'name': f'E2E R&D Study {datetime.now().strftime(\"%H%M%S\")}',
                'tax_year': 2024,
                'entity_type': 'c_corp',
                'entity_name': 'E2E Test Corporation',
                'client_name': 'E2E Test R&D Client'
            }

            rd_response = await client.post(
                f'{RD_STUDY_URL}/studies',
                json=rd_study_data,
                headers=headers
            )

            if rd_response.status_code in [200, 201]:
                rd_result = rd_response.json()
                print(f'   SUCCESS: Created R&D study ID: {rd_result.get(\"id\")}')
            else:
                print(f'   Status: {rd_response.status_code}')
                print(f'   Response: {rd_response.text[:500]}')

        print('\\n[4] Testing SOC Audit Creation...')
        try:
            health_resp = await client.get(f'{SOC_URL}/health', timeout=5.0)
            print(f'   SOC Service health: {health_resp.status_code}')
        except Exception as e:
            print(f'   SOC Service not responding: {e}')
        else:
            from datetime import timedelta
            today = date.today()
            soc_data = {
                'client_name': f'E2E SOC Client {datetime.now().strftime(\"%H%M%S\")}',
                'service_description': 'Cloud hosting and data processing services',
                'engagement_type': 'SOC2',
                'report_type': 'TYPE2',
                'tsc_categories': ['SECURITY', 'AVAILABILITY'],
                'review_period_start': str(today - timedelta(days=365)),
                'review_period_end': str(today)
            }

            soc_response = await client.post(
                f'{SOC_URL}/engagements',
                json=soc_data,
                headers=headers
            )

            if soc_response.status_code in [200, 201]:
                soc_result = soc_response.json()
                print(f'   SUCCESS: Created SOC engagement ID: {soc_result.get(\"id\")}')
            else:
                print(f'   Status: {soc_response.status_code}')
                print(f'   Response: {soc_response.text[:500]}')

        print('\\n' + '=' * 60)
        print('E2E Test Complete')
        print('=' * 60)

asyncio.run(main())
"@

# Run directly using here-doc approach with exec
$escapedScript = $testScript.Replace("`r`n", "`n")
kubectl exec -n aura-audit-ai $POD -i -- python -c "$escapedScript"
