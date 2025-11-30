"""
Payroll Provider API Integrations

Real API connections for ADP Run, Justworks, and Paychex Flex.
Includes OAuth flows and data sync capabilities.
"""

import logging
import httpx
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


@dataclass
class PayrollEmployee:
    """Standardized employee data from payroll provider."""
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str]
    title: Optional[str]
    department: Optional[str]
    hire_date: Optional[date]
    termination_date: Optional[date]
    status: str  # active, terminated, on_leave
    w2_wages: Decimal
    ytd_wages: Decimal
    pay_frequency: str  # weekly, biweekly, semimonthly, monthly


@dataclass
class PayrollConnection:
    """OAuth connection state."""
    provider: str
    access_token: str
    refresh_token: Optional[str]
    token_expires_at: datetime
    company_id: Optional[str]
    scopes: List[str]


class PayrollProviderBase(ABC):
    """Base class for payroll provider integrations."""

    provider_name: str = "base"
    oauth_base_url: str = ""
    api_base_url: str = ""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.http_client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Generate OAuth authorization URL."""
        pass

    @abstractmethod
    async def exchange_code_for_token(self, code: str) -> PayrollConnection:
        """Exchange authorization code for access token."""
        pass

    @abstractmethod
    async def refresh_access_token(self, connection: PayrollConnection) -> PayrollConnection:
        """Refresh expired access token."""
        pass

    @abstractmethod
    async def get_employees(self, connection: PayrollConnection, year: int) -> List[PayrollEmployee]:
        """Fetch all employees with wage data for the given year."""
        pass

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


class ADPRunProvider(PayrollProviderBase):
    """
    ADP Run (RUN Powered by ADP) API Integration.

    API Documentation: https://developers.adp.com/articles/api/run-api
    OAuth: https://developers.adp.com/articles/guide/auth-process-overview
    """

    provider_name = "adp_run"
    oauth_base_url = "https://accounts.adp.com"
    api_base_url = "https://api.adp.com"

    def get_authorization_url(self, state: str) -> str:
        """Generate ADP OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "api openid profile",
            "state": state,
        }
        return f"{self.oauth_base_url}/auth/oauth/v2/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> PayrollConnection:
        """Exchange ADP authorization code for access token."""
        token_url = f"{self.oauth_base_url}/auth/oauth/v2/token"

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self.http_client.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        expires_in = token_data.get("expires_in", 3600)

        return PayrollConnection(
            provider=self.provider_name,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            company_id=token_data.get("company_id"),
            scopes=token_data.get("scope", "").split(),
        )

    async def refresh_access_token(self, connection: PayrollConnection) -> PayrollConnection:
        """Refresh ADP access token."""
        if not connection.refresh_token:
            raise ValueError("No refresh token available")

        token_url = f"{self.oauth_base_url}/auth/oauth/v2/token"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": connection.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self.http_client.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        expires_in = token_data.get("expires_in", 3600)

        return PayrollConnection(
            provider=self.provider_name,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", connection.refresh_token),
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            company_id=connection.company_id,
            scopes=connection.scopes,
        )

    async def get_employees(self, connection: PayrollConnection, year: int) -> List[PayrollEmployee]:
        """Fetch employees from ADP Run with wage data."""
        headers = {
            "Authorization": f"Bearer {connection.access_token}",
            "Accept": "application/json",
        }

        # Get workers
        workers_url = f"{self.api_base_url}/hr/v2/workers"
        response = await self.http_client.get(workers_url, headers=headers)
        response.raise_for_status()
        workers_data = response.json()

        employees = []
        for worker in workers_data.get("workers", []):
            person = worker.get("person", {})
            name = person.get("legalName", {})
            work_assignment = worker.get("workAssignments", [{}])[0]

            # Get wage data for the year
            worker_id = worker.get("associateOID")
            wages = await self._get_worker_wages(connection, worker_id, year)

            employee = PayrollEmployee(
                employee_id=worker_id,
                first_name=name.get("givenName", ""),
                last_name=name.get("familyName1", ""),
                full_name=f"{name.get('givenName', '')} {name.get('familyName1', '')}".strip(),
                email=person.get("communication", {}).get("emails", [{}])[0].get("emailUri"),
                title=work_assignment.get("jobTitle"),
                department=work_assignment.get("homeOrganizationalUnits", [{}])[0].get("nameCode", {}).get("shortName"),
                hire_date=self._parse_date(work_assignment.get("hireDate")),
                termination_date=self._parse_date(work_assignment.get("terminationDate")),
                status="active" if work_assignment.get("workerStatus", {}).get("statusCode", {}).get("codeValue") == "Active" else "terminated",
                w2_wages=Decimal(str(wages.get("w2_wages", 0))),
                ytd_wages=Decimal(str(wages.get("ytd_wages", 0))),
                pay_frequency=work_assignment.get("payrollScheduleReference", {}).get("payFrequencyCode", {}).get("codeValue", "biweekly"),
            )
            employees.append(employee)

        return employees

    async def _get_worker_wages(self, connection: PayrollConnection, worker_id: str, year: int) -> Dict[str, float]:
        """Get wage totals for a worker for the specified year."""
        headers = {
            "Authorization": f"Bearer {connection.access_token}",
            "Accept": "application/json",
        }

        # Get pay statements for the year
        url = f"{self.api_base_url}/payroll/v1/workers/{worker_id}/pay-statements"
        params = {"$filter": f"payDate ge '{year}-01-01' and payDate le '{year}-12-31'"}

        try:
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            statements = response.json().get("payStatements", [])

            total_wages = sum(
                float(stmt.get("grossPay", {}).get("amount", 0))
                for stmt in statements
            )

            return {"w2_wages": total_wages, "ytd_wages": total_wages}
        except Exception as e:
            logger.warning(f"Could not fetch wages for worker {worker_id}: {e}")
            return {"w2_wages": 0, "ytd_wages": 0}

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (ValueError, IndexError):
            return None


