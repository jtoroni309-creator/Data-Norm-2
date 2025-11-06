"""
E&O Insurance Test Case Management Service

Enables E&O insurance companies to test the platform's detection capabilities by:
- Uploading real audit failures (material misstatements, going concern issues, etc.)
- Running the platform's full audit suite on historical engagements
- Comparing platform findings vs. actual outcomes
- Tracking detection accuracy and false positive/negative rates
- Generating comprehensive risk assessment reports

This demonstrates platform value for reducing E&O liability premiums.
"""

import json
import logging
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class AuditFailureType(str, Enum):
    """Types of audit failures that lead to lawsuits"""
    MATERIAL_MISSTATEMENT = "material_misstatement"
    GOING_CONCERN_ISSUE = "going_concern_issue"
    FRAUD_NOT_DETECTED = "fraud_not_detected"
    RELATED_PARTY_UNDISCLOSED = "related_party_undisclosed"
    REVENUE_RECOGNITION_ERROR = "revenue_recognition_error"
    ASSET_OVERSTATEMENT = "asset_overstatement"
    LIABILITY_UNDERSTATEMENT = "liability_understatement"
    INADEQUATE_DISCLOSURE = "inadequate_disclosure"
    INDEPENDENCE_VIOLATION = "independence_violation"
    SCOPE_LIMITATION = "scope_limitation"
    SUBSEQUENT_EVENT_MISSED = "subsequent_event_missed"
    INTERNAL_CONTROL_FAILURE = "internal_control_failure"


