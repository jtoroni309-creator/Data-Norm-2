"""
Payroll Provider Integrations

Integrations with major payroll providers for R&D tax credit data collection:
- ADP Workforce Now / RUN Powered by ADP
- Justworks
- Paychex Flex

Supports OAuth2 authentication and secure API access to retrieve:
- Employee census data
- W-2 wage information
- Department/cost center allocations
- Pay period breakdowns
"""

import logging
import json
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from abc import ABC, abstractmethod
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class PayrollProvider(str, Enum):
    """Supported payroll providers."""
    ADP = "adp"
    JUSTWORKS = "justworks"
    PAYCHEX = "paychex"


@dataclass
class PayrollEmployee:
    """Standardized employee record from payroll."""
    employee_id: str
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str]
    title: Optional[str]
    department: Optional[str]
    cost_center: Optional[str]
    hire_date: Optional[date]
    termination_date: Optional[date]
    employment_status: str  # active, terminated, on_leave
    pay_type: str  # salary, hourly
    annual_salary: Optional[Decimal]
    hourly_rate: Optional[Decimal]


@dataclass
class PayrollWageData:
    """W-2 wage data for an employee."""
    employee_id: str
    tax_year: int
    w2_wages: Decimal  # Box 1
    federal_tax_withheld: Decimal  # Box 2
    social_security_wages: Decimal  # Box 3
    social_security_tax: Decimal  # Box 4
    medicare_wages: Decimal  # Box 5
    medicare_tax: Decimal  # Box 6
    state_wages: Optional[Dict[str, Decimal]]  # By state
    gross_pay: Decimal
    bonus_pay: Optional[Decimal]
    overtime_pay: Optional[Decimal]


@dataclass
class PayPeriodData:
    """Pay period breakdown for time analysis."""
    employee_id: str
    pay_date: date
    period_start: date
    period_end: date
    gross_pay: Decimal
    regular_hours: Optional[float]
    overtime_hours: Optional[float]
    department: Optional[str]
    cost_center: Optional[str]


@dataclass
class PayrollIntegrationResult:
    """Result of payroll data fetch."""
    provider: PayrollProvider
    success: bool
    employees: List[PayrollEmployee]
    wage_data: List[PayrollWageData]
    pay_periods: List[PayPeriodData]
    error_message: Optional[str]
    sync_timestamp: datetime


class PayrollProviderBase(ABC):
    """Base class for payroll provider integrations."""

    def __init__(self, config: Dict[str, str]):
        """
        Initialize provider with configuration.

        Config should contain:
        - client_id: OAuth client ID
        - client_secret: OAuth client secret
        - redirect_uri: OAuth redirect URI
        - environment: 'sandbox' or 'production'
        """
        self.config = config
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None

    @abstractmethod
    async def get_auth_url(self, state: str) -> str:
        """Get OAuth authorization URL."""
        pass

    @abstractmethod
    async def exchange_code(self, auth_code: str) -> Dict[str, str]:
        """Exchange authorization code for tokens."""
        pass

    @abstractmethod
    async def refresh_access_token(self) -> bool:
        """Refresh the access token."""
        pass

    @abstractmethod
    async def get_employees(self) -> List[PayrollEmployee]:
        """Fetch employee census data."""
        pass

    @abstractmethod
    async def get_wage_data(self, tax_year: int) -> List[PayrollWageData]:
        """Fetch W-2 wage data for a tax year."""
        pass

    @abstractmethod
    async def get_pay_periods(
        self,
        start_date: date,
        end_date: date
    ) -> List[PayPeriodData]:
        """Fetch pay period data within date range."""
        pass

    async def _ensure_token_valid(self):
        """Ensure access token is valid, refresh if needed."""
        if not self.access_token:
            raise ValueError("Not authenticated. Please connect to the payroll provider.")

        if self.token_expires and datetime.now() >= self.token_expires:
            await self.refresh_access_token()