class JustworksProvider(PayrollProviderBase):
    """
    Justworks API Integration.

    API Documentation: https://developers.justworks.com/
    """

    provider_name = "justworks"
    oauth_base_url = "https://secure.justworks.com"
    api_base_url = "https://api.justworks.com/v1"

    def get_authorization_url(self, state: str) -> str:
        """Generate Justworks OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "read:employees read:payroll",
            "state": state,
        }
        return f"{self.oauth_base_url}/oauth/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> PayrollConnection:
        """Exchange Justworks authorization code for access token."""
        token_url = f"{self.oauth_base_url}/oauth/token"

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self.http_client.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        expires_in = token_data.get("expires_in", 7200)

        return PayrollConnection(
            provider=self.provider_name,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            company_id=token_data.get("company_id"),
            scopes=token_data.get("scope", "").split(),
        )

    async def refresh_access_token(self, connection: PayrollConnection) -> PayrollConnection:
        """Refresh Justworks access token."""
        if not connection.refresh_token:
            raise ValueError("No refresh token available")

        token_url = f"{self.oauth_base_url}/oauth/token"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": connection.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self.http_client.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        expires_in = token_data.get("expires_in", 7200)

        return PayrollConnection(
            provider=self.provider_name,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", connection.refresh_token),
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            company_id=connection.company_id,
            scopes=connection.scopes,
        )

    async def get_employees(self, connection: PayrollConnection, year: int) -> List[PayrollEmployee]:
        """Fetch employees from Justworks with wage data."""
        headers = {
            "Authorization": f"Bearer {connection.access_token}",
            "Accept": "application/json",
        }

        # Get employees
        employees_url = f"{self.api_base_url}/employees"
        response = await self.http_client.get(employees_url, headers=headers)
        response.raise_for_status()
        employees_data = response.json()

        employees = []
        for emp in employees_data.get("employees", []):
            # Get payroll data for the year
            emp_id = emp.get("id")
            wages = await self._get_employee_wages(connection, emp_id, year)

            employee = PayrollEmployee(
                employee_id=emp_id,
                first_name=emp.get("first_name", ""),
                last_name=emp.get("last_name", ""),
                full_name=f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip(),
                email=emp.get("email"),
                title=emp.get("job_title"),
                department=emp.get("department"),
                hire_date=self._parse_date(emp.get("hire_date")),
                termination_date=self._parse_date(emp.get("termination_date")),
                status=emp.get("status", "active").lower(),
                w2_wages=Decimal(str(wages.get("w2_wages", 0))),
                ytd_wages=Decimal(str(wages.get("ytd_wages", 0))),
                pay_frequency=emp.get("pay_frequency", "biweekly"),
            )
            employees.append(employee)

        return employees

    async def _get_employee_wages(self, connection: PayrollConnection, employee_id: str, year: int) -> Dict[str, float]:
        """Get wage totals for an employee for the specified year."""
        headers = {
            "Authorization": f"Bearer {connection.access_token}",
            "Accept": "application/json",
        }

        url = f"{self.api_base_url}/employees/{employee_id}/payroll"
        params = {"year": year}

        try:
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            payroll_data = response.json()

            w2_wages = float(payroll_data.get("ytd_gross_wages", 0))

            return {"w2_wages": w2_wages, "ytd_wages": w2_wages}
        except Exception as e:
            logger.warning(f"Could not fetch wages for employee {employee_id}: {e}")
            return {"w2_wages": 0, "ytd_wages": 0}

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (ValueError, IndexError):
            return None


class PaychexFlexProvider(PayrollProviderBase):
    """
    Paychex Flex API Integration.

    API Documentation: https://developer.paychex.com/
    """

    provider_name = "paychex_flex"
    oauth_base_url = "https://api.paychex.com"
    api_base_url = "https://api.paychex.com"

    def get_authorization_url(self, state: str) -> str:
        """Generate Paychex Flex OAuth authorization URL."""
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": "read:workers read:payroll",
            "state": state,
        }
        return f"{self.oauth_base_url}/auth/oauth/v2/authorize?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> PayrollConnection:
        """Exchange Paychex authorization code for access token."""
        token_url = f"{self.oauth_base_url}/auth/oauth/v2/token"

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self.http_client.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        expires_in = token_data.get("expires_in", 3600)

        return PayrollConnection(
            provider=self.provider_name,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            company_id=token_data.get("companyId"),
            scopes=token_data.get("scope", "").split(),
        )

    async def refresh_access_token(self, connection: PayrollConnection) -> PayrollConnection:
        """Refresh Paychex access token."""
        if not connection.refresh_token:
            raise ValueError("No refresh token available")

        token_url = f"{self.oauth_base_url}/auth/oauth/v2/token"

        data = {
            "grant_type": "refresh_token",
            "refresh_token": connection.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = await self.http_client.post(token_url, data=data)
        response.raise_for_status()
        token_data = response.json()

        expires_in = token_data.get("expires_in", 3600)

        return PayrollConnection(
            provider=self.provider_name,
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", connection.refresh_token),
            token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
            company_id=connection.company_id,
            scopes=connection.scopes,
        )

    async def get_employees(self, connection: PayrollConnection, year: int) -> List[PayrollEmployee]:
        """Fetch employees from Paychex Flex with wage data."""
        headers = {
            "Authorization": f"Bearer {connection.access_token}",
            "Accept": "application/json",
        }

        # Get company workers
        company_id = connection.company_id
        workers_url = f"{self.api_base_url}/companies/{company_id}/workers"
        response = await self.http_client.get(workers_url, headers=headers)
        response.raise_for_status()
        workers_data = response.json()

        employees = []
        for worker in workers_data.get("content", []):
            worker_id = worker.get("workerId")
            name = worker.get("name", {})

            # Get wage data for the year
            wages = await self._get_worker_wages(connection, company_id, worker_id, year)

            employee = PayrollEmployee(
                employee_id=worker_id,
                first_name=name.get("givenName", ""),
                last_name=name.get("familyName", ""),
                full_name=f"{name.get('givenName', '')} {name.get('familyName', '')}".strip(),
                email=worker.get("communications", {}).get("emails", [{}])[0].get("emailAddress"),
                title=worker.get("job", {}).get("title"),
                department=worker.get("organization", {}).get("department", {}).get("name"),
                hire_date=self._parse_date(worker.get("employmentStartDate")),
                termination_date=self._parse_date(worker.get("employmentEndDate")),
                status="active" if worker.get("workerStatus") == "ACTIVE" else "terminated",
                w2_wages=Decimal(str(wages.get("w2_wages", 0))),
                ytd_wages=Decimal(str(wages.get("ytd_wages", 0))),
                pay_frequency=worker.get("payFrequency", "BI_WEEKLY").lower().replace("_", ""),
            )
            employees.append(employee)

        return employees

    async def _get_worker_wages(self, connection: PayrollConnection, company_id: str, worker_id: str, year: int) -> Dict[str, float]:
        """Get wage totals for a worker for the specified year."""
        headers = {
            "Authorization": f"Bearer {connection.access_token}",
            "Accept": "application/json",
        }

        # Get pay checks for the year
        url = f"{self.api_base_url}/companies/{company_id}/workers/{worker_id}/paychecks"
        params = {"fromDate": f"{year}-01-01", "toDate": f"{year}-12-31"}

        try:
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            paychecks = response.json().get("content", [])

            total_wages = sum(
                float(check.get("grossPay", 0))
                for check in paychecks
            )

            return {"w2_wages": total_wages, "ytd_wages": total_wages}
        except Exception as e:
            logger.warning(f"Could not fetch wages for worker {worker_id}: {e}")
            return {"w2_wages": 0, "ytd_wages": 0}

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string to date object."""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
        except (ValueError, IndexError):
            return None


# Provider factory
PAYROLL_PROVIDERS = {
    "adp_run": ADPRunProvider,
    "adp": ADPRunProvider,
    "justworks": JustworksProvider,
    "paychex": PaychexFlexProvider,
    "paychex_flex": PaychexFlexProvider,
}


def get_payroll_provider(
    provider_name: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str
) -> PayrollProviderBase:
    """Factory function to get a payroll provider instance."""
    provider_class = PAYROLL_PROVIDERS.get(provider_name.lower())
    if not provider_class:
        raise ValueError(f"Unknown payroll provider: {provider_name}. Supported: {list(PAYROLL_PROVIDERS.keys())}")
    return provider_class(client_id, client_secret, redirect_uri)


# Add missing import
from datetime import timedelta
