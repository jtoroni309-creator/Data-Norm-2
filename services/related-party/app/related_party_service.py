"""
Related Party Transactions Service

Implements PCAOB AS 1320: Consideration of an Entity's Relationships and Transactions
with Related Parties and AS 2410: Related Parties

Key Requirements:
- Identify all related party relationships
- Identify and test related party transactions
- Evaluate economic substance vs legal form
- Assess disclosure completeness
- Test for undisclosed related parties

Related Party Scope (ASC 850):
- Parent-subsidiary relationships
- Affiliates
- Principal owners (>10% ownership)
- Management and their immediate families
- Other parties that can exercise significant influence
"""

import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class RelatedPartyType(str, Enum):
    """Types of related party relationships"""
    PARENT_COMPANY = "parent_company"
    SUBSIDIARY = "subsidiary"
    AFFILIATE = "affiliate"
    JOINT_VENTURE = "joint_venture"
    PRINCIPAL_OWNER = "principal_owner"  # >10% ownership
    EXECUTIVE_MANAGEMENT = "executive_management"  # CEO, CFO, etc.
    BOARD_MEMBER = "board_member"
    KEY_MANAGEMENT = "key_management"
    IMMEDIATE_FAMILY = "immediate_family"  # Family of key management
    ENTITY_UNDER_COMMON_CONTROL = "common_control"
    SIGNIFICANT_INFLUENCE = "significant_influence"  # Can influence but <50% ownership


class TransactionType(str, Enum):
    """Types of related party transactions"""
    SALE_OF_GOODS = "sale_of_goods"
    PURCHASE_OF_GOODS = "purchase_of_goods"
    SALE_OF_ASSETS = "sale_of_assets"
    PURCHASE_OF_ASSETS = "purchase_of_assets"
    LOAN_RECEIVABLE = "loan_receivable"
    LOAN_PAYABLE = "loan_payable"
    LEASE_AGREEMENT = "lease_agreement"
    SERVICE_AGREEMENT = "service_agreement"
    GUARANTEE = "guarantee"
    MANAGEMENT_COMPENSATION = "management_compensation"
    EQUITY_TRANSACTION = "equity_transaction"
    TRANSFER_PRICING = "transfer_pricing"
    CASH_ADVANCE = "cash_advance"


class SubstanceRating(str, Enum):
    """Economic substance assessment"""
    CLEAR_BUSINESS_PURPOSE = "clear_business_purpose"
    LEGITIMATE_BUT_UNUSUAL = "legitimate_but_unusual"
    QUESTIONABLE_SUBSTANCE = "questionable_substance"
    LACKS_BUSINESS_PURPOSE = "lacks_business_purpose"


class ArmLengthAssessment(str, Enum):
    """Arms-length assessment"""
    AT_MARKET_RATE = "at_market_rate"
    FAVORABLE_TO_COMPANY = "favorable_to_company"
    FAVORABLE_TO_RELATED_PARTY = "favorable_to_related_party"
    SIGNIFICANTLY_OFF_MARKET = "significantly_off_market"


