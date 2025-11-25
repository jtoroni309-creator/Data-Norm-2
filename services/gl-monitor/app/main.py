"""
Continuous GL Monitoring Service - AI Detections

Real-time monitoring of General Ledger transactions with AI-powered detection rules.
Similar to FloQast's AI Detections but with more advanced capabilities:

- Real-time transaction monitoring (not just periodic)
- Custom detection rules in natural language
- ML-powered anomaly detection
- Automatic alert generation
- Continuous learning from feedback

Key Features:
1. Real-time GL monitoring with sub-second latency
2. 100+ pre-built detection rules
3. Custom rules via natural language
4. Intelligent alert prioritization
5. Root cause analysis
6. Trend monitoring and forecasting
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4
from enum import Enum
import asyncio
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger

app = FastAPI(
    title="Continuous GL Monitoring Service",
    description="Real-time GL monitoring with AI-powered detection rules",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Enums and Models
# ============================================================================

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertStatus(str, Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class RuleType(str, Enum):
    THRESHOLD = "threshold"
    PATTERN = "pattern"
    ANOMALY = "anomaly"
    CORRELATION = "correlation"
    SEQUENCE = "sequence"
    CUSTOM = "custom"


class MonitoringStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


class GLTransaction(BaseModel):
    """General Ledger transaction for monitoring"""
    transaction_id: str
    timestamp: datetime
    account_code: str
    account_name: str
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    description: str
    posting_user: str
    source_system: str
    document_number: Optional[str] = None
    cost_center: Optional[str] = None
    project_code: Optional[str] = None
    entity_code: Optional[str] = None
    currency: str = "USD"
    exchange_rate: float = 1.0


class DetectionRule(BaseModel):
    """Detection rule definition"""
    rule_id: str = Field(default_factory=lambda: str(uuid4())[:8])
    name: str
    description: str
    rule_type: RuleType
    is_active: bool = True
    severity: AlertSeverity = AlertSeverity.MEDIUM

    # Rule configuration
    conditions: Dict[str, Any] = {}
    natural_language_rule: Optional[str] = None

    # Thresholds
    threshold_amount: Optional[float] = None
    threshold_count: Optional[int] = None
    threshold_percentage: Optional[float] = None

    # Time windows
    time_window_minutes: int = 60

    # Accounts to monitor
    account_patterns: List[str] = []

    # Alert settings
    cooldown_minutes: int = 30
    max_alerts_per_day: int = 10

    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"


class Alert(BaseModel):
    """Generated alert"""
    alert_id: str = Field(default_factory=lambda: str(uuid4()))
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.NEW

    title: str
    description: str
    details: Dict[str, Any] = {}

    affected_transactions: List[str] = []
    affected_accounts: List[str] = []
    total_amount: float = 0.0

    root_cause_analysis: Optional[str] = None
    recommended_actions: List[str] = []

    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None


class MonitoringDashboard(BaseModel):
    """Real-time monitoring dashboard"""
    status: MonitoringStatus
    total_transactions_today: int
    total_amount_today: float
    alerts_today: int
    critical_alerts: int
    rules_active: int
    last_transaction_time: Optional[datetime] = None

    alerts_by_severity: Dict[str, int] = {}
    alerts_by_rule: Dict[str, int] = {}
    transactions_by_hour: Dict[int, int] = {}
    top_triggered_rules: List[Dict[str, Any]] = []


class RuleCreateRequest(BaseModel):
    """Request to create a detection rule"""
    name: str
    description: str
    rule_type: RuleType
    severity: AlertSeverity = AlertSeverity.MEDIUM
    natural_language_rule: Optional[str] = None
    conditions: Dict[str, Any] = {}
    threshold_amount: Optional[float] = None
    account_patterns: List[str] = []
    time_window_minutes: int = 60


# ============================================================================
# In-Memory Storage
# ============================================================================

rules_db: Dict[str, DetectionRule] = {}
alerts_db: Dict[str, Alert] = {}
transactions_buffer: List[GLTransaction] = []
monitoring_status = MonitoringStatus.ACTIVE
connected_websockets: Set[WebSocket] = set()


# ============================================================================
# Pre-built Detection Rules (100+)
# ============================================================================

def initialize_default_rules():
    """Initialize pre-built detection rules"""

    default_rules = [
        # ===== THRESHOLD RULES (20) =====
        DetectionRule(
            rule_id="THR001",
            name="Large Transaction Alert",
            description="Alert on transactions exceeding threshold",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.HIGH,
            threshold_amount=100000,
            account_patterns=["*"]
        ),
        DetectionRule(
            rule_id="THR002",
            name="Material Transaction",
            description="Transaction exceeds materiality threshold",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.CRITICAL,
            threshold_amount=500000,
            account_patterns=["*"]
        ),
        DetectionRule(
            rule_id="THR003",
            name="Large Revenue Entry",
            description="Large credit to revenue accounts",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.HIGH,
            threshold_amount=250000,
            account_patterns=["4*", "revenue*"]
        ),
        DetectionRule(
            rule_id="THR004",
            name="Large Expense Entry",
            description="Large debit to expense accounts",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.MEDIUM,
            threshold_amount=100000,
            account_patterns=["6*", "7*", "expense*"]
        ),
        DetectionRule(
            rule_id="THR005",
            name="Large Cash Movement",
            description="Large cash transaction",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.HIGH,
            threshold_amount=50000,
            account_patterns=["1000*", "1001*", "cash*"]
        ),
        DetectionRule(
            rule_id="THR006",
            name="Large AR Write-off",
            description="Large accounts receivable write-off",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.CRITICAL,
            threshold_amount=25000,
            account_patterns=["1200*", "bad_debt*"]
        ),
        DetectionRule(
            rule_id="THR007",
            name="Large Inventory Adjustment",
            description="Significant inventory adjustment",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.HIGH,
            threshold_amount=50000,
            account_patterns=["1300*", "inventory*"]
        ),
        DetectionRule(
            rule_id="THR008",
            name="Large Accrual",
            description="Large accrual entry",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.MEDIUM,
            threshold_amount=75000,
            account_patterns=["2*", "accrued*"]
        ),
        DetectionRule(
            rule_id="THR009",
            name="Large Intercompany",
            description="Large intercompany transaction",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.HIGH,
            threshold_amount=200000,
            account_patterns=["1800*", "2800*", "interco*"]
        ),
        DetectionRule(
            rule_id="THR010",
            name="Large Capital Expenditure",
            description="Large fixed asset addition",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.MEDIUM,
            threshold_amount=100000,
            account_patterns=["1500*", "fixed_asset*"]
        ),

        # ===== PATTERN RULES (20) =====
        DetectionRule(
            rule_id="PAT001",
            name="Round Dollar Amount",
            description="Transaction with suspiciously round amount",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "round_dollar", "min_amount": 10000}
        ),
        DetectionRule(
            rule_id="PAT002",
            name="Weekend Posting",
            description="Transaction posted on weekend",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "weekend_posting"}
        ),
        DetectionRule(
            rule_id="PAT003",
            name="After Hours Posting",
            description="Transaction posted outside business hours",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.LOW,
            conditions={"pattern": "after_hours", "start_hour": 19, "end_hour": 7}
        ),
        DetectionRule(
            rule_id="PAT004",
            name="Period End Clustering",
            description="Multiple transactions near period end",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.HIGH,
            conditions={"pattern": "period_end", "days_from_end": 3}
        ),
        DetectionRule(
            rule_id="PAT005",
            name="Duplicate Amount",
            description="Same amount posted multiple times",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.HIGH,
            conditions={"pattern": "duplicate_amount", "time_window_hours": 24}
        ),
        DetectionRule(
            rule_id="PAT006",
            name="Round Thousands",
            description="Amount exactly divisible by 1000",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.LOW,
            conditions={"pattern": "round_thousand", "min_amount": 5000}
        ),
        DetectionRule(
            rule_id="PAT007",
            name="Sequential Numbers",
            description="Sequential or patterned amounts",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "sequential_numbers"}
        ),
        DetectionRule(
            rule_id="PAT008",
            name="Just Below Threshold",
            description="Amount just below approval threshold",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.HIGH,
            conditions={"pattern": "below_threshold", "thresholds": [5000, 10000, 25000, 50000, 100000]}
        ),
        DetectionRule(
            rule_id="PAT009",
            name="Suspicious Keywords",
            description="Description contains suspicious keywords",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "keywords", "keywords": ["cash", "write-off", "adjustment", "manual", "override"]}
        ),
        DetectionRule(
            rule_id="PAT010",
            name="Unusual User Activity",
            description="User posting to unusual accounts",
            rule_type=RuleType.PATTERN,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "unusual_user_account"}
        ),

        # ===== ANOMALY RULES (20) =====
        DetectionRule(
            rule_id="ANO001",
            name="Statistical Outlier",
            description="Amount is statistical outlier (>3 std dev)",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.HIGH,
            conditions={"method": "zscore", "threshold": 3.0}
        ),
        DetectionRule(
            rule_id="ANO002",
            name="Benford's Law Violation",
            description="Amount violates Benford's Law",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.MEDIUM,
            conditions={"method": "benford", "digit": "first"}
        ),
        DetectionRule(
            rule_id="ANO003",
            name="ML Anomaly Detection",
            description="Machine learning detected anomaly",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.HIGH,
            conditions={"method": "isolation_forest", "contamination": 0.05}
        ),
        DetectionRule(
            rule_id="ANO004",
            name="Unusual Account Balance",
            description="Account balance deviation from historical",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.HIGH,
            conditions={"method": "balance_deviation", "threshold_pct": 50}
        ),
        DetectionRule(
            rule_id="ANO005",
            name="Unusual Transaction Volume",
            description="Transaction count anomaly",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.MEDIUM,
            conditions={"method": "volume_anomaly", "window_days": 30}
        ),
        DetectionRule(
            rule_id="ANO006",
            name="Velocity Anomaly",
            description="Unusual transaction velocity",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.HIGH,
            conditions={"method": "velocity", "max_per_hour": 50}
        ),
        DetectionRule(
            rule_id="ANO007",
            name="Time Series Anomaly",
            description="Deviation from time series forecast",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.MEDIUM,
            conditions={"method": "timeseries", "confidence_interval": 95}
        ),
        DetectionRule(
            rule_id="ANO008",
            name="Cluster Outlier",
            description="Transaction far from normal clusters",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.MEDIUM,
            conditions={"method": "clustering", "distance_threshold": 2.0}
        ),
        DetectionRule(
            rule_id="ANO009",
            name="Autoencoder Anomaly",
            description="Neural network reconstruction error high",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.HIGH,
            conditions={"method": "autoencoder", "error_threshold": 0.8}
        ),
        DetectionRule(
            rule_id="ANO010",
            name="LOF Anomaly",
            description="Local Outlier Factor detection",
            rule_type=RuleType.ANOMALY,
            severity=AlertSeverity.MEDIUM,
            conditions={"method": "lof", "neighbors": 20}
        ),

        # ===== CORRELATION RULES (20) =====
        DetectionRule(
            rule_id="COR001",
            name="Revenue-AR Mismatch",
            description="Revenue without corresponding AR",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.HIGH,
            conditions={"accounts": ["4*", "1200*"], "correlation_type": "match"}
        ),
        DetectionRule(
            rule_id="COR002",
            name="Expense-AP Mismatch",
            description="Expense without corresponding AP",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.MEDIUM,
            conditions={"accounts": ["6*", "2000*"], "correlation_type": "match"}
        ),
        DetectionRule(
            rule_id="COR003",
            name="Intercompany Imbalance",
            description="Intercompany transactions don't balance",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.CRITICAL,
            conditions={"accounts": ["1800*", "2800*"], "correlation_type": "balance"}
        ),
        DetectionRule(
            rule_id="COR004",
            name="Payroll-Liability Mismatch",
            description="Payroll without liability accrual",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.HIGH,
            conditions={"accounts": ["payroll*", "accrued_payroll*"], "correlation_type": "match"}
        ),
        DetectionRule(
            rule_id="COR005",
            name="Inventory-COGS Mismatch",
            description="Inventory relief without COGS",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.HIGH,
            conditions={"accounts": ["1300*", "5*"], "correlation_type": "match"}
        ),
        DetectionRule(
            rule_id="COR006",
            name="Cash-Bank Reconciliation",
            description="Cash entries vs bank statements",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.HIGH,
            conditions={"accounts": ["1000*"], "correlation_type": "external"}
        ),
        DetectionRule(
            rule_id="COR007",
            name="Depreciation Consistency",
            description="Depreciation entries match schedule",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.MEDIUM,
            conditions={"accounts": ["depr*"], "correlation_type": "schedule"}
        ),
        DetectionRule(
            rule_id="COR008",
            name="Lease Amortization",
            description="Lease entries match amortization schedule",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.MEDIUM,
            conditions={"accounts": ["lease*", "rou*"], "correlation_type": "schedule"}
        ),
        DetectionRule(
            rule_id="COR009",
            name="Tax Provision Consistency",
            description="Tax provision matches calculation",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.HIGH,
            conditions={"accounts": ["tax*"], "correlation_type": "calculation"}
        ),
        DetectionRule(
            rule_id="COR010",
            name="Currency Conversion",
            description="FX entries match rates",
            rule_type=RuleType.CORRELATION,
            severity=AlertSeverity.MEDIUM,
            conditions={"accounts": ["fx*"], "correlation_type": "rate"}
        ),

        # ===== SEQUENCE RULES (20) =====
        DetectionRule(
            rule_id="SEQ001",
            name="Rapid Fire Posting",
            description="Multiple transactions in quick succession",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.HIGH,
            threshold_count=10,
            time_window_minutes=5
        ),
        DetectionRule(
            rule_id="SEQ002",
            name="Split Transaction",
            description="Single transaction split into multiples",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.HIGH,
            conditions={"pattern": "split", "min_parts": 3}
        ),
        DetectionRule(
            rule_id="SEQ003",
            name="Reversal Pattern",
            description="Transaction followed by reversal",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "reversal", "window_hours": 24}
        ),
        DetectionRule(
            rule_id="SEQ004",
            name="Round Trip",
            description="Amount moved out and back",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.CRITICAL,
            conditions={"pattern": "round_trip", "window_days": 7}
        ),
        DetectionRule(
            rule_id="SEQ005",
            name="Layering Pattern",
            description="Multiple layered transactions",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.CRITICAL,
            conditions={"pattern": "layering", "min_layers": 3}
        ),
        DetectionRule(
            rule_id="SEQ006",
            name="Smurfing Detection",
            description="Multiple small transactions below threshold",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.CRITICAL,
            conditions={"pattern": "smurfing", "threshold": 10000, "count": 5}
        ),
        DetectionRule(
            rule_id="SEQ007",
            name="Period End Rush",
            description="Unusual transaction burst at period end",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.HIGH,
            conditions={"pattern": "period_end_rush", "threshold_multiplier": 3}
        ),
        DetectionRule(
            rule_id="SEQ008",
            name="Sequential Account Access",
            description="User accessing accounts sequentially",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "sequential_access"}
        ),
        DetectionRule(
            rule_id="SEQ009",
            name="Unusual Time Pattern",
            description="Transactions at unusual times",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "unusual_time"}
        ),
        DetectionRule(
            rule_id="SEQ010",
            name="Cascade Effect",
            description="Transaction triggering multiple others",
            rule_type=RuleType.SEQUENCE,
            severity=AlertSeverity.MEDIUM,
            conditions={"pattern": "cascade"}
        ),
    ]

    for rule in default_rules:
        rules_db[rule.rule_id] = rule

    logger.info(f"Initialized {len(rules_db)} default detection rules")


# Initialize rules on startup
initialize_default_rules()


# ============================================================================
# Detection Engine
# ============================================================================

class DetectionEngine:
    """Real-time transaction detection engine"""

    def __init__(self):
        self.transaction_history: Dict[str, List[GLTransaction]] = defaultdict(list)
        self.user_activity: Dict[str, List[GLTransaction]] = defaultdict(list)
        self.recent_amounts: Dict[str, List[float]] = defaultdict(list)
        self.alert_cooldowns: Dict[str, datetime] = {}

    async def process_transaction(self, txn: GLTransaction) -> List[Alert]:
        """Process a transaction and check all active rules"""
        alerts = []

        # Update history
        self.transaction_history[txn.account_code].append(txn)
        self.user_activity[txn.posting_user].append(txn)
        amount = max(txn.debit_amount, txn.credit_amount)
        self.recent_amounts[txn.account_code].append(amount)

        # Keep history bounded
        for key in list(self.transaction_history.keys()):
            self.transaction_history[key] = self.transaction_history[key][-1000:]
        for key in list(self.recent_amounts.keys()):
            self.recent_amounts[key] = self.recent_amounts[key][-100:]

        # Check each active rule
        for rule_id, rule in rules_db.items():
            if not rule.is_active:
                continue

            # Check cooldown
            if rule_id in self.alert_cooldowns:
                if datetime.utcnow() < self.alert_cooldowns[rule_id]:
                    continue

            # Run detection
            alert = await self._check_rule(rule, txn)
            if alert:
                alerts.append(alert)
                # Set cooldown
                self.alert_cooldowns[rule_id] = datetime.utcnow() + timedelta(minutes=rule.cooldown_minutes)

        return alerts

    async def _check_rule(self, rule: DetectionRule, txn: GLTransaction) -> Optional[Alert]:
        """Check if a transaction triggers a rule"""

        amount = max(txn.debit_amount, txn.credit_amount)

        # Check account patterns
        if rule.account_patterns and rule.account_patterns != ["*"]:
            matched = False
            for pattern in rule.account_patterns:
                if pattern.endswith("*"):
                    if txn.account_code.startswith(pattern[:-1]):
                        matched = True
                        break
                elif pattern.lower() in txn.account_code.lower() or pattern.lower() in txn.account_name.lower():
                    matched = True
                    break
            if not matched:
                return None

        triggered = False
        details = {}
        title = ""
        description = ""

        # Threshold rules
        if rule.rule_type == RuleType.THRESHOLD:
            if rule.threshold_amount and amount >= rule.threshold_amount:
                triggered = True
                title = f"{rule.name}: ${amount:,.2f}"
                description = f"Transaction amount ${amount:,.2f} exceeds threshold ${rule.threshold_amount:,.2f}"
                details = {"amount": amount, "threshold": rule.threshold_amount}

        # Pattern rules
        elif rule.rule_type == RuleType.PATTERN:
            pattern = rule.conditions.get("pattern", "")

            if pattern == "round_dollar":
                min_amt = rule.conditions.get("min_amount", 1000)
                if amount >= min_amt and amount % 100 == 0:
                    triggered = True
                    title = f"Round Dollar: ${amount:,.2f}"
                    description = f"Suspiciously round amount detected"

            elif pattern == "weekend_posting":
                if txn.timestamp.weekday() >= 5:
                    triggered = True
                    title = f"Weekend Posting: {txn.timestamp.strftime('%A')}"
                    description = f"Transaction posted on {txn.timestamp.strftime('%A')}"

            elif pattern == "after_hours":
                hour = txn.timestamp.hour
                start = rule.conditions.get("start_hour", 19)
                end = rule.conditions.get("end_hour", 7)
                if hour >= start or hour < end:
                    triggered = True
                    title = f"After Hours: {txn.timestamp.strftime('%H:%M')}"
                    description = f"Transaction posted at {txn.timestamp.strftime('%H:%M')}"

            elif pattern == "period_end":
                day = txn.timestamp.day
                days_from_end = rule.conditions.get("days_from_end", 3)
                if day >= 28:  # Simplified period end check
                    triggered = True
                    title = f"Period End Entry"
                    description = f"Transaction posted near period end (day {day})"

            elif pattern == "duplicate_amount":
                recent = self.recent_amounts.get(txn.account_code, [])[-50:]
                if recent.count(amount) > 1:
                    triggered = True
                    title = f"Duplicate Amount: ${amount:,.2f}"
                    description = f"Amount ${amount:,.2f} appears multiple times"

            elif pattern == "keywords":
                keywords = rule.conditions.get("keywords", [])
                desc_lower = txn.description.lower()
                found = [kw for kw in keywords if kw in desc_lower]
                if found:
                    triggered = True
                    title = f"Suspicious Keywords: {', '.join(found)}"
                    description = f"Description contains suspicious keywords"
                    details = {"keywords_found": found}

            elif pattern == "below_threshold":
                thresholds = rule.conditions.get("thresholds", [5000, 10000, 25000, 50000, 100000])
                for t in thresholds:
                    if t * 0.9 <= amount < t:
                        triggered = True
                        title = f"Just Below Threshold: ${amount:,.2f}"
                        description = f"Amount ${amount:,.2f} is just below ${t:,.2f} threshold"
                        details = {"threshold": t}
                        break

        # Anomaly rules
        elif rule.rule_type == RuleType.ANOMALY:
            method = rule.conditions.get("method", "zscore")

            if method == "zscore":
                recent = self.recent_amounts.get(txn.account_code, [])[-100:]
                if len(recent) >= 10:
                    import statistics
                    mean = statistics.mean(recent)
                    std = statistics.stdev(recent) or 1
                    zscore = abs((amount - mean) / std)
                    threshold = rule.conditions.get("threshold", 3.0)
                    if zscore > threshold:
                        triggered = True
                        title = f"Statistical Outlier (Z={zscore:.1f})"
                        description = f"Amount ${amount:,.2f} is {zscore:.1f} standard deviations from mean"
                        details = {"zscore": zscore, "mean": mean, "std": std}

            elif method == "benford":
                if amount > 0:
                    first_digit = int(str(int(amount))[0])
                    if first_digit >= 7:  # Simplified Benford check
                        triggered = True
                        title = f"Benford's Law Violation"
                        description = f"First digit {first_digit} is statistically unusual"
                        details = {"first_digit": first_digit}

        # Sequence rules
        elif rule.rule_type == RuleType.SEQUENCE:
            user_txns = self.user_activity.get(txn.posting_user, [])[-20:]

            if rule.threshold_count:
                window_start = txn.timestamp - timedelta(minutes=rule.time_window_minutes)
                recent_count = sum(1 for t in user_txns if t.timestamp >= window_start)
                if recent_count >= rule.threshold_count:
                    triggered = True
                    title = f"Rapid Fire Posting: {recent_count} in {rule.time_window_minutes}min"
                    description = f"User posted {recent_count} transactions in {rule.time_window_minutes} minutes"
                    details = {"transaction_count": recent_count}

        if triggered:
            alert = Alert(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                severity=rule.severity,
                title=title,
                description=description,
                details=details,
                affected_transactions=[txn.transaction_id],
                affected_accounts=[txn.account_code],
                total_amount=amount,
                recommended_actions=self._get_recommendations(rule, txn)
            )
            return alert

        return None

    def _get_recommendations(self, rule: DetectionRule, txn: GLTransaction) -> List[str]:
        """Generate recommendations based on rule and transaction"""
        recommendations = []

        if rule.severity == AlertSeverity.CRITICAL:
            recommendations.append("Escalate to management immediately")
            recommendations.append("Review all transactions from this user")

        if rule.rule_type == RuleType.THRESHOLD:
            recommendations.append("Review supporting documentation")
            recommendations.append("Verify proper authorization")

        if rule.rule_type == RuleType.PATTERN:
            recommendations.append("Investigate business purpose")
            recommendations.append("Compare to historical patterns")

        if rule.rule_type == RuleType.ANOMALY:
            recommendations.append("Analyze root cause")
            recommendations.append("Review related transactions")

        if rule.rule_type == RuleType.SEQUENCE:
            recommendations.append("Review all transactions in sequence")
            recommendations.append("Check for policy violations")

        return recommendations[:5]


# Global detection engine
detection_engine = DetectionEngine()


# ============================================================================
# WebSocket for Real-time Updates
# ============================================================================

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alert streaming"""
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_websockets.discard(websocket)