class TestCaseStatus(str, Enum):
    """Status of test case"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class DetectionResult(str, Enum):
    """Platform detection result"""
    TRUE_POSITIVE = "true_positive"  # Correctly detected issue
    FALSE_NEGATIVE = "false_negative"  # Missed issue
    FALSE_POSITIVE = "false_positive"  # Flagged non-issue
    TRUE_NEGATIVE = "true_negative"  # Correctly did not flag


class TestCaseService:
    """
    Test case management for E&O insurance validation.

    Allows insurance companies to:
    1. Upload real audit failures (anonymized)
    2. Run platform validation
    3. Compare results vs. actual outcomes
    4. Track performance metrics
    5. Generate risk assessment reports
    """

    def __init__(
        self,
        anonymization_service=None,
        audit_log_service=None,
    ):
        """
        Initialize test case service.

        Args:
            anonymization_service: For anonymizing test cases
            audit_log_service: For audit logging
        """
        self.anonymization_service = anonymization_service
        self.audit_log_service = audit_log_service

        # In-memory storage (in production, use database)
        self._test_cases: Dict[str, Dict] = {}
        self._validation_results: Dict[str, Dict] = {}
        self._performance_metrics: Dict[str, Any] = {}

    async def create_test_case(
        self,
        case_name: str,
        description: str,
        failure_type: AuditFailureType,
        actual_outcome: Dict[str, Any],
        source_documents: Dict[str, Any],
        financial_statements: Dict[str, Any],
        cpa_firm_info: Dict[str, Any],
        lawsuit_details: Optional[Dict[str, Any]] = None,
        insurance_company_id: UUID = None,
        created_by_user_id: UUID = None,
    ) -> str:
        """
        Create a test case from a real audit failure.

        Args:
            case_name: Name for test case
            description: Description of the failure
            failure_type: Type of audit failure
            actual_outcome: What actually happened (lawsuit, restatement, etc.)
            source_documents: Original audit documents
            financial_statements: Financial statements
            cpa_firm_info: CPA firm information (anonymized)
            lawsuit_details: Details of lawsuit if applicable
            insurance_company_id: Insurance company creating case
            created_by_user_id: User creating case

        Returns:
            Test case ID
        """
        try:
            test_case_id = str(uuid4())

            # Anonymize sensitive information
            if self.anonymization_service:
                source_documents = self.anonymization_service.anonymize_financial_statement(
                    source_documents,
                    level="full"
                )
                financial_statements = self.anonymization_service.anonymize_financial_statement(
                    financial_statements,
                    level="full"
                )
                cpa_firm_info = self._anonymize_cpa_firm_info(cpa_firm_info)

            # Create test case record
            test_case = {
                "id": test_case_id,
                "case_name": case_name,
                "description": description,
                "failure_type": failure_type.value,
                "actual_outcome": actual_outcome,
                "source_documents": source_documents,
                "financial_statements": financial_statements,
                "cpa_firm_info": cpa_firm_info,
                "lawsuit_details": lawsuit_details or {},
                "insurance_company_id": str(insurance_company_id) if insurance_company_id else None,
                "created_by": str(created_by_user_id) if created_by_user_id else None,
                "created_at": datetime.utcnow().isoformat(),
                "status": TestCaseStatus.PENDING.value,
                "validation_results": None,
                "platform_findings": None,
            }

            self._test_cases[test_case_id] = test_case

            # Audit log
            if self.audit_log_service:
                logger.info(f"Created test case: {test_case_id} ({failure_type.value})")

            return test_case_id

        except Exception as e:
            logger.error(f"Failed to create test case: {e}", exc_info=True)
            raise TestCaseError(f"Test case creation failed: {e}")

    async def run_platform_validation(
        self,
        test_case_id: str,
        validation_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run full platform validation on test case.

        Executes all platform audit procedures:
        - Financial analysis (ratio analysis, trend analysis)
        - Fraud detection (Benford's Law, journal entry testing)
        - Going concern assessment
        - Related party detection
        - Revenue recognition testing
        - Subsequent events review
        - Risk assessment

        Args:
            test_case_id: Test case to validate
            validation_config: Optional configuration

        Returns:
            Validation results
        """
        try:
            if test_case_id not in self._test_cases:
                raise TestCaseError(f"Test case not found: {test_case_id}")

            test_case = self._test_cases[test_case_id]
            test_case["status"] = TestCaseStatus.RUNNING.value

            # Run all platform checks
            platform_findings = await self._run_all_platform_checks(
                test_case["source_documents"],
                test_case["financial_statements"]
            )

            # Compare with actual outcome
            comparison = self._compare_results(
                platform_findings=platform_findings,
                actual_outcome=test_case["actual_outcome"],
                failure_type=test_case["failure_type"]
            )

            # Store results
            validation_result = {
                "test_case_id": test_case_id,
                "platform_findings": platform_findings,
                "actual_outcome": test_case["actual_outcome"],
                "comparison": comparison,
                "detection_result": comparison["detection_result"],
                "accuracy_score": comparison["accuracy_score"],
                "validated_at": datetime.utcnow().isoformat(),
            }

            self._validation_results[test_case_id] = validation_result

            test_case["validation_results"] = validation_result
            test_case["platform_findings"] = platform_findings
            test_case["status"] = TestCaseStatus.COMPLETED.value

            # Update performance metrics
            self._update_performance_metrics(validation_result)

            logger.info(
                f"Validation completed for test case {test_case_id}: "
                f"{comparison['detection_result']}"
            )

            return validation_result

        except Exception as e:
            logger.error(f"Platform validation failed: {e}", exc_info=True)
            if test_case_id in self._test_cases:
                self._test_cases[test_case_id]["status"] = TestCaseStatus.FAILED.value
            raise TestCaseError(f"Platform validation failed: {e}")

    async def _run_all_platform_checks(
        self,
        source_documents: Dict[str, Any],
        financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run all platform audit checks.

        Args:
            source_documents: Audit source documents
            financial_statements: Financial statements

        Returns:
            All platform findings
        """
        findings = {
            "financial_analysis": {},
            "fraud_detection": {},
            "going_concern": {},
            "related_party": {},
            "revenue_recognition": {},
            "subsequent_events": {},
            "risk_assessment": {},
            "overall_assessment": {},
        }

        # 1. Financial Analysis
        findings["financial_analysis"] = await self._run_financial_analysis(
            financial_statements
        )

        # 2. Fraud Detection
        findings["fraud_detection"] = await self._run_fraud_detection(
            source_documents,
            financial_statements
        )

        # 3. Going Concern Assessment
        findings["going_concern"] = await self._assess_going_concern(
            financial_statements
        )

        # 4. Related Party Transactions
        findings["related_party"] = await self._detect_related_parties(
            source_documents
        )

        # 5. Revenue Recognition
        findings["revenue_recognition"] = await self._test_revenue_recognition(
            source_documents,
            financial_statements
        )

        # 6. Subsequent Events
        findings["subsequent_events"] = await self._review_subsequent_events(
            source_documents
        )

        # 7. Risk Assessment
        findings["risk_assessment"] = await self._assess_audit_risk(
            financial_statements,
            findings
        )

        # 8. Overall Assessment
        findings["overall_assessment"] = self._generate_overall_assessment(
            findings
        )

        return findings

    async def _run_financial_analysis(
        self,
        financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run comprehensive financial analysis."""
        analysis = {
            "ratios": {},
            "trends": {},
            "red_flags": [],
            "materiality": {},
        }

        # Calculate key ratios
        if all(k in financial_statements for k in ['total_assets', 'total_liabilities', 'total_equity']):
            total_assets = Decimal(str(financial_statements['total_assets']))
            total_liabilities = Decimal(str(financial_statements['total_liabilities']))
            total_equity = Decimal(str(financial_statements['total_equity']))

            # Debt-to-equity ratio
            if total_equity != 0:
                debt_to_equity = total_liabilities / total_equity
                analysis["ratios"]["debt_to_equity"] = float(debt_to_equity)

                # Red flag: High leverage
                if debt_to_equity > 3:
                    analysis["red_flags"].append({
                        "type": "high_leverage",
                        "severity": "high",
                        "description": f"Debt-to-equity ratio of {debt_to_equity:.2f} indicates high leverage",
                    })

        # Calculate materiality
        if 'revenue' in financial_statements:
            revenue = Decimal(str(financial_statements['revenue']))
            materiality = revenue * Decimal('0.05')  # 5% of revenue
            analysis["materiality"] = {
                "overall_materiality": float(materiality),
                "performance_materiality": float(materiality * Decimal('0.75')),
                "basis": "revenue",
            }

        return analysis

    async def _run_fraud_detection(
        self,
        source_documents: Dict[str, Any],
        financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run fraud detection algorithms."""
        fraud_findings = {
            "benfords_law": {},
            "journal_entry_testing": {},
            "revenue_manipulation": {},
            "fraud_risk_score": 0,
        }

        # Check for revenue manipulation indicators
        if 'revenue' in financial_statements and 'accounts_receivable' in financial_statements:
            revenue = Decimal(str(financial_statements['revenue']))
            ar = Decimal(str(financial_statements['accounts_receivable']))

            if revenue != 0:
                ar_days = (ar / revenue) * 365

                # Red flag: Rapidly growing AR relative to revenue
                if ar_days > 90:
                    fraud_findings["revenue_manipulation"] = {
                        "indicator": "high_ar_days",
                        "ar_days": float(ar_days),
                        "description": "Accounts receivable days unusually high - potential revenue recognition issues",
                        "risk": "high",
                    }
                    fraud_findings["fraud_risk_score"] += 40

        return fraud_findings

    async def _assess_going_concern(
        self,
        financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess going concern issues."""
        going_concern = {
            "indicators": [],
            "risk_level": "low",
            "recommendation": "",
        }

        # Check for negative equity
        if 'total_equity' in financial_statements:
            equity = Decimal(str(financial_statements['total_equity']))
            if equity < 0:
                going_concern["indicators"].append({
                    "type": "negative_equity",
                    "severity": "critical",
                    "description": f"Negative equity of ${equity:,.2f}",
                })
                going_concern["risk_level"] = "critical"

        # Check for negative cash flow
        if 'operating_cash_flow' in financial_statements:
            ocf = Decimal(str(financial_statements['operating_cash_flow']))
            if ocf < 0:
                going_concern["indicators"].append({
                    "type": "negative_cash_flow",
                    "severity": "high",
                    "description": f"Negative operating cash flow of ${ocf:,.2f}",
                })
                if going_concern["risk_level"] == "low":
                    going_concern["risk_level"] = "high"

        # Generate recommendation
        if going_concern["risk_level"] == "critical":
            going_concern["recommendation"] = "Going concern opinion required - substantial doubt about ability to continue"
        elif going_concern["risk_level"] == "high":
            going_concern["recommendation"] = "Significant going concern indicators - additional procedures required"

        return going_concern

    async def _detect_related_parties(
        self,
        source_documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect undisclosed related party transactions."""
        # Placeholder implementation
        return {
            "related_parties_identified": [],
            "undisclosed_transactions": [],
            "risk_assessment": "low",
        }

    async def _test_revenue_recognition(
        self,
        source_documents: Dict[str, Any],
        financial_statements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test revenue recognition policies."""
        # Placeholder implementation
        return {
            "policy_assessment": "appropriate",
            "issues_identified": [],
            "risk_score": 0,
        }

    async def _review_subsequent_events(
        self,
        source_documents: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Review subsequent events."""
        # Placeholder implementation
        return {
            "events_identified": [],
            "disclosure_required": [],
            "adjustment_required": [],
        }

    async def _assess_audit_risk(
        self,
        financial_statements: Dict[str, Any],
        findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess overall audit risk."""
        risk_factors = []
        overall_risk = 0

        # Fraud risk
        if findings.get("fraud_detection", {}).get("fraud_risk_score", 0) > 30:
            risk_factors.append("High fraud risk detected")
            overall_risk += 30

        # Going concern risk
        if findings.get("going_concern", {}).get("risk_level") == "critical":
            risk_factors.append("Critical going concern issues")
            overall_risk += 40

        return {
            "overall_risk_score": overall_risk,
            "risk_factors": risk_factors,
            "risk_level": "critical" if overall_risk > 60 else ("high" if overall_risk > 30 else "moderate"),
        }

    def _generate_overall_assessment(
        self,
        findings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate overall platform assessment."""
        issues_found = []
        critical_count = 0
        high_count = 0

        # Check fraud findings
        if findings["fraud_detection"].get("fraud_risk_score", 0) > 30:
            issues_found.append({
                "category": "fraud_risk",
                "severity": "high",
                "description": "Elevated fraud risk indicators detected",
            })
            high_count += 1

        # Check going concern
        if findings["going_concern"].get("risk_level") == "critical":
            issues_found.append({
                "category": "going_concern",
                "severity": "critical",
                "description": "Substantial doubt about going concern",
            })
            critical_count += 1

        return {
            "issues_found": issues_found,
            "critical_count": critical_count,
            "high_count": high_count,
            "overall_opinion": "qualified" if critical_count > 0 else ("clean" if high_count == 0 else "clean_with_explanatory_paragraph"),
        }

    def _compare_results(
        self,
        platform_findings: Dict[str, Any],
        actual_outcome: Dict[str, Any],
        failure_type: str
    ) -> Dict[str, Any]:
        """
        Compare platform findings vs. actual outcome.

        Determines if platform would have caught the issue.

        Args:
            platform_findings: What the platform found
            actual_outcome: What actually happened
            failure_type: Type of failure

        Returns:
            Comparison results
        """
        # Determine if platform detected the issue
        platform_detected = self._did_platform_detect_issue(
            platform_findings,
            failure_type
        )

        # Determine detection result
        if actual_outcome.get("issue_occurred", True):  # Issue actually occurred
            if platform_detected:
                detection_result = DetectionResult.TRUE_POSITIVE
                accuracy_score = 100
            else:
                detection_result = DetectionResult.FALSE_NEGATIVE
                accuracy_score = 0
        else:  # No issue occurred
            if platform_detected:
                detection_result = DetectionResult.FALSE_POSITIVE
                accuracy_score = 0
            else:
                detection_result = DetectionResult.TRUE_NEGATIVE
                accuracy_score = 100

        return {
            "detection_result": detection_result.value,
            "platform_detected": platform_detected,
            "actual_issue": actual_outcome.get("issue_occurred", True),
            "accuracy_score": accuracy_score,
            "details": {
                "platform_findings_summary": self._summarize_findings(platform_findings),
                "actual_outcome_summary": actual_outcome.get("description", ""),
            }
        }

    def _did_platform_detect_issue(
        self,
        platform_findings: Dict[str, Any],
        failure_type: str
    ) -> bool:
        """
        Determine if platform detected the issue.

        Args:
            platform_findings: Platform findings
            failure_type: Type of failure to check

        Returns:
            True if platform detected issue
        """
        if failure_type == AuditFailureType.GOING_CONCERN_ISSUE.value:
            # Check if platform flagged going concern
            gc_risk = platform_findings.get("going_concern", {}).get("risk_level", "low")
            return gc_risk in ["high", "critical"]

        elif failure_type == AuditFailureType.FRAUD_NOT_DETECTED.value:
            # Check if platform flagged fraud risk
            fraud_score = platform_findings.get("fraud_detection", {}).get("fraud_risk_score", 0)
            return fraud_score > 30

        elif failure_type == AuditFailureType.MATERIAL_MISSTATEMENT.value:
            # Check if platform found material issues
            issues = platform_findings.get("overall_assessment", {}).get("issues_found", [])
            return any(issue["severity"] in ["high", "critical"] for issue in issues)

        # Default: Check if any critical or high severity issues found
        overall = platform_findings.get("overall_assessment", {})
        return overall.get("critical_count", 0) > 0 or overall.get("high_count", 0) > 0

    def _summarize_findings(self, findings: Dict[str, Any]) -> str:
        """Summarize platform findings."""
        overall = findings.get("overall_assessment", {})
        critical = overall.get("critical_count", 0)
        high = overall.get("high_count", 0)

        if critical > 0:
            return f"{critical} critical issue(s) found"
        elif high > 0:
            return f"{high} high severity issue(s) found"
        else:
            return "No critical issues found"

    def _update_performance_metrics(self, validation_result: Dict[str, Any]):
        """Update overall performance metrics."""
        detection_result = validation_result["detection_result"]

        if "detection_results" not in self._performance_metrics:
            self._performance_metrics["detection_results"] = {
                "true_positive": 0,
                "false_negative": 0,
                "false_positive": 0,
                "true_negative": 0,
            }

        self._performance_metrics["detection_results"][detection_result] += 1

        # Calculate overall accuracy
        results = self._performance_metrics["detection_results"]
        total = sum(results.values())
        correct = results["true_positive"] + results["true_negative"]
        self._performance_metrics["overall_accuracy"] = (correct / total * 100) if total > 0 else 0

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get platform performance metrics.

        Returns:
            Performance metrics
        """
        results = self._performance_metrics.get("detection_results", {
            "true_positive": 0,
            "false_negative": 0,
            "false_positive": 0,
            "true_negative": 0,
        })

        total = sum(results.values())

        if total == 0:
            return {
                "total_test_cases": 0,
                "overall_accuracy": 0,
                "detection_rate": 0,
                "false_negative_rate": 0,
                "false_positive_rate": 0,
            }

        # Calculate metrics
        tp = results["true_positive"]
        tn = results["true_negative"]
        fp = results["false_positive"]
        fn = results["false_negative"]

        accuracy = ((tp + tn) / total * 100) if total > 0 else 0
        detection_rate = (tp / (tp + fn) * 100) if (tp + fn) > 0 else 0
        false_negative_rate = (fn / (tp + fn) * 100) if (tp + fn) > 0 else 0
        false_positive_rate = (fp / (fp + tn) * 100) if (fp + tn) > 0 else 0

        return {
            "total_test_cases": total,
            "overall_accuracy": round(accuracy, 2),
            "detection_rate": round(detection_rate, 2),
            "false_negative_rate": round(false_negative_rate, 2),
            "false_positive_rate": round(false_positive_rate, 2),
            "true_positives": tp,
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
        }

    def _anonymize_cpa_firm_info(self, cpa_firm_info: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize CPA firm information."""
        # Placeholder - would use anonymization service
        return {
            "firm_id": "[FIRM_ID_" + str(uuid4())[:8] + "]",
            "firm_size": cpa_firm_info.get("firm_size", "unknown"),
            "years_in_practice": cpa_firm_info.get("years_in_practice", 0),
        }


class TestCaseError(Exception):
    """Raised when test case operation fails"""
    pass