class RelatedPartyService:
    """
    Service for identifying and testing related party transactions.

    Implements PCAOB AS 1320 and AS 2410 requirements.
    """

    def __init__(self):
        """Initialize related party service"""
        self.identified_parties: Set[str] = set()
        self.ownership_relationships: Dict[str, Dict] = {}

    def identify_related_parties(
        self,
        ownership_structure: List[Dict],  # [{"entity": "ABC Corp", "ownership_percent": 35}]
        management_list: List[Dict],  # [{"name": "John Doe", "title": "CEO"}]
        board_members: List[str],
        significant_vendors: List[Dict],  # Check for common ownership
        significant_customers: List[Dict],
    ) -> Dict:
        """
        Identify all related parties that require disclosure.

        AS 1320.04: Auditor must obtain understanding of company's related
        party relationships and transactions.

        Args:
            ownership_structure: List of entities with ownership relationships
            management_list: List of executive management
            board_members: List of board of directors members
            significant_vendors: Major vendors (to check for common ownership)
            significant_customers: Major customers (to check for common ownership)

        Returns:
            Dictionary of identified related parties by type
        """
        related_parties = {
            "parent_companies": [],
            "subsidiaries": [],
            "affiliates": [],
            "principal_owners": [],
            "executive_management": [],
            "board_members": board_members,
            "potential_undisclosed": [],
        }

        # Identify ownership-based relationships
        for entity in ownership_structure:
            name = entity["entity"]
            ownership = Decimal(str(entity.get("ownership_percent", 0)))

            if entity.get("owns_company", False) and ownership > 50:
                related_parties["parent_companies"].append({
                    "name": name,
                    "ownership_percent": float(ownership),
                    "type": RelatedPartyType.PARENT_COMPANY.value,
                })
            elif entity.get("owned_by_company", False) and ownership > 50:
                related_parties["subsidiaries"].append({
                    "name": name,
                    "ownership_percent": float(ownership),
                    "type": RelatedPartyType.SUBSIDIARY.value,
                })
            elif ownership > 10:
                related_parties["principal_owners"].append({
                    "name": name,
                    "ownership_percent": float(ownership),
                    "type": RelatedPartyType.PRINCIPAL_OWNER.value,
                })
            elif ownership > 0 or entity.get("significant_influence", False):
                related_parties["affiliates"].append({
                    "name": name,
                    "ownership_percent": float(ownership),
                    "type": RelatedPartyType.AFFILIATE.value,
                })

            self.identified_parties.add(name)

        # Identify management-based relationships
        for person in management_list:
            related_parties["executive_management"].append({
                "name": person["name"],
                "title": person["title"],
                "type": RelatedPartyType.EXECUTIVE_MANAGEMENT.value,
            })
            self.identified_parties.add(person["name"])

        # Check for undisclosed related parties (red flags)
        for vendor in significant_vendors:
            if self._check_potential_undisclosed_party(vendor):
                related_parties["potential_undisclosed"].append({
                    "name": vendor["name"],
                    "reason": "Significant vendor with potential ownership connection",
                    "requires_investigation": True,
                })

        for customer in significant_customers:
            if self._check_potential_undisclosed_party(customer):
                related_parties["potential_undisclosed"].append({
                    "name": customer["name"],
                    "reason": "Significant customer with potential ownership connection",
                    "requires_investigation": True,
                })

        return {
            "related_parties": related_parties,
            "total_identified": len(self.identified_parties),
            "requires_disclosure": self._count_disclosure_required(related_parties),
            "potential_undisclosed_count": len(related_parties["potential_undisclosed"]),
        }

    def evaluate_transaction_substance(
        self,
        transaction_description: str,
        transaction_type: TransactionType,
        amount: Decimal,
        terms: Dict,
        business_rationale: str,
        market_comparison: Optional[Dict] = None,
    ) -> Dict:
        """
        Evaluate economic substance of related party transaction.

        AS 1320.12: Auditor should evaluate whether related party transaction
        has been recorded in accordance with economic substance.

        Args:
            transaction_description: Description of transaction
            transaction_type: Type of transaction
            amount: Transaction amount
            terms: Terms (interest rate, payment terms, etc.)
            business_rationale: Management's stated business purpose
            market_comparison: Comparison to market terms if available

        Returns:
            Substance evaluation
        """
        red_flags = []
        substance_score = 100  # Start at 100, deduct for red flags

        # Check for missing business rationale
        if not business_rationale or len(business_rationale) < 20:
            red_flags.append("Inadequate business rationale provided")
            substance_score -= 30

        # Check terms against market
        if market_comparison:
            terms_assessment = self._evaluate_transaction_terms(
                terms, market_comparison, transaction_type
            )
            if terms_assessment["off_market"]:
                red_flags.append(f"Terms are off-market: {terms_assessment['description']}")
                substance_score -= 25

        # Check for unusual timing
        if terms.get("near_period_end", False):
            red_flags.append("Transaction occurred near period end")
            substance_score -= 15

        # Check for unusual structure
        if terms.get("complex_structure", False):
            red_flags.append("Unusually complex transaction structure")
            substance_score -= 20

        # Check for lack of documentation
        if not terms.get("written_agreement", True):
            red_flags.append("No written agreement")
            substance_score -= 20

        # Determine substance rating
        if substance_score >= 90:
            substance = SubstanceRating.CLEAR_BUSINESS_PURPOSE
            audit_conclusion = "Transaction appears to have clear business purpose and substance"
        elif substance_score >= 70:
            substance = SubstanceRating.LEGITIMATE_BUT_UNUSUAL
            audit_conclusion = "Transaction has business purpose but requires additional procedures"
        elif substance_score >= 50:
            substance = SubstanceRating.QUESTIONABLE_SUBSTANCE
            audit_conclusion = "Economic substance is questionable. Consider disclosure implications"
        else:
            substance = SubstanceRating.LACKS_BUSINESS_PURPOSE
            audit_conclusion = "Transaction may lack economic substance. Consult with specialists"

        return {
            "transaction_description": transaction_description,
            "transaction_type": transaction_type.value,
            "amount": float(amount),
            "substance_rating": substance.value,
            "substance_score": substance_score,
            "red_flags": red_flags if red_flags else ["None identified"],
            "audit_conclusion": audit_conclusion,
            "requires_disclosure": True,  # All related party transactions require disclosure
            "additional_procedures_required": substance_score < 70,
        }

    def test_arms_length_terms(
        self,
        transaction_type: TransactionType,
        related_party_terms: Dict,
        market_terms: Dict,
    ) -> Dict:
        """
        Test whether related party transaction is at arm's length.

        Compare transaction terms to market terms for similar transactions.

        Args:
            transaction_type: Type of transaction
            related_party_terms: Terms of related party transaction
            market_terms: Market terms for comparable transactions

        Returns:
            Arms-length assessment
        """
        assessment_details = []
        overall_conclusion = ArmLengthAssessment.AT_MARKET_RATE

        # Interest rate comparison (for loans)
        if "interest_rate" in related_party_terms and "interest_rate" in market_terms:
            rp_rate = Decimal(str(related_party_terms["interest_rate"]))
            market_rate = Decimal(str(market_terms["interest_rate"]))
            rate_diff = rp_rate - market_rate
            rate_diff_pct = (rate_diff / market_rate * 100) if market_rate != 0 else 0

            if abs(rate_diff_pct) < 5:
                assessment_details.append({
                    "term": "Interest Rate",
                    "related_party_value": float(rp_rate),
                    "market_value": float(market_rate),
                    "variance_percent": round(float(rate_diff_pct), 2),
                    "assessment": "At market rate",
                })
            elif rate_diff_pct < -10:
                assessment_details.append({
                    "term": "Interest Rate",
                    "related_party_value": float(rp_rate),
                    "market_value": float(market_rate),
                    "variance_percent": round(float(rate_diff_pct), 2),
                    "assessment": "Below market (favorable to company)",
                })
                overall_conclusion = ArmLengthAssessment.FAVORABLE_TO_COMPANY
            elif rate_diff_pct > 10:
                assessment_details.append({
                    "term": "Interest Rate",
                    "related_party_value": float(rp_rate),
                    "market_value": float(market_rate),
                    "variance_percent": round(float(rate_diff_pct), 2),
                    "assessment": "Above market (favorable to related party)",
                })
                overall_conclusion = ArmLengthAssessment.FAVORABLE_TO_RELATED_PARTY

        # Price comparison (for goods/services)
        if "price_per_unit" in related_party_terms and "price_per_unit" in market_terms:
            rp_price = Decimal(str(related_party_terms["price_per_unit"]))
            market_price = Decimal(str(market_terms["price_per_unit"]))
            price_diff = rp_price - market_price
            price_diff_pct = (price_diff / market_price * 100) if market_price != 0 else 0

            if abs(price_diff_pct) < 10:
                assessment_details.append({
                    "term": "Price",
                    "related_party_value": float(rp_price),
                    "market_value": float(market_price),
                    "variance_percent": round(float(price_diff_pct), 2),
                    "assessment": "At market rate",
                })
            elif abs(price_diff_pct) > 25:
                overall_conclusion = ArmLengthAssessment.SIGNIFICANTLY_OFF_MARKET
                assessment_details.append({
                    "term": "Price",
                    "related_party_value": float(rp_price),
                    "market_value": float(market_price),
                    "variance_percent": round(float(price_diff_pct), 2),
                    "assessment": "Significantly off market",
                })

        # Payment terms comparison
        if "payment_days" in related_party_terms and "payment_days" in market_terms:
            rp_days = int(related_party_terms["payment_days"])
            market_days = int(market_terms["payment_days"])
            days_diff = rp_days - market_days

            if abs(days_diff) <= 15:  # Within 15 days
                assessment_details.append({
                    "term": "Payment Terms",
                    "related_party_value": rp_days,
                    "market_value": market_days,
                    "variance_days": days_diff,
                    "assessment": "Standard terms",
                })
            else:
                assessment_details.append({
                    "term": "Payment Terms",
                    "related_party_value": rp_days,
                    "market_value": market_days,
                    "variance_days": days_diff,
                    "assessment": "Non-standard terms",
                })

        # Determine audit implications
        if overall_conclusion == ArmLengthAssessment.SIGNIFICANTLY_OFF_MARKET:
            audit_implication = "Transaction terms are significantly off-market. High risk of improper accounting or disclosure"
        elif overall_conclusion in [ArmLengthAssessment.FAVORABLE_TO_COMPANY, ArmLengthAssessment.FAVORABLE_TO_RELATED_PARTY]:
            audit_implication = "Transaction terms favor one party. Assess for economic substance and proper disclosure"
        else:
            audit_implication = "Transaction appears to be at arm's length"

        return {
            "transaction_type": transaction_type.value,
            "overall_assessment": overall_conclusion.value,
            "term_comparisons": assessment_details,
            "audit_implication": audit_implication,
            "requires_enhanced_procedures": overall_conclusion != ArmLengthAssessment.AT_MARKET_RATE,
        }

    def assess_disclosure_completeness(
        self,
        identified_relationships: List[Dict],
        disclosed_relationships: List[Dict],
        identified_transactions: List[Dict],
        disclosed_transactions: List[Dict],
    ) -> Dict:
        """
        Assess completeness of related party disclosures.

        ASC 850 requires disclosure of:
        - Nature of relationships
        - Description of transactions
        - Dollar amounts of transactions
        - Amounts due to/from related parties

        Args:
            identified_relationships: All relationships auditor identified
            disclosed_relationships: Relationships disclosed in financial statements
            identified_transactions: All transactions auditor identified
            disclosed_transactions: Transactions disclosed in financial statements

        Returns:
            Disclosure completeness assessment
        """
        # Check relationship disclosure completeness
        identified_party_names = {rp["name"] for rp in identified_relationships}
        disclosed_party_names = {rp["name"] for rp in disclosed_relationships}

        undisclosed_relationships = identified_party_names - disclosed_party_names
        improperly_disclosed = disclosed_party_names - identified_party_names

        # Check transaction disclosure completeness
        identified_tx_ids = {tx.get("id") or tx.get("description") for tx in identified_transactions}
        disclosed_tx_ids = {tx.get("id") or tx.get("description") for tx in disclosed_transactions}

        undisclosed_transactions = identified_tx_ids - disclosed_tx_ids

        # Calculate materiality of undisclosed items
        undisclosed_amount = sum(
            Decimal(str(tx.get("amount", 0)))
            for tx in identified_transactions
            if (tx.get("id") or tx.get("description")) in undisclosed_transactions
        )

        # Assess completeness
        if not undisclosed_relationships and not undisclosed_transactions:
            completeness_rating = "COMPLETE"
            conclusion = "All identified related parties and transactions are properly disclosed"
        elif len(undisclosed_relationships) <= 1 and undisclosed_amount < 10000:
            completeness_rating = "SUBSTANTIALLY_COMPLETE"
            conclusion = "Minor disclosure omissions identified. Propose adjustments"
        else:
            completeness_rating = "INCOMPLETE"
            conclusion = "Material related party relationships or transactions not disclosed. Required disclosure adjustment"

        return {
            "completeness_rating": completeness_rating,
            "identified_relationships": len(identified_relationships),
            "disclosed_relationships": len(disclosed_relationships),
            "undisclosed_relationships": list(undisclosed_relationships) if undisclosed_relationships else [],
            "undisclosed_relationship_count": len(undisclosed_relationships),
            "identified_transactions": len(identified_transactions),
            "disclosed_transactions": len(disclosed_transactions),
            "undisclosed_transactions": list(undisclosed_transactions) if undisclosed_transactions else [],
            "undisclosed_transaction_count": len(undisclosed_transactions),
            "undisclosed_amount": float(undisclosed_amount),
            "improperly_disclosed_parties": list(improperly_disclosed) if improperly_disclosed else [],
            "audit_conclusion": conclusion,
            "adjustment_required": completeness_rating == "INCOMPLETE",
        }

    # Private helper methods

    def _check_potential_undisclosed_party(self, entity: Dict) -> bool:
        """Check if entity might be undisclosed related party"""
        red_flags = 0

        # Unusually favorable terms
        if entity.get("favorable_terms", False):
            red_flags += 1

        # High concentration (>10% of revenues or expenses)
        if entity.get("concentration_percent", 0) > 10:
            red_flags += 1

        # Unusual transaction patterns
        if entity.get("unusual_transactions", False):
            red_flags += 1

        # Common address or phone number
        if entity.get("shared_address", False):
            red_flags += 1

        return red_flags >= 2

    def _evaluate_transaction_terms(
        self,
        transaction_terms: Dict,
        market_terms: Dict,
        transaction_type: TransactionType,
    ) -> Dict:
        """Evaluate if transaction terms are off-market"""
        # Simplified evaluation - real implementation would be more sophisticated
        off_market = False
        description = "Terms appear consistent with market"

        if "interest_rate" in transaction_terms:
            rp_rate = Decimal(str(transaction_terms["interest_rate"]))
            market_rate = Decimal(str(market_terms.get("interest_rate", rp_rate)))
            if abs(rp_rate - market_rate) / market_rate > Decimal("0.20"):  # >20% variance
                off_market = True
                description = f"Interest rate {rp_rate}% vs market {market_rate}%"

        return {
            "off_market": off_market,
            "description": description,
        }

    def _count_disclosure_required(self, related_parties: Dict) -> int:
        """Count relationships requiring disclosure"""
        count = 0
        for category in ["parent_companies", "subsidiaries", "affiliates", "principal_owners"]:
            count += len(related_parties.get(category, []))
        return count