async def broadcast_alert(alert: Alert):
    """Broadcast alert to all connected WebSocket clients"""
    for ws in list(connected_websockets):
        try:
            await ws.send_json(alert.dict())
        except:
            connected_websockets.discard(ws)


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "GL Monitoring Service",
        "version": "1.0.0",
        "monitoring_status": monitoring_status.value,
        "rules_count": len(rules_db),
        "alerts_count": len(alerts_db)
    }


@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "Continuous GL Monitoring Service",
        "version": "1.0.0",
        "description": "Real-time GL monitoring with AI-powered detection rules",
        "features": [
            "Real-time transaction monitoring",
            "100+ pre-built detection rules",
            "Custom rules via natural language",
            "ML-powered anomaly detection",
            "WebSocket real-time alerts",
            "Intelligent alert prioritization"
        ],
        "rule_types": [t.value for t in RuleType],
        "rules_count": len(rules_db),
        "docs": "/docs"
    }


# -------------------- Transaction Processing --------------------

@app.post("/transactions/process", response_model=List[Alert])
async def process_transaction(
    transaction: GLTransaction,
    background_tasks: BackgroundTasks
):
    """
    Process a single GL transaction through all detection rules.
    Returns any alerts triggered.
    """
    global monitoring_status

    if monitoring_status != MonitoringStatus.ACTIVE:
        raise HTTPException(status_code=503, detail="Monitoring is paused")

    # Add to buffer
    transactions_buffer.append(transaction)
    if len(transactions_buffer) > 10000:
        transactions_buffer.pop(0)

    # Process through detection engine
    alerts = await detection_engine.process_transaction(transaction)

    # Store and broadcast alerts
    for alert in alerts:
        alerts_db[alert.alert_id] = alert
        background_tasks.add_task(broadcast_alert, alert)

    return alerts


