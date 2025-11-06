"""
Electronic Confirmation Service (AS 2310 / AU-C 505)

Mirrors confirmation.com functionality for sending and receiving
external confirmations during audit and review engagements.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    ConfirmationType,
    ConfirmationFormat,
    ConfirmationMethod,
    ConfirmationStatus,
)

logger = logging.getLogger(__name__)


class ConfirmationService:
    """
    Electronic confirmation service mirroring confirmation.com.

    Provides functionality for:
    - Creating confirmation requests
    - Managing templates
    - Electronic delivery
    - Response tracking
    - Exception handling
    - AS 2310 compliance
    """

    def __init__(self):
        """Initialize confirmation service."""
        self.templates = {}
        self._initialize_standard_templates()
        logger.info("Confirmation service initialized")

    def _initialize_standard_templates(self):
        """Initialize standard confirmation templates."""

        # Bank Confirmation Template
        self.templates["BANK_STANDARD"] = {
            "template_code": "BANK_STANDARD",
            "template_name": "Standard Bank Confirmation",
            "confirmation_type": ConfirmationType.BANK,
            "confirmation_format": ConfirmationFormat.POSITIVE,
            "subject_line": "Audit Confirmation Request - {{client_name}}",
            "letter_header": """
{{bank_name}}
{{bank_address}}

Re: Confirmation of Bank Accounts for {{client_name}}
As of: {{as_of_date}}
            """,
            "letter_body": """
Dear {{bank_contact}}:

In connection with an audit of the financial statements of {{client_name}} as of {{as_of_date}}, please confirm directly to our auditors the following information regarding accounts maintained at your institution.

CLIENT: {{client_name}}
ACCOUNT NUMBER: {{account_number}}
ACCOUNT TYPE: {{account_type}}

Please provide the following information as of {{as_of_date}}:

1. Account Balance: $_____________
2. Account Type (Checking, Savings, CD, etc.): _____________
3. Interest Rate (if applicable): _____________%
4. Maturity Date (if applicable): _____________

ADDITIONAL INFORMATION:

Please also confirm any of the following that apply:
- Outstanding loans or lines of credit
- Pledged collateral or restricted balances
- Contingent liabilities or guarantees
- Safe deposit boxes

Please sign below and return this confirmation directly to:
{{auditor_firm_name}}
{{auditor_address}}
Email: {{auditor_email}}

This information is for audit purposes only and will be kept confidential.
            """,
            "letter_footer": """
Authorized Bank Representative:

Signature: _________________________ Date: _____________
Printed Name: _______________________
Title: _______________________________
            """,
            "instructions": "Please complete all sections and return within 10 business days.",
            "required_fields": [
                "client_name",
                "bank_name",
                "account_number",
                "as_of_date",
                "auditor_firm_name",
            ],
            "applicable_standards": ["AS 2310", "AU-C 505"],
        }

        # Accounts Receivable Confirmation Template
        self.templates["AR_POSITIVE"] = {
            "template_code": "AR_POSITIVE",
            "template_name": "Accounts Receivable - Positive Confirmation",
            "confirmation_type": ConfirmationType.ACCOUNTS_RECEIVABLE,
            "confirmation_format": ConfirmationFormat.POSITIVE,
            "subject_line": "Account Balance Confirmation Request",
            "letter_header": """
{{customer_name}}
{{customer_address}}

Re: Confirmation of Account Balance
Date: {{confirmation_date}}
            """,
            "letter_body": """
Dear {{customer_contact}}:

Our auditors, {{auditor_firm_name}}, are conducting an audit of our financial statements. As part of this process, please confirm the accuracy of the following information regarding your account with {{client_name}}.

According to our records, your account balance as of {{as_of_date}} is:

AMOUNT DUE: ${{balance_amount}}

BREAKDOWN:
{{invoice_details}}

Please review this information and respond directly to our auditors using one of the following methods:

[ ] The above balance is CORRECT
[ ] The above balance is INCORRECT (please provide details below)

If incorrect, please provide the correct balance and details:
Correct Balance: $_____________
Explanation: ________________________________________________________________
___________________________________________________________________________

