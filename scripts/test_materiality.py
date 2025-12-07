#!/usr/bin/env python3
"""Test AI materiality endpoint"""
import httpx

data = {
    "financial_data": {
        "total_assets": 10000000,
        "total_revenue": 5000000,
        "pretax_income": 500000,
        "total_equity": 3000000
    },
    "industry": "manufacturing"
}

r = httpx.post("http://localhost:8000/ai/materiality", json=data)
print(r.text)
