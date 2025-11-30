"""
Payroll and Data Integration Services

Provides integrations with major payroll providers and data sources:
- ADP Run (RUN Powered by ADP)
- ADP Workforce Now
- Justworks
- Paychex Flex
"""

from .payroll_integrations import (
    PayrollProvider,
    PayrollEmployee,
    PayrollWageData,
    PayPeriodData,
    PayrollIntegrationResult,
    PayrollIntegrationService,
    ADPIntegration,
    JustworksIntegration,
    PaychexIntegration,
)

# OAuth-based providers
from .payroll_providers import (
    PayrollProviderBase,
    ADPRunProvider,
    JustworksProvider,
    PaychexFlexProvider,
    PayrollConnection,
    get_payroll_provider,
    PAYROLL_PROVIDERS,
)

__all__ = [
    # Legacy integrations
    "PayrollProvider",
    "PayrollEmployee",
    "PayrollWageData",
    "PayPeriodData",
    "PayrollIntegrationResult",
    "PayrollIntegrationService",
    "ADPIntegration",
    "JustworksIntegration",
    "PaychexIntegration",
    # OAuth-based providers
    "PayrollProviderBase",
    "ADPRunProvider",
    "JustworksProvider",
    "PaychexFlexProvider",
    "PayrollConnection",
    "get_payroll_provider",
    "PAYROLL_PROVIDERS",
]