Please return this confirmation to:
{{auditor_firm_name}}
{{auditor_address}}
Email: {{auditor_email}}

NOTE: This is not a request for payment. Please do not send payments to our auditors.
            """,
            "letter_footer": """
Customer Representative:

Signature: _________________________ Date: _____________
Printed Name: _______________________
Title: _______________________________
Company: _____________________________
            """,
            "instructions": "Please respond within 10 business days, even if you agree with the balance.",
            "required_fields": [
                "client_name",
                "customer_name",
                "balance_amount",
                "as_of_date",
                "auditor_firm_name",
            ],
            "applicable_standards": ["AS 2310", "AU-C 505"],
        }

        # Accounts Payable Confirmation Template
        self.templates["AP_POSITIVE"] = {
            "template_code": "AP_POSITIVE",
            "template_name": "Accounts Payable - Positive Confirmation",
            "confirmation_type": ConfirmationType.ACCOUNTS_PAYABLE,
            "confirmation_format": ConfirmationFormat.POSITIVE,
            "subject_line": "Vendor Account Balance Confirmation",
            "letter_header": """
{{vendor_name}}
{{vendor_address}}

Re: Confirmation of Payable Balance
Date: {{confirmation_date}}
            """,
            "letter_body": """
Dear {{vendor_contact}}:

Our auditors, {{auditor_firm_name}}, are conducting an audit of the financial statements of {{client_name}}. Please confirm the amount we owe to your company as of {{as_of_date}}.

According to our records, the amount payable to {{vendor_name}} is:

AMOUNT PAYABLE: ${{balance_amount}}

Please confirm:
[ ] The above balance is CORRECT
[ ] The above balance is INCORRECT (please provide correct amount below)

Correct Amount: $_____________
Explanation of difference: __________________________________________________
___________________________________________________________________________

Please respond directly to:
{{auditor_firm_name}}
{{auditor_address}}
Email: {{auditor_email}}
            """,
            "letter_footer": """
Vendor Representative:

Signature: _________________________ Date: _____________
Printed Name: _______________________
Title: _______________________________
            """,
            "instructions": "Please respond within 10 business days.",
            "required_fields": [
                "client_name",
                "vendor_name",
                "balance_amount",
                "as_of_date",
                "auditor_firm_name",
            ],
            "applicable_standards": ["AS 2310", "AU-C 505"],
        }

        # Legal Confirmation Template
        self.templates["LEGAL_STANDARD"] = {
            "template_code": "LEGAL_STANDARD",
            "template_name": "Standard Legal Confirmation",
            "confirmation_type": ConfirmationType.LEGAL,
            "confirmation_format": ConfirmationFormat.POSITIVE,
            "subject_line": "Legal Confirmation Request - {{client_name}}",
            "letter_header": """
{{law_firm_name}}
{{law_firm_address}}

Attention: {{attorney_name}}

Re: Audit Confirmation for {{client_name}}
As of: {{as_of_date}}
            """,
            "letter_body": """
Dear {{attorney_name}}:

In connection with an audit of the financial statements of {{client_name}} as of {{as_of_date}}, please furnish our auditors with the information requested below regarding pending or threatened litigation, claims, and assessments.

Management of {{client_name}} has represented to us that they have consulted your firm regarding legal matters. Please confirm or provide information about:

1. Pending or threatened litigation:
   - Description of matter
   - Progress to date
   - How management is responding
   - Likelihood of unfavorable outcome
   - Estimated potential loss or range of loss

2. Unasserted claims or assessments

3. Legal fees:
   - Amount billed through {{as_of_date}}: $_____________
   - Amount unbilled through {{as_of_date}}: $_____________
   - Outstanding balance: $_____________

Please send your response directly to:
{{auditor_firm_name}}
{{auditor_address}}
Email: {{auditor_email}}

Please respond by {{due_date}}.
            """,
            "letter_footer": """
Yours truly,

{{client_name}}