class ADPIntegration(PayrollProviderBase):
    """
    ADP Workforce Now / RUN Powered by ADP Integration.

    Uses ADP's REST APIs for:
    - Workers v2 API for employee data
    - Pay Data API for earnings
    - Tax Documents API for W-2 data
    """

    BASE_URL_SANDBOX = "https://api.adp.com"
    BASE_URL_PROD = "https://api.adp.com"
    AUTH_URL = "https://accounts.adp.com/auth/oauth/v2/authorize"
    TOKEN_URL = "https://accounts.adp.com/auth/oauth/v2/token"

    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.base_url = (
            self.BASE_URL_PROD
            if config.get("environment") == "production"
            else self.BASE_URL_SANDBOX
        )

    async def get_auth_url(self, state: str) -> str:
        """Generate ADP OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "scope": "api openid profile",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, auth_code: str) -> Dict[str, str]:
        """Exchange authorization code for ADP tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                    "redirect_uri": self.config["redirect_uri"],
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                raise ValueError(f"Token exchange failed: {response.text}")

            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            self.token_expires = datetime.now().replace(
                second=datetime.now().second + data.get("expires_in", 3600)
            )

            return data

    async def refresh_access_token(self) -> bool:
        """Refresh ADP access token."""
        if not self.refresh_token:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                logger.error(f"Token refresh failed: {response.text}")
                return False

            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            self.token_expires = datetime.now().replace(
                second=datetime.now().second + data.get("expires_in", 3600)
            )

            return True

    async def get_employees(self) -> List[PayrollEmployee]:
        """Fetch employee data from ADP Workers API."""
        await self._ensure_token_valid()

        employees = []

        async with httpx.AsyncClient() as client:
            # ADP Workers V2 API
            response = await client.get(
                f"{self.base_url}/hr/v2/workers",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
            )

            if response.status_code != 200:
                logger.error(f"ADP workers fetch failed: {response.text}")
                return employees

            data = response.json()

            for worker in data.get("workers", []):
                person = worker.get("person", {})
                emp_data = worker.get("workerDates", {})
                job = worker.get("workAssignments", [{}])[0] if worker.get("workAssignments") else {}

                employees.append(PayrollEmployee(
                    employee_id=worker.get("associateOID", ""),
                    first_name=person.get("legalName", {}).get("givenName", ""),
                    last_name=person.get("legalName", {}).get("familyName1", ""),
                    full_name=f"{person.get('legalName', {}).get('givenName', '')} {person.get('legalName', {}).get('familyName1', '')}".strip(),
                    email=self._extract_email(person.get("communication", {})),
                    title=job.get("jobTitle", ""),
                    department=job.get("homeOrganizationalUnits", [{}])[0].get("nameCode", {}).get("shortName", "") if job.get("homeOrganizationalUnits") else None,
                    cost_center=job.get("homeCostCenterID", {}).get("idValue", ""),
                    hire_date=self._parse_date(emp_data.get("originalHireDate")),
                    termination_date=self._parse_date(emp_data.get("terminationDate")),
                    employment_status=self._map_status(worker.get("workerStatus", {}).get("statusCode", {}).get("codeValue", "")),
                    pay_type="salary" if job.get("payrollProcessingStatusCode", {}).get("codeValue") == "Salaried" else "hourly",
                    annual_salary=self._parse_decimal(job.get("baseRemuneration", {}).get("annualRateAmount", {}).get("amountValue")),
                    hourly_rate=self._parse_decimal(job.get("baseRemuneration", {}).get("hourlyRateAmount", {}).get("amountValue")),
                ))

        return employees

    async def get_wage_data(self, tax_year: int) -> List[PayrollWageData]:
        """Fetch W-2 wage data from ADP."""
        await self._ensure_token_valid()

        wage_data = []

        async with httpx.AsyncClient() as client:
            # ADP Pay Data / Tax Documents API
            response = await client.get(
                f"{self.base_url}/payroll/v1/workers/*/pay-distributions",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                params={"$filter": f"payDate ge {tax_year}-01-01 and payDate le {tax_year}-12-31"}
            )

            if response.status_code != 200:
                logger.error(f"ADP wage fetch failed: {response.text}")
                return wage_data

            # Process and aggregate wage data by employee
            data = response.json()

            employee_wages = {}
            for pay in data.get("payDistributions", []):
                emp_id = pay.get("associateOID", "")
                if emp_id not in employee_wages:
                    employee_wages[emp_id] = {
                        "w2_wages": Decimal("0"),
                        "gross_pay": Decimal("0"),
                        "federal_tax": Decimal("0"),
                        "ss_wages": Decimal("0"),
                        "ss_tax": Decimal("0"),
                        "medicare_wages": Decimal("0"),
                        "medicare_tax": Decimal("0"),
                        "bonus": Decimal("0"),
                        "overtime": Decimal("0"),
                    }

                earnings = pay.get("grossPay", {}).get("amountValue", 0)
                employee_wages[emp_id]["gross_pay"] += Decimal(str(earnings))
                employee_wages[emp_id]["w2_wages"] += Decimal(str(earnings))

            for emp_id, wages in employee_wages.items():
                wage_data.append(PayrollWageData(
                    employee_id=emp_id,
                    tax_year=tax_year,
                    w2_wages=wages["w2_wages"],
                    federal_tax_withheld=wages["federal_tax"],
                    social_security_wages=wages["ss_wages"],
                    social_security_tax=wages["ss_tax"],
                    medicare_wages=wages["medicare_wages"],
                    medicare_tax=wages["medicare_tax"],
                    state_wages=None,
                    gross_pay=wages["gross_pay"],
                    bonus_pay=wages["bonus"] if wages["bonus"] else None,
                    overtime_pay=wages["overtime"] if wages["overtime"] else None,
                ))

        return wage_data

    async def get_pay_periods(
        self,
        start_date: date,
        end_date: date
    ) -> List[PayPeriodData]:
        """Fetch pay period data from ADP."""
        await self._ensure_token_valid()

        pay_periods = []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/payroll/v1/workers/*/pay-distributions",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                params={
                    "$filter": f"payDate ge {start_date.isoformat()} and payDate le {end_date.isoformat()}"
                }
            )

            if response.status_code != 200:
                logger.error(f"ADP pay periods fetch failed: {response.text}")
                return pay_periods

            data = response.json()

            for pay in data.get("payDistributions", []):
                pay_periods.append(PayPeriodData(
                    employee_id=pay.get("associateOID", ""),
                    pay_date=self._parse_date(pay.get("payDate")) or date.today(),
                    period_start=self._parse_date(pay.get("payPeriod", {}).get("startDate")) or date.today(),
                    period_end=self._parse_date(pay.get("payPeriod", {}).get("endDate")) or date.today(),
                    gross_pay=Decimal(str(pay.get("grossPay", {}).get("amountValue", 0))),
                    regular_hours=pay.get("hoursWorked"),
                    overtime_hours=None,
                    department=None,
                    cost_center=None,
                ))

        return pay_periods

    def _extract_email(self, communication: Dict) -> Optional[str]:
        """Extract email from ADP communication object."""
        emails = communication.get("emails", [])
        for email in emails:
            if email.get("emailUri"):
                return email["emailUri"]
        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse ADP date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse decimal value."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None

    def _map_status(self, status_code: str) -> str:
        """Map ADP status code to standard status."""
        status_map = {
            "A": "active",
            "Active": "active",
            "T": "terminated",
            "Terminated": "terminated",
            "L": "on_leave",
        }
        return status_map.get(status_code, "active")


class JustworksIntegration(PayrollProviderBase):
    """
    Justworks Integration.

    Uses Justworks API for:
    - Employee directory
    - Payroll reports
    - W-2 data
    """

    BASE_URL = "https://api.justworks.com/v1"
    AUTH_URL = "https://secure.justworks.com/oauth/authorize"
    TOKEN_URL = "https://api.justworks.com/oauth/token"

    async def get_auth_url(self, state: str) -> str:
        """Generate Justworks OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "scope": "employees:read payroll:read",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, auth_code: str) -> Dict[str, str]:
        """Exchange authorization code for Justworks tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                json={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                    "redirect_uri": self.config["redirect_uri"],
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                raise ValueError(f"Token exchange failed: {response.text}")

            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            self.token_expires = datetime.now().replace(
                second=datetime.now().second + data.get("expires_in", 3600)
            )

            return data

    async def refresh_access_token(self) -> bool:
        """Refresh Justworks access token."""
        if not self.refresh_token:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                json={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                },
                headers={"Content-Type": "application/json"}
            )

            if response.status_code != 200:
                return False

            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)

            return True

    async def get_employees(self) -> List[PayrollEmployee]:
        """Fetch employee data from Justworks."""
        await self._ensure_token_valid()

        employees = []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/employees",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
            )

            if response.status_code != 200:
                logger.error(f"Justworks employees fetch failed: {response.text}")
                return employees

            data = response.json()

            for emp in data.get("employees", []):
                employees.append(PayrollEmployee(
                    employee_id=emp.get("id", ""),
                    first_name=emp.get("first_name", ""),
                    last_name=emp.get("last_name", ""),
                    full_name=f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip(),
                    email=emp.get("email"),
                    title=emp.get("job_title"),
                    department=emp.get("department", {}).get("name"),
                    cost_center=emp.get("cost_center"),
                    hire_date=self._parse_date(emp.get("hire_date")),
                    termination_date=self._parse_date(emp.get("termination_date")),
                    employment_status=emp.get("status", "active"),
                    pay_type=emp.get("pay_type", "salary"),
                    annual_salary=self._parse_decimal(emp.get("annual_salary")),
                    hourly_rate=self._parse_decimal(emp.get("hourly_rate")),
                ))

        return employees

    async def get_wage_data(self, tax_year: int) -> List[PayrollWageData]:
        """Fetch W-2 wage data from Justworks."""
        await self._ensure_token_valid()

        wage_data = []

        async with httpx.AsyncClient() as client:
            # Justworks W-2 endpoint
            response = await client.get(
                f"{self.BASE_URL}/tax-documents/w2",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                params={"year": tax_year}
            )

            if response.status_code != 200:
                # Fall back to payroll data
                return await self._get_wage_from_payroll(tax_year)

            data = response.json()

            for w2 in data.get("w2_documents", []):
                wage_data.append(PayrollWageData(
                    employee_id=w2.get("employee_id", ""),
                    tax_year=tax_year,
                    w2_wages=Decimal(str(w2.get("box_1_wages", 0))),
                    federal_tax_withheld=Decimal(str(w2.get("box_2_federal_tax", 0))),
                    social_security_wages=Decimal(str(w2.get("box_3_ss_wages", 0))),
                    social_security_tax=Decimal(str(w2.get("box_4_ss_tax", 0))),
                    medicare_wages=Decimal(str(w2.get("box_5_medicare_wages", 0))),
                    medicare_tax=Decimal(str(w2.get("box_6_medicare_tax", 0))),
                    state_wages=None,
                    gross_pay=Decimal(str(w2.get("gross_pay", 0))),
                    bonus_pay=None,
                    overtime_pay=None,
                ))

        return wage_data

    async def _get_wage_from_payroll(self, tax_year: int) -> List[PayrollWageData]:
        """Fall back to aggregating payroll data."""
        pay_periods = await self.get_pay_periods(
            date(tax_year, 1, 1),
            date(tax_year, 12, 31)
        )

        employee_wages = {}
        for period in pay_periods:
            if period.employee_id not in employee_wages:
                employee_wages[period.employee_id] = Decimal("0")
            employee_wages[period.employee_id] += period.gross_pay

        return [
            PayrollWageData(
                employee_id=emp_id,
                tax_year=tax_year,
                w2_wages=wages,
                federal_tax_withheld=Decimal("0"),
                social_security_wages=wages,
                social_security_tax=Decimal("0"),
                medicare_wages=wages,
                medicare_tax=Decimal("0"),
                state_wages=None,
                gross_pay=wages,
                bonus_pay=None,
                overtime_pay=None,
            )
            for emp_id, wages in employee_wages.items()
        ]

    async def get_pay_periods(
        self,
        start_date: date,
        end_date: date
    ) -> List[PayPeriodData]:
        """Fetch pay period data from Justworks."""
        await self._ensure_token_valid()

        pay_periods = []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/payroll/pay-stubs",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                params={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                }
            )

            if response.status_code != 200:
                logger.error(f"Justworks pay periods fetch failed: {response.text}")
                return pay_periods

            data = response.json()

            for stub in data.get("pay_stubs", []):
                pay_periods.append(PayPeriodData(
                    employee_id=stub.get("employee_id", ""),
                    pay_date=self._parse_date(stub.get("pay_date")) or date.today(),
                    period_start=self._parse_date(stub.get("period_start")) or date.today(),
                    period_end=self._parse_date(stub.get("period_end")) or date.today(),
                    gross_pay=Decimal(str(stub.get("gross_pay", 0))),
                    regular_hours=stub.get("regular_hours"),
                    overtime_hours=stub.get("overtime_hours"),
                    department=stub.get("department"),
                    cost_center=stub.get("cost_center"),
                ))

        return pay_periods

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str).date()
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse decimal value."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None


class PaychexIntegration(PayrollProviderBase):
    """
    Paychex Flex Integration.

    Uses Paychex APIs for:
    - Workers API for employee data
    - Payroll API for earnings
    - Tax Management API for W-2 data
    """

    BASE_URL_SANDBOX = "https://api.sandbox.paychex.com"
    BASE_URL_PROD = "https://api.paychex.com"
    AUTH_URL = "https://api.paychex.com/auth/oauth/v2/authorize"
    TOKEN_URL = "https://api.paychex.com/auth/oauth/v2/token"

    def __init__(self, config: Dict[str, str]):
        super().__init__(config)
        self.base_url = (
            self.BASE_URL_PROD
            if config.get("environment") == "production"
            else self.BASE_URL_SANDBOX
        )
        self.company_id = config.get("company_id")

    async def get_auth_url(self, state: str) -> str:
        """Generate Paychex OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.config["client_id"],
            "redirect_uri": self.config["redirect_uri"],
            "scope": "workers payroll",
            "state": state,
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, auth_code: str) -> Dict[str, str]:
        """Exchange authorization code for Paychex tokens."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                    "redirect_uri": self.config["redirect_uri"],
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                raise ValueError(f"Token exchange failed: {response.text}")

            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token")
            self.token_expires = datetime.now().replace(
                second=datetime.now().second + data.get("expires_in", 3600)
            )

            # Get company ID
            if not self.company_id:
                await self._fetch_company_id()

            return data

    async def _fetch_company_id(self):
        """Fetch company ID after authentication."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/companies",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
            )
            if response.status_code == 200:
                data = response.json()
                companies = data.get("content", [])
                if companies:
                    self.company_id = companies[0].get("companyId")

    async def refresh_access_token(self) -> bool:
        """Refresh Paychex access token."""
        if not self.refresh_token:
            return False

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.config["client_id"],
                    "client_secret": self.config["client_secret"],
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

            if response.status_code != 200:
                return False

            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)

            return True

    async def get_employees(self) -> List[PayrollEmployee]:
        """Fetch employee data from Paychex Workers API."""
        await self._ensure_token_valid()

        if not self.company_id:
            await self._fetch_company_id()

        employees = []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/companies/{self.company_id}/workers",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
            )

            if response.status_code != 200:
                logger.error(f"Paychex workers fetch failed: {response.text}")
                return employees

            data = response.json()

            for worker in data.get("content", []):
                name = worker.get("name", {})
                employees.append(PayrollEmployee(
                    employee_id=worker.get("workerId", ""),
                    first_name=name.get("givenName", ""),
                    last_name=name.get("familyName", ""),
                    full_name=f"{name.get('givenName', '')} {name.get('familyName', '')}".strip(),
                    email=self._extract_email(worker.get("communications", [])),
                    title=worker.get("currentPosition", {}).get("jobTitle"),
                    department=worker.get("laborAssignments", [{}])[0].get("laborAssignmentName") if worker.get("laborAssignments") else None,
                    cost_center=None,
                    hire_date=self._parse_date(worker.get("hireDate")),
                    termination_date=self._parse_date(worker.get("terminationDate")),
                    employment_status="active" if worker.get("workerStatus") == "ACTIVE" else "terminated",
                    pay_type="salary" if worker.get("payType") == "SALARY" else "hourly",
                    annual_salary=self._parse_decimal(worker.get("annualSalary")),
                    hourly_rate=self._parse_decimal(worker.get("hourlyRate")),
                ))

        return employees

    async def get_wage_data(self, tax_year: int) -> List[PayrollWageData]:
        """Fetch W-2 wage data from Paychex."""
        await self._ensure_token_valid()

        if not self.company_id:
            await self._fetch_company_id()

        wage_data = []

        async with httpx.AsyncClient() as client:
            # Get check data and aggregate
            response = await client.get(
                f"{self.base_url}/companies/{self.company_id}/checks",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                params={
                    "from": f"{tax_year}-01-01",
                    "to": f"{tax_year}-12-31"
                }
            )

            if response.status_code != 200:
                logger.error(f"Paychex wage fetch failed: {response.text}")
                return wage_data

            data = response.json()

            employee_wages = {}
            for check in data.get("content", []):
                emp_id = check.get("workerId", "")
                if emp_id not in employee_wages:
                    employee_wages[emp_id] = {
                        "gross": Decimal("0"),
                    }
                employee_wages[emp_id]["gross"] += Decimal(str(check.get("grossPay", 0)))

            for emp_id, wages in employee_wages.items():
                wage_data.append(PayrollWageData(
                    employee_id=emp_id,
                    tax_year=tax_year,
                    w2_wages=wages["gross"],
                    federal_tax_withheld=Decimal("0"),
                    social_security_wages=wages["gross"],
                    social_security_tax=Decimal("0"),
                    medicare_wages=wages["gross"],
                    medicare_tax=Decimal("0"),
                    state_wages=None,
                    gross_pay=wages["gross"],
                    bonus_pay=None,
                    overtime_pay=None,
                ))

        return wage_data

    async def get_pay_periods(
        self,
        start_date: date,
        end_date: date
    ) -> List[PayPeriodData]:
        """Fetch pay period data from Paychex."""
        await self._ensure_token_valid()

        if not self.company_id:
            await self._fetch_company_id()

        pay_periods = []

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/companies/{self.company_id}/checks",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                },
                params={
                    "from": start_date.isoformat(),
                    "to": end_date.isoformat()
                }
            )

            if response.status_code != 200:
                logger.error(f"Paychex pay periods fetch failed: {response.text}")
                return pay_periods

            data = response.json()

            for check in data.get("content", []):
                pay_periods.append(PayPeriodData(
                    employee_id=check.get("workerId", ""),
                    pay_date=self._parse_date(check.get("checkDate")) or date.today(),
                    period_start=self._parse_date(check.get("periodBeginDate")) or date.today(),
                    period_end=self._parse_date(check.get("periodEndDate")) or date.today(),
                    gross_pay=Decimal(str(check.get("grossPay", 0))),
                    regular_hours=check.get("regularHours"),
                    overtime_hours=check.get("overtimeHours"),
                    department=None,
                    cost_center=None,
                ))

        return pay_periods

    def _extract_email(self, communications: List[Dict]) -> Optional[str]:
        """Extract email from communications list."""
        for comm in communications:
            if comm.get("communicationType") == "WORK_EMAIL":
                return comm.get("emailAddress")
        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Parse date string."""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
        except (ValueError, TypeError):
            return None

    def _parse_decimal(self, value: Any) -> Optional[Decimal]:
        """Parse decimal value."""
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            return None


class PayrollIntegrationService:
    """
    Main service for managing payroll integrations.

    Provides a unified interface for all supported payroll providers.
    """

    def __init__(self):
        self.integrations: Dict[str, PayrollProviderBase] = {}

    def configure_provider(
        self,
        provider: PayrollProvider,
        config: Dict[str, str]
    ) -> PayrollProviderBase:
        """Configure a payroll provider integration."""
        integration: PayrollProviderBase

        if provider == PayrollProvider.ADP:
            integration = ADPIntegration(config)
        elif provider == PayrollProvider.JUSTWORKS:
            integration = JustworksIntegration(config)
        elif provider == PayrollProvider.PAYCHEX:
            integration = PaychexIntegration(config)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        self.integrations[provider.value] = integration
        return integration

    def get_integration(self, provider: PayrollProvider) -> Optional[PayrollProviderBase]:
        """Get configured integration for a provider."""
        return self.integrations.get(provider.value)

    async def fetch_all_data(
        self,
        provider: PayrollProvider,
        tax_year: int
    ) -> PayrollIntegrationResult:
        """Fetch all payroll data from a provider."""
        integration = self.get_integration(provider)

        if not integration:
            return PayrollIntegrationResult(
                provider=provider,
                success=False,
                employees=[],
                wage_data=[],
                pay_periods=[],
                error_message="Provider not configured",
                sync_timestamp=datetime.now()
            )

        try:
            employees = await integration.get_employees()
            wage_data = await integration.get_wage_data(tax_year)
            pay_periods = await integration.get_pay_periods(
                date(tax_year, 1, 1),
                date(tax_year, 12, 31)
            )

            return PayrollIntegrationResult(
                provider=provider,
                success=True,
                employees=employees,
                wage_data=wage_data,
                pay_periods=pay_periods,
                error_message=None,
                sync_timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Payroll fetch failed for {provider}: {e}")
            return PayrollIntegrationResult(
                provider=provider,
                success=False,
                employees=[],
                wage_data=[],
                pay_periods=[],
                error_message=str(e),
                sync_timestamp=datetime.now()
            )
