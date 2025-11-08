"""
CMBS Document Parser Service
AI-powered extraction of deal terms from PSAs, prospectuses, and other deal documents
"""
import logging
import re
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class CMBSDocumentParser:
    """AI-powered parser for CMBS deal documents"""

    def __init__(self, db: AsyncSession, llm_service=None):
        """
        Initialize CMBS document parser

        Args:
            db: Database session
            llm_service: LLM service for AI extraction
        """
        self.db = db
        self.llm_service = llm_service

    async def parse_psa_document(
        self,
        deal_id: UUID,
        document_s3_uri: str,
        document_content: str
    ) -> Dict[str, Any]:
        """
        Parse Pooling and Servicing Agreement (PSA) using AI

        Args:
            deal_id: CMBS deal ID
            document_s3_uri: S3 URI of PSA document
            document_content: Full text of PSA

        Returns:
            Extracted deal terms
        """
        logger.info(f"Parsing PSA for deal {deal_id}")

        # Use AI to extract structured data from PSA
        extracted_terms = await self._ai_extract_psa_terms(document_content)

        # Store extracted terms
        insert_query = text("""
            INSERT INTO atlas.ai_extracted_deal_terms (
                deal_id, source_document_type, source_document_s3_uri,
                extracted_terms, ai_model_used, confidence_score
            ) VALUES (
                :deal_id, 'PSA', :document_uri, :terms::jsonb,
                :ai_model, :confidence
            )
            RETURNING id
        """)

        result = await self.db.execute(insert_query, {
            "deal_id": deal_id,
            "document_uri": document_s3_uri,
            "terms": json.dumps(extracted_terms),
            "ai_model": "claude-sonnet-4",
            "confidence": extracted_terms.get('_metadata', {}).get('confidence', 0.95)
        })

        extraction_id = result.scalar_one()
        await self.db.commit()

        logger.info(f"Extracted PSA terms for deal {deal_id}: {extraction_id}")
        return extracted_terms

    async def _ai_extract_psa_terms(self, psa_content: str) -> Dict[str, Any]:
        """
        Use AI to extract key terms from PSA

        Args:
            psa_content: Full PSA text

        Returns:
            Structured deal terms
        """
        # AI prompt for PSA extraction
        prompt = f"""
You are an expert in CMBS deal structures and Pooling and Servicing Agreements (PSAs).
Extract the following key terms from this PSA document:

1. Payment Dates: When are distributions made to investors?
2. Distribution Priority (Waterfall): How are cash flows prioritized?
3. Servicer Compensation: How is the servicer paid? What are the fees?
4. Servicing Fees: Master servicer fee, special servicer fee, trustee fee
5. Trigger Events: What events trigger changes to the waterfall or servicing?
6. Cleanup Call Provisions: When can the deal be called?
7. Advance Obligations: What advances is the servicer required to make?
8. Delinquency Definitions: When is a loan considered delinquent?
9. Special Servicing Transfer: When are loans transferred to special servicer?
10. Reporting Requirements: What reports must be provided and when?
11. Modification Authority: Under what conditions can loans be modified?
12. REO Management: How is real estate owned managed?

Return a JSON object with these fields. Be precise with dates, percentages, and dollar amounts.
If a term is not found, use null.

PSA CONTENT:
{psa_content[:50000]}  # Limit to avoid token limits

Return JSON only, no explanation.
"""

        if self.llm_service:
            # Use actual LLM service
            response = await self.llm_service.generate_structured_output(
                prompt=prompt,
                response_format="json"
            )
            extracted_terms = json.loads(response)
        else:
            # Fallback: Rule-based extraction with regex patterns
            extracted_terms = self._rule_based_extraction(psa_content)

        # Add metadata
        extracted_terms['_metadata'] = {
            'extraction_date': datetime.utcnow().isoformat(),
            'extraction_method': 'ai_llm' if self.llm_service else 'rule_based',
            'confidence': 0.95 if self.llm_service else 0.75,
            'document_length': len(psa_content)
        }

        return extracted_terms

    def _rule_based_extraction(self, psa_content: str) -> Dict[str, Any]:
        """
        Fallback rule-based extraction using regex patterns

        Args:
            psa_content: PSA text

        Returns:
            Extracted terms
        """
        terms = {}

        # Payment date patterns
        payment_date_pattern = r'(?:Distribution|Payment)\s+Date.*?(\d{1,2})(?:st|nd|rd|th)?\s+day\s+of\s+each\s+month'
        match = re.search(payment_date_pattern, psa_content, re.IGNORECASE)
        if match:
            terms['payment_date'] = match.group(1)

        # Servicer fee patterns
        servicer_fee_pattern = r'(?:Master\s+)?Servicer.*?Fee.*?(\d+(?:\.\d+)?)\s*(?:basis\s+points|%|percent)'
        match = re.search(servicer_fee_pattern, psa_content, re.IGNORECASE)
        if match:
            terms['master_servicer_fee_bps'] = float(match.group(1))

        # Delinquency definition
        delinquency_pattern = r'(?:Delinquent|Delinquency).*?(\d+)\s+days'
        match = re.search(delinquency_pattern, psa_content, re.IGNORECASE)
        if match:
            terms['delinquency_days'] = int(match.group(1))

        # Special servicing transfer
        special_servicing_pattern = r'(?:Special\s+Servicing|Specially\s+Serviced).*?(\d+)\s+days'
        match = re.search(special_servicing_pattern, psa_content, re.IGNORECASE)
        if match:
            terms['special_servicing_transfer_days'] = int(match.group(1))

        return terms

    async def parse_loan_tape(
        self,
        deal_id: UUID,
        loan_tape_file_path: str,
        file_format: str = 'csv'
    ) -> int:
        """
        Parse and load loan tape data

        Args:
            deal_id: CMBS deal ID
            loan_tape_file_path: Path to loan tape file
            file_format: File format ('csv', 'excel', 'txt')

        Returns:
            Number of loans loaded
        """
        logger.info(f"Parsing loan tape for deal {deal_id}")

        # Parse file based on format
        if file_format == 'csv':
            loans = await self._parse_csv_loan_tape(loan_tape_file_path)
        elif file_format == 'excel':
            loans = await self._parse_excel_loan_tape(loan_tape_file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        # Load loans into database
        loaded_count = 0
        for loan in loans:
            await self._insert_loan(deal_id, loan)
            loaded_count += 1

        await self.db.commit()

        logger.info(f"Loaded {loaded_count} loans for deal {deal_id}")
        return loaded_count

    async def _parse_csv_loan_tape(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse CSV loan tape"""
        import csv

        loans = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                loan = self._normalize_loan_data(row)
                loans.append(loan)

        return loans

    async def _parse_excel_loan_tape(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse Excel loan tape"""
        import pandas as pd

        df = pd.read_excel(file_path)
        loans = []

        for _, row in df.iterrows():
            loan = self._normalize_loan_data(row.to_dict())
            loans.append(loan)

        return loans

    def _normalize_loan_data(self, raw_loan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize loan data from various formats

        Args:
            raw_loan: Raw loan data from file

        Returns:
            Normalized loan dict
        """
        # Map common field variations
        field_mappings = {
            'loan_number': ['Loan Number', 'Loan ID', 'LoanNumber', 'loan_number'],
            'prospectus_loan_id': ['Prospectus ID', 'Prospectus Loan ID', 'ProspectusID'],
            'borrower_name': ['Borrower', 'Borrower Name', 'BorrowerName'],
            'property_name': ['Property', 'Property Name', 'PropertyName'],
            'property_type': ['Property Type', 'PropertyType', 'Type'],
            'original_balance': ['Original Balance', 'OriginalBalance', 'OB'],
            'current_balance': ['Current Balance', 'CurrentBalance', 'CB', 'Outstanding Balance'],
            'interest_rate': ['Interest Rate', 'Rate', 'Coupon'],
            'maturity_date': ['Maturity', 'Maturity Date', 'MaturityDate'],
            'property_state': ['State', 'Property State', 'ST'],
            'property_city': ['City', 'Property City'],
        }

        normalized = {}
        for normalized_field, possible_names in field_mappings.items():
            for name in possible_names:
                if name in raw_loan and raw_loan[name] is not None:
                    normalized[normalized_field] = raw_loan[name]
                    break

        return normalized

    async def _insert_loan(self, deal_id: UUID, loan_data: Dict[str, Any]):
        """Insert loan into database"""
        insert_query = text("""
            INSERT INTO atlas.cmbs_loan_tape (
                deal_id, loan_number, prospectus_loan_id,
                borrower_name, property_name, property_type,
                property_city, property_state,
                original_balance, current_balance, interest_rate,
                maturity_date, as_of_date
            ) VALUES (
                :deal_id, :loan_number, :prospectus_loan_id,
                :borrower_name, :property_name, :property_type,
                :property_city, :property_state,
                :original_balance, :current_balance, :interest_rate,
                :maturity_date, :as_of_date
            )
            ON CONFLICT DO NOTHING
        """)

        await self.db.execute(insert_query, {
            "deal_id": deal_id,
            "loan_number": loan_data.get('loan_number'),
            "prospectus_loan_id": loan_data.get('prospectus_loan_id'),
            "borrower_name": loan_data.get('borrower_name'),
            "property_name": loan_data.get('property_name'),
            "property_type": loan_data.get('property_type'),
            "property_city": loan_data.get('property_city'),
            "property_state": loan_data.get('property_state'),
            "original_balance": loan_data.get('original_balance'),
            "current_balance": loan_data.get('current_balance'),
            "interest_rate": loan_data.get('interest_rate'),
            "maturity_date": loan_data.get('maturity_date'),
            "as_of_date": loan_data.get('as_of_date', date.today())
        })

    async def identify_risks_ai(
        self,
        deal_id: UUID,
        engagement_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """
        Use AI to identify risks in CMBS deal

        Args:
            deal_id: CMBS deal ID
            engagement_id: Optional engagement ID

        Returns:
            List of identified risks
        """
        logger.info(f"AI risk identification for deal {deal_id}")

        # Get deal data
        deal_data = await self._get_deal_data(deal_id)

        # Use AI to identify risks
        risks = await self._ai_analyze_risks(deal_data)

        # Store identified risks
        for risk in risks:
            insert_query = text("""
                INSERT INTO atlas.ai_identified_risks (
                    deal_id, reg_ab_engagement_id, risk_category,
                    risk_title, risk_description, risk_severity,
                    supporting_data, ai_model_used, confidence_score
                ) VALUES (
                    :deal_id, :engagement_id, :category,
                    :title, :description, :severity,
                    :supporting_data::jsonb, :ai_model, :confidence
                )
            """)

            await self.db.execute(insert_query, {
                "deal_id": deal_id,
                "engagement_id": engagement_id,
                "category": risk['category'],
                "title": risk['title'],
                "description": risk['description'],
                "severity": risk['severity'],
                "supporting_data": json.dumps(risk.get('supporting_data', {})),
                "ai_model": "claude-sonnet-4",
                "confidence": risk.get('confidence', 0.90)
            })

        await self.db.commit()

        logger.info(f"Identified {len(risks)} risks for deal {deal_id}")
        return risks

    async def _get_deal_data(self, deal_id: UUID) -> Dict[str, Any]:
        """Get comprehensive deal data for AI analysis"""
        query = text("""
            SELECT
                d.*,
                (SELECT COUNT(*) FROM atlas.cmbs_loan_tape WHERE deal_id = d.id) as loan_count,
                (SELECT COUNT(*) FROM atlas.cmbs_loan_tape WHERE deal_id = d.id AND is_current = FALSE) as delinquent_count,
                (SELECT SUM(current_balance) FROM atlas.cmbs_loan_tape WHERE deal_id = d.id AND days_delinquent >= 90) as balance_90plus,
                (SELECT json_agg(property_type) FROM (
                    SELECT property_type, COUNT(*) as count, SUM(current_balance) as balance
                    FROM atlas.cmbs_loan_tape
                    WHERE deal_id = d.id
                    GROUP BY property_type
                ) prop_types) as property_type_concentration
            FROM atlas.cmbs_deals d
            WHERE d.id = :deal_id
        """)

        result = await self.db.execute(query, {"deal_id": deal_id})
        row = result.fetchone()

        if not row:
            raise ValueError(f"Deal {deal_id} not found")

        # Convert to dict
        deal_data = dict(row._mapping)
        return deal_data

    async def _ai_analyze_risks(self, deal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use AI to analyze deal risks"""

        prompt = f"""
Analyze this CMBS deal for risks and issues that should be reported to investors and noted in the Regulation AB assessment.

Deal Data:
- Deal Name: {deal_data.get('deal_name')}
- Current Balance: ${deal_data.get('current_balance'):,.2f}
- Number of Loans: {deal_data.get('loan_count')}
- Delinquent Loans: {deal_data.get('delinquent_count')}
- 90+ Days Delinquent Balance: ${deal_data.get('balance_90plus', 0):,.2f}
- Property Type Concentration: {deal_data.get('property_type_concentration')}

Identify risks in these categories:
1. Concentration risk (geographic, property type, borrower)
2. Credit risk (delinquencies, defaults)
3. Performance trends
4. Structural concerns

For each risk, provide:
- category: One of 'concentration', 'delinquency', 'property_type', 'geographic', 'structural'
- title: Brief title
- description: Detailed description
- severity: 'low', 'medium', 'high', or 'critical'
- supporting_data: Any relevant metrics

Return JSON array of risks.
"""

        if self.llm_service:
            response = await self.llm_service.generate_structured_output(
                prompt=prompt,
                response_format="json"
            )
            risks = json.loads(response)
        else:
            # Fallback: Rule-based risk identification
            risks = self._rule_based_risk_identification(deal_data)

        return risks

    def _rule_based_risk_identification(self, deal_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback rule-based risk identification"""
        risks = []

        # Delinquency risk
        delinquent_count = deal_data.get('delinquent_count', 0)
        loan_count = deal_data.get('loan_count', 1)
        delinquency_rate = delinquent_count / loan_count if loan_count > 0 else 0

        if delinquency_rate > 0.10:  # >10% delinquency
            risks.append({
                'category': 'delinquency',
                'title': 'Elevated Delinquency Rate',
                'description': f'Delinquency rate of {delinquency_rate:.1%} exceeds industry benchmark of 5%.',
                'severity': 'high' if delinquency_rate > 0.15 else 'medium',
                'confidence': 1.0,
                'supporting_data': {
                    'delinquent_count': delinquent_count,
                    'total_loans': loan_count,
                    'delinquency_rate': delinquency_rate
                }
            })

        # 90+ day delinquency risk
        balance_90plus = deal_data.get('balance_90plus', 0)
        current_balance = deal_data.get('current_balance', 1)
        if current_balance > 0 and balance_90plus / current_balance > 0.05:
            risks.append({
                'category': 'delinquency',
                'title': 'Material 90+ Day Delinquencies',
                'description': f'${balance_90plus:,.2f} ({balance_90plus/current_balance:.1%}) of pool balance is 90+ days delinquent.',
                'severity': 'high',
                'confidence': 1.0,
                'supporting_data': {
                    'balance_90plus': float(balance_90plus),
                    'current_balance': float(current_balance),
                    'percentage': balance_90plus / current_balance
                }
            })

        return risks