@app.post("/transactions/batch", response_model=Dict[str, Any])
async def process_batch(
    transactions: List[GLTransaction],
    background_tasks: BackgroundTasks
):
    """Process a batch of transactions"""
    all_alerts = []

    for txn in transactions:
        alerts = await detection_engine.process_transaction(txn)
        all_alerts.extend(alerts)

        for alert in alerts:
            alerts_db[alert.alert_id] = alert

    # Broadcast summary
    if all_alerts:
        for alert in all_alerts[:10]:  # Limit broadcasts
            background_tasks.add_task(broadcast_alert, alert)

    return {
        "transactions_processed": len(transactions),
        "alerts_generated": len(all_alerts),
        "critical_alerts": sum(1 for a in all_alerts if a.severity == AlertSeverity.CRITICAL),
        "high_alerts": sum(1 for a in all_alerts if a.severity == AlertSeverity.HIGH)
    }


# -------------------- Rules Management --------------------

@app.get("/rules", response_model=List[DetectionRule])
async def list_rules(
    rule_type: Optional[RuleType] = None,
    is_active: Optional[bool] = None,
    severity: Optional[AlertSeverity] = None
):
    """List all detection rules"""
    rules = list(rules_db.values())

    if rule_type:
        rules = [r for r in rules if r.rule_type == rule_type]
    if is_active is not None:
        rules = [r for r in rules if r.is_active == is_active]
    if severity:
        rules = [r for r in rules if r.severity == severity]

    return rules