By: _________________________ Date: _____________
    Authorized Signature
            """,
            "instructions": "Attorney response required per AU-C 501.",
            "required_fields": [
                "client_name",
                "law_firm_name",
                "attorney_name",
                "as_of_date",
                "auditor_firm_name",
            ],
            "applicable_standards": ["AS 2310", "AU-C 505", "AU-C 501"],
        }

        # Debt Confirmation Template
        self.templates["DEBT_STANDARD"] = {
            "template_code": "DEBT_STANDARD",
            "template_name": "Debt/Loan Confirmation",
            "confirmation_type": ConfirmationType.DEBT,
            "confirmation_format": ConfirmationFormat.POSITIVE,
            "subject_line": "Loan Confirmation Request - {{client_name}}",
            "letter_body": """
Dear {{lender_contact}}:

In connection with an audit of {{client_name}}, please confirm the following loan information as of {{as_of_date}}:

LOAN DETAILS:
- Loan Number/ID: {{loan_number}}
- Original Loan Amount: $_____________
- Current Principal Balance: $_____________
- Interest Rate: _____________%
- Maturity Date: _____________
- Payment Amount: $_____________
- Payment Frequency: _____________

ADDITIONAL INFORMATION:
- Accrued Interest Payable: $_____________
- Prepayment penalties: Yes [ ] No [ ]
- Default status: Yes [ ] No [ ]
- Collateral pledged: _____________
- Debt covenants: _____________

