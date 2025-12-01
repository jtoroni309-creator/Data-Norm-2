#!/usr/bin/env python3
"""Test computer rental QRE creation."""

import asyncio
import httpx

BASE_URL = "http://identity:80"
RD_STUDY_URL = "http://rd-study-automation:8000"

async def test_computer_rental():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Authenticate
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@example.com", "password": "Admin123!"}
        )
        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}

        # Get existing studies
        response = await client.get(
            f"{RD_STUDY_URL}/studies",
            headers=headers
        )
        studies = response.json()
        print(f"Found {studies.get('total', 0)} studies")

        if studies.get('items'):
            study_id = studies['items'][0]['id']
            print(f"Using study: {study_id}")

            # Try to create computer rental QRE
            qre_data = {
                "category": "computer_rental",
                "supply_description": "AWS EC2 compute instances - R&D workloads",
                "supply_vendor": "Amazon Web Services",
                "gross_amount": "150000",
                "qualified_percentage": 85,
                "source_reference": "INV-123456"
            }

            print(f"Sending QRE data: {qre_data}")

            response = await client.post(
                f"{RD_STUDY_URL}/studies/{study_id}/qres",
                json=qre_data,
                headers=headers
            )

            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")

asyncio.run(test_computer_rental())
