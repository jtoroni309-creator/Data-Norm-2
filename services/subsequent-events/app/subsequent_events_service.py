"""
Subsequent Events Review Service

Implements AICPA AU-C 560: Subsequent Events and Subsequently Discovered Facts

Period Coverage:
- Type I Events (Recognized): Events that provide evidence about conditions
  that existed at balance sheet date
- Type II Events (Disclosed): Events that provide evidence about conditions
  that arose after balance sheet date

Review Period: From balance sheet date through audit report date (and beyond for subsequently discovered facts)
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Classification of subsequent events"""
    TYPE_I_RECOGNIZED = "type_i_recognized"  # Adjust FS - condition existed at BS date
    TYPE_II_DISCLOSED = "type_ii_disclosed"  # Disclose only - condition arose after BS date
    NOT_SIGNIFICANT = "not_significant"  # No action required


class EventCategory(str, Enum):
    """Categories of subsequent events"""
    DEBT_ISSUANCE = "debt_issuance"
    DEBT_REFINANCING = "debt_refinancing"
    BUSINESS_COMBINATION = "business_combination"
    ASSET_SALE = "asset_sale"
    LITIGATION_SETTLEMENT = "litigation_settlement"
    LOSS_FROM_CASUALTY = "loss_from_casualty"
    BANKRUPTCY = "bankruptcy"
    INVENTORY_LOSS = "inventory_loss"
    RECEIVABLE_WRITE_OFF = "receivable_write_off"
    STOCK_ISSUANCE = "stock_issuance"
    DIVIDEND_DECLARATION = "dividend_declaration"
    GOING_CONCERN_DOUBT = "going_concern_doubt"
    MANAGEMENT_CHANGE = "management_change"
    OTHER = "other"


class SubsequentEventsService:
    """Service for subsequent events review per AU-C 560"""

    def evaluate_event(
        self,
        event_description: str,
        event_date: datetime,
        balance_sheet_date: datetime,
        event_category: EventCategory,
        amount: Optional[Decimal] = None,
        conditions_existed_at_bs_date: bool = False,
        is_material: bool = False,
    ) -> Dict:
        """
        Evaluate and classify a subsequent event.

        Args:
            event_description: Description of event
            event_date: When event occurred
            balance_sheet_date: Financial statement date
            event_category: Category of event
            amount: Dollar amount if quantifiable
            conditions_existed_at_bs_date: Did conditions exist at BS date?
            is_material: Is event material to FS?

        Returns:
            Event classification and required action
        """
        # Ensure event is after balance sheet date
        if event_date < balance_sheet_date:
            return {
                "error": "Event date is before balance sheet date",
                "classification": "NOT_APPLICABLE",
            }

        # Determine event type
        if conditions_existed_at_bs_date:
            event_type = EventType.TYPE_I_RECOGNIZED
            required_action = "Adjust financial statements"
            disclosure_required = True
        elif is_material:
            event_type = EventType.TYPE_II_DISCLOSED
            required_action = "Disclose in notes to financial statements"
            disclosure_required = True
        else:
            event_type = EventType.NOT_SIGNIFICANT
            required_action = "No action required"
            disclosure_required = False

        # Specific guidance by category
        category_guidance = self._get_category_guidance(event_category, event_type)

        days_after_bs = (event_date - balance_sheet_date).days

        return {
            "event_description": event_description,
            "event_date": event_date.isoformat(),
            "balance_sheet_date": balance_sheet_date.isoformat(),
            "days_after_bs_date": days_after_bs,
            "event_category": event_category.value,
            "event_type": event_type.value,
            "amount": float(amount) if amount else None,
            "is_material": is_material,
            "conditions_existed_at_bs_date": conditions_existed_at_bs_date,
            "required_action": required_action,
            "disclosure_required": disclosure_required,
            "category_specific_guidance": category_guidance,
        }

    def generate_procedures_checklist(
        self,
        balance_sheet_date: datetime,
        expected_report_date: datetime,
    ) -> Dict:
        """
        Generate subsequent events review procedures checklist.

        AU-C 560.07 requires specific procedures for subsequent events review.

        Args:
            balance_sheet_date: Financial statement date
            expected_report_date: Expected audit report date

        Returns:
            Procedures checklist with dates
        """
        review_period_days = (expected_report_date - balance_sheet_date).days

        procedures = [
            {
                "procedure": "Read minutes of meetings of stockholders, board of directors, and audit committee held after BS date",
                "required": True,
                "timing": "Through report date",
            },
            {
                "procedure": "Inquire of management about significant transactions, changes in capital stock, debt, or working capital",
                "required": True,
                "timing": "At/near completion of fieldwork",
            },
            {
                "procedure": "Read latest available interim financial statements and compare to FS being reported on",
                "required": True,
                "timing": "Most recent available",
            },
            {
                "procedure": "Inquire about unusual adjustments made after BS date",
                "required": True,
                "timing": "Through report date",
            },
            {
                "procedure": "Inquire about litigation, claims, and assessments",
                "required": True,
                "timing": "Through report date",
            },
            {
                "procedure": "Inquire about events that raise substantial doubt about going concern",
                "required": True,
                "timing": "Through report date",
            },
            {
                "procedure": "Obtain management representation letter dated as of report date",
                "required": True,
                "timing": "Date of auditor's report",
            },
        ]

        return {
            "balance_sheet_date": balance_sheet_date.isoformat(),
            "expected_report_date": expected_report_date.isoformat(),
            "review_period_days": review_period_days,
            "procedures": procedures,
            "total_procedures": len(procedures),
        }

    def _get_category_guidance(self, category: EventCategory, event_type: EventType) -> str:
        """Get specific guidance for event category"""
        guidance_map = {
            (EventCategory.LITIGATION_SETTLEMENT, EventType.TYPE_I_RECOGNIZED):
                "Adjust accrued litigation liability. Condition (lawsuit) existed at BS date.",
            (EventCategory.LITIGATION_SETTLEMENT, EventType.TYPE_II_DISCLOSED):
                "Disclose settlement. Litigation filed after BS date.",
            (EventCategory.RECEIVABLE_WRITE_OFF, EventType.TYPE_I_RECOGNIZED):
                "Adjust allowance for doubtful accounts. Customer's inability to pay existed at BS date.",
            (EventCategory.INVENTORY_LOSS, EventType.TYPE_I_RECOGNIZED):
                "Adjust inventory valuation. Obsolescence existed at BS date.",
            (EventCategory.BUSINESS_COMBINATION, EventType.TYPE_II_DISCLOSED):
                "Disclose business combination including terms, date, and impact.",
            (EventCategory.DEBT_ISSUANCE, EventType.TYPE_II_DISCLOSED):
                "Disclose debt issuance including amount, terms, and purpose.",
            (EventCategory.BANKRUPTCY, EventType.TYPE_II_DISCLOSED):
                "Disclose bankruptcy filing and potential impact. May raise going concern doubt.",
            (EventCategory.GOING_CONCERN_DOUBT, EventType.TYPE_II_DISCLOSED):
                "Disclose conditions raising substantial doubt. May require going concern emphasis paragraph.",
        }

        return guidance_map.get((category, event_type), "Apply professional judgment for disclosure requirements.")