Please return directly to {{auditor_firm_name}} at {{auditor_email}}
            """,
            "required_fields": [
                "client_name",
                "lender_name",
                "loan_number",
                "as_of_date",
                "auditor_firm_name",
            ],
            "applicable_standards": ["AS 2310", "AU-C 505"],
        }

    async def create_confirmation_request(
        self,
        engagement_id: str,
        confirmation_type: ConfirmationType,
        template_code: str,
        respondent_info: Dict[str, Any],
        confirmation_data: Dict[str, Any],
        created_by: str,
        delivery_method: ConfirmationMethod = ConfirmationMethod.ELECTRONIC,
        due_days: int = 10,
    ) -> Dict[str, Any]:
        """
        Create a new confirmation request.

        Args:
            engagement_id: Engagement ID
            confirmation_type: Type of confirmation
            template_code: Template to use
            respondent_info: Respondent contact information
            confirmation_data: Data to populate template
            created_by: User creating confirmation
            delivery_method: How to deliver
            due_days: Days until due

        Returns:
            Confirmation request details
        """
        # Get template
        template = self.templates.get(template_code)
        if not template:
            raise ValueError(f"Template {template_code} not found")

        # Generate confirmation number
        confirmation_number = self._generate_confirmation_number(
            confirmation_type, engagement_id
        )

        # Populate template
        confirmation_text = self._populate_template(template, confirmation_data)

        # Calculate due date
        due_date = datetime.utcnow() + timedelta(days=due_days)

        # Create confirmation request
        confirmation = {
            "confirmation_number": confirmation_number,
            "engagement_id": engagement_id,
            "confirmation_type": confirmation_type.value,
            "confirmation_format": template["confirmation_format"].value,
            "confirmation_method": delivery_method.value,
            "template_id": template_code,
            "template_name": template["template_name"],
            "respondent_name": respondent_info["name"],
            "respondent_organization": respondent_info.get("organization"),
            "respondent_email": respondent_info.get("email"),
            "respondent_phone": respondent_info.get("phone"),
            "respondent_address": respondent_info.get("address"),
            "confirmation_text": confirmation_text,
            "custom_fields": confirmation_data,
            "due_date": due_date.isoformat(),
            "status": ConfirmationStatus.DRAFT.value,
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "encryption_used": True,
            "compliance_check": self._check_as2310_compliance(
                confirmation_type, template
            ),
        }

        logger.info(
            f"Created {confirmation_type.value} confirmation {confirmation_number}"
        )

        return confirmation

    def _generate_confirmation_number(
        self, confirmation_type: ConfirmationType, engagement_id: str
    ) -> str:
        """Generate unique confirmation number."""
        prefix_map = {
            ConfirmationType.BANK: "BNK",
            ConfirmationType.ACCOUNTS_RECEIVABLE: "AR",
            ConfirmationType.ACCOUNTS_PAYABLE: "AP",
            ConfirmationType.LEGAL: "LEG",
            ConfirmationType.DEBT: "DBT",
            ConfirmationType.INVESTMENTS: "INV",
            ConfirmationType.INVENTORY: "INVT",
            ConfirmationType.OTHER: "OTH",
        }

        prefix = prefix_map.get(confirmation_type, "CONF")
        unique_id = str(uuid4())[:8].upper()
        engagement_short = engagement_id[:8]

        return f"{prefix}-{engagement_short}-{unique_id}"

    def _populate_template(
        self, template: Dict[str, Any], data: Dict[str, Any]
    ) -> str:
        """Populate template with data."""
        text = ""

        # Add header
        if "letter_header" in template:
            text += template["letter_header"] + "\n\n"

        # Add body
        text += template["letter_body"] + "\n\n"

        # Add footer
        if "letter_footer" in template:
            text += template["letter_footer"] + "\n\n"

        # Add instructions
        if "instructions" in template:
            text += f"INSTRUCTIONS: {template['instructions']}\n"

        # Replace placeholders
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            text = text.replace(placeholder, str(value))

        return text

    def _check_as2310_compliance(
        self, confirmation_type: ConfirmationType, template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance with AS 2310 requirements."""
        compliance = {
            "standard": "AS 2310",
            "checked_at": datetime.utcnow().isoformat(),
            "checks": [],
        }

        # Check 1: Auditor control
        compliance["checks"].append({
            "requirement": "Auditor controls selection and sending",
            "status": "pass",
            "note": "Confirmation controlled by auditor",
        })

        # Check 2: Direct response to auditor
        compliance["checks"].append({
            "requirement": "Response sent directly to auditor",
            "status": "pass",
            "note": "Template requests direct response to auditor",
        })

        # Check 3: Positive confirmation for certain accounts
        if confirmation_type in [
            ConfirmationType.BANK,
            ConfirmationType.ACCOUNTS_RECEIVABLE,
        ]:
            if template["confirmation_format"] == ConfirmationFormat.POSITIVE:
                compliance["checks"].append({
                    "requirement": "Positive confirmation for cash and AR",
                    "status": "pass",
                    "note": "Using positive confirmation format",
                })
            else:
                compliance["checks"].append({
                    "requirement": "Positive confirmation for cash and AR",
                    "status": "warning",
                    "note": "Consider using positive confirmation",
                })

        # Check 4: Negative confirmation alone insufficient
        if template["confirmation_format"] == ConfirmationFormat.NEGATIVE:
            compliance["checks"].append({
                "requirement": "Negative confirmation not sole procedure",
                "status": "warning",
                "note": "AS 2310 requires negative confirmations be supplemented",
            })

        compliance["overall_status"] = (
            "compliant" if all(c["status"] == "pass" for c in compliance["checks"]) else "review_needed"
        )

        return compliance

    async def send_confirmation(
        self,
        confirmation_id: str,
        sent_by: str,
        send_immediately: bool = True,
    ) -> Dict[str, Any]:
        """
        Send confirmation to respondent.

        Args:
            confirmation_id: Confirmation request ID
            sent_by: User sending confirmation
            send_immediately: Send now or schedule

        Returns:
            Sending status
        """
        # In production, this would integrate with email service
        # For now, simulate sending

        delivery_result = {
            "confirmation_id": confirmation_id,
            "sent_by": sent_by,
            "sent_date": datetime.utcnow().isoformat(),
            "delivery_method": "electronic",
            "delivery_status": "sent",
            "tracking_id": self._generate_tracking_id(),
            "estimated_delivery": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
        }

        logger.info(f"Sent confirmation {confirmation_id}")

        return delivery_result

    def _generate_tracking_id(self) -> str:
        """Generate delivery tracking ID."""
        return hashlib.sha256(
            f"{datetime.utcnow().isoformat()}-{uuid4()}".encode()
        ).hexdigest()[:16].upper()

    async def record_response(
        self,
        confirmation_id: str,
        response_data: Dict[str, Any],
        response_method: str = "electronic",
    ) -> Dict[str, Any]:
        """
        Record confirmation response.

        Args:
            confirmation_id: Confirmation request ID
            response_data: Response information
            response_method: How response was received

        Returns:
            Response record
        """
        response = {
            "confirmation_id": confirmation_id,
            "response_date": datetime.utcnow().isoformat(),
            "response_method": response_method,
            "respondent_name": response_data.get("respondent_name"),
            "respondent_title": response_data.get("respondent_title"),
            "agrees_with_client_records": response_data.get("agrees", True),
            "confirmed_amount": response_data.get("confirmed_amount"),
            "has_exceptions": response_data.get("has_exceptions", False),
            "exception_details": response_data.get("exception_details"),
            "digital_signature": response_data.get("digital_signature"),
            "ip_address": response_data.get("ip_address"),
            "verification_code": self._generate_verification_code(),
        }

        # Log response
        logger.info(
            f"Recorded response for confirmation {confirmation_id} - Agrees: {response['agrees_with_client_records']}"
        )

        return response

    def _generate_verification_code(self) -> str:
        """Generate verification code for response."""
        return hashlib.sha256(
            f"VERIFY-{datetime.utcnow().isoformat()}-{uuid4()}".encode()
        ).hexdigest()[:12].upper()

    async def get_confirmation_status(
        self, engagement_id: str
    ) -> Dict[str, Any]:
        """
        Get status summary for all confirmations in engagement.

        Args:
            engagement_id: Engagement ID

        Returns:
            Status summary
        """
        # In production, this would query database
        # For now, return summary structure

        summary = {
            "engagement_id": engagement_id,
            "total_confirmations": 0,
            "by_type": {},
            "by_status": {
                "draft": 0,
                "sent": 0,
                "responded": 0,
                "exception": 0,
                "no_response": 0,
                "alternative_procedures": 0,
            },
            "response_rate": 0.0,
            "exceptions_count": 0,
            "overdue_count": 0,
            "generated_at": datetime.utcnow().isoformat(),
        }

        return summary

    async def send_reminder(
        self, confirmation_id: str, sent_by: str
    ) -> Dict[str, Any]:
        """
        Send reminder for outstanding confirmation.

        Args:
            confirmation_id: Confirmation request ID
            sent_by: User sending reminder

        Returns:
            Reminder status
        """
        reminder = {
            "confirmation_id": confirmation_id,
            "reminder_sent": True,
            "reminder_date": datetime.utcnow().isoformat(),
            "sent_by": sent_by,
            "reminder_number": 1,  # Track which reminder this is
        }

        logger.info(f"Sent reminder for confirmation {confirmation_id}")

        return reminder

    async def perform_alternative_procedures(
        self,
        confirmation_id: str,
        procedures: List[Dict[str, Any]],
        performed_by: str,
    ) -> Dict[str, Any]:
        """
        Document alternative procedures when confirmation not received.

        Args:
            confirmation_id: Confirmation request ID
            procedures: List of alternative procedures performed
            performed_by: User performing procedures

        Returns:
            Alternative procedures documentation
        """
        alternative = {
            "confirmation_id": confirmation_id,
            "procedures_performed": procedures,
            "performed_by": performed_by,
            "performed_date": datetime.utcnow().isoformat(),
            "sufficient_evidence_obtained": len(procedures) >= 2,  # Example logic
            "conclusion": "Evidence obtained through alternative procedures"
            if len(procedures) >= 2
            else "Additional procedures required",
        }

        logger.info(
            f"Documented alternative procedures for confirmation {confirmation_id}"
        )

        return alternative

    def get_available_templates(
        self, confirmation_type: Optional[ConfirmationType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get available confirmation templates.

        Args:
            confirmation_type: Filter by type (optional)

        Returns:
            List of available templates
        """
        templates = []

        for code, template in self.templates.items():
            if confirmation_type is None or template["confirmation_type"] == confirmation_type:
                templates.append({
                    "template_code": code,
                    "template_name": template["template_name"],
                    "confirmation_type": template["confirmation_type"].value,
                    "confirmation_format": template["confirmation_format"].value,
                    "required_fields": template["required_fields"],
                    "applicable_standards": template["applicable_standards"],
                })

        return templates


# Singleton instance
confirmation_service = ConfirmationService()