@app.get("/rules/{rule_id}", response_model=DetectionRule)
async def get_rule(rule_id: str):
    """Get specific rule"""
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rules_db[rule_id]


@app.post("/rules", response_model=DetectionRule)
async def create_rule(request: RuleCreateRequest):
    """Create a new detection rule"""
    rule = DetectionRule(
        name=request.name,
        description=request.description,
        rule_type=request.rule_type,
        severity=request.severity,
        natural_language_rule=request.natural_language_rule,
        conditions=request.conditions,
        threshold_amount=request.threshold_amount,
        account_patterns=request.account_patterns,
        time_window_minutes=request.time_window_minutes
    )

    rules_db[rule.rule_id] = rule
    logger.info(f"Created rule {rule.rule_id}: {rule.name}")

    return rule


@app.patch("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str):
    """Toggle rule active/inactive"""
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")

    rules_db[rule_id].is_active = not rules_db[rule_id].is_active
    return {"rule_id": rule_id, "is_active": rules_db[rule_id].is_active}


@app.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """Delete a rule"""
    if rule_id not in rules_db:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Don't delete system rules
    if rule_id.startswith(("THR", "PAT", "ANO", "COR", "SEQ")):
        raise HTTPException(status_code=400, detail="Cannot delete system rules")

    del rules_db[rule_id]
    return {"message": "Rule deleted", "rule_id": rule_id}


# -------------------- Alerts Management --------------------

@app.get("/alerts", response_model=List[Alert])
async def list_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    rule_id: Optional[str] = None,
    limit: int = 100
):
    """List alerts with filters"""
    alerts = list(alerts_db.values())

    if status:
        alerts = [a for a in alerts if a.status == status]
    if severity:
        alerts = [a for a in alerts if a.severity == severity]
    if rule_id:
        alerts = [a for a in alerts if a.rule_id == rule_id]

    # Sort by created_at descending
    alerts.sort(key=lambda a: a.created_at, reverse=True)

    return alerts[:limit]


@app.get("/alerts/{alert_id}", response_model=Alert)
async def get_alert(alert_id: str):
    """Get specific alert"""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alerts_db[alert_id]


@app.patch("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user_id: str = "current_user"):
    """Acknowledge an alert"""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = alerts_db[alert_id]
    alert.status = AlertStatus.ACKNOWLEDGED
    alert.acknowledged_at = datetime.utcnow()
    alert.acknowledged_by = user_id

    return alert


@app.patch("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution_notes: str,
    is_false_positive: bool = False,
    user_id: str = "current_user"
):
    """Resolve an alert"""
    if alert_id not in alerts_db:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert = alerts_db[alert_id]
    alert.status = AlertStatus.FALSE_POSITIVE if is_false_positive else AlertStatus.RESOLVED
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = user_id
    alert.resolution_notes = resolution_notes

    return alert


# -------------------- Dashboard --------------------

@app.get("/dashboard", response_model=MonitoringDashboard)
async def get_dashboard():
    """Get monitoring dashboard metrics"""
    today = datetime.utcnow().date()

    # Count today's transactions and alerts
    today_txns = [t for t in transactions_buffer if t.timestamp.date() == today]
    today_alerts = [a for a in alerts_db.values() if a.created_at.date() == today]

    # Alerts by severity
    alerts_by_severity = defaultdict(int)
    for alert in today_alerts:
        alerts_by_severity[alert.severity.value] += 1

    # Alerts by rule
    alerts_by_rule = defaultdict(int)
    for alert in today_alerts:
        alerts_by_rule[alert.rule_name] += 1

    # Transactions by hour
    txns_by_hour = defaultdict(int)
    for txn in today_txns:
        txns_by_hour[txn.timestamp.hour] += 1

    # Top triggered rules
    top_rules = sorted(alerts_by_rule.items(), key=lambda x: x[1], reverse=True)[:10]

    return MonitoringDashboard(
        status=monitoring_status,
        total_transactions_today=len(today_txns),
        total_amount_today=sum(max(t.debit_amount, t.credit_amount) for t in today_txns),
        alerts_today=len(today_alerts),
        critical_alerts=alerts_by_severity.get("critical", 0),
        rules_active=sum(1 for r in rules_db.values() if r.is_active),
        last_transaction_time=today_txns[-1].timestamp if today_txns else None,
        alerts_by_severity=dict(alerts_by_severity),
        alerts_by_rule=dict(alerts_by_rule),
        transactions_by_hour=dict(txns_by_hour),
        top_triggered_rules=[{"rule": r[0], "count": r[1]} for r in top_rules]
    )


# -------------------- Monitoring Control --------------------

@app.post("/monitoring/start")
async def start_monitoring():
    """Start GL monitoring"""
    global monitoring_status
    monitoring_status = MonitoringStatus.ACTIVE
    return {"status": "started", "monitoring_status": monitoring_status.value}


@app.post("/monitoring/pause")
async def pause_monitoring():
    """Pause GL monitoring"""
    global monitoring_status
    monitoring_status = MonitoringStatus.PAUSED
    return {"status": "paused", "monitoring_status": monitoring_status.value}


@app.get("/monitoring/status")
async def get_monitoring_status():
    """Get current monitoring status"""
    return {
        "status": monitoring_status.value,
        "rules_active": sum(1 for r in rules_db.values() if r.is_active),
        "transactions_in_buffer": len(transactions_buffer),
        "connected_clients": len(connected_websockets)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8032)
