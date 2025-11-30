"""
Compliance Report Generator
AICPA, GAAP, FASB, PCAOB, and SEC Compliant Report Generation

Supports:
- Compilations (SSARS AR-C 80)
- Reviews (SSARS AR-C 90)
- Audits (GAAS AU-C 700, PCAOB AS 3101)
- Management Representation Letters (AU-C 580, AS 2805)
- Cover Letters
- Notes to Financial Statements (FASB ASC)

Standards Compliance:
- AICPA: AU-C 700, AU-C 570, AU-C 580, AU-C 260, AR-C 80, AR-C 90
- PCAOB: AS 3101, AS 2401, AS 2415, AS 2805, AS 1301
- GAAP/FASB: ASC 205-10, ASC 235, ASC 275, ASC 450, ASC 606, ASC 842
- SEC: Regulation S-X, Regulation S-K (for public companies)
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from decimal import Decimal
import jinja2

logger = logging.getLogger(__name__)


class EngagementType(str, Enum):
    """Engagement types per professional standards"""
    COMPILATION = "compilation"  # SSARS AR-C 80
    REVIEW = "review"           # SSARS AR-C 90
    AUDIT = "audit"             # GAAS AU-C / PCAOB AS
    AUDIT_INTEGRATED = "audit_integrated"  # PCAOB Integrated Audit


class OpinionType(str, Enum):
    """Opinion/Report types per professional standards"""
    # Audit Opinions (AU-C 700, AS 3101)
    UNMODIFIED = "unmodified"
    QUALIFIED_SCOPE = "qualified_scope"
    QUALIFIED_GAAP = "qualified_gaap"
    ADVERSE = "adverse"
    DISCLAIMER = "disclaimer"
    # Review Conclusions (AR-C 90)
    REVIEW_UNMODIFIED = "review_unmodified"
    REVIEW_MODIFIED = "review_modified"
    # Compilation Reports (AR-C 80)
    COMPILATION_STANDARD = "compilation_standard"
    COMPILATION_NO_INDEPENDENCE = "compilation_no_independence"
    COMPILATION_OMIT_DISCLOSURES = "compilation_omit_disclosures"


class EntityType(str, Enum):
    """Entity types for report customization"""
    PUBLIC_COMPANY = "public_company"       # SEC registrant
    PRIVATE_COMPANY = "private_company"     # Nonpublic entity
    NONPROFIT = "nonprofit"                 # Not-for-profit
    GOVERNMENT = "government"               # Governmental entity
    ERISA_PLAN = "erisa_plan"              # Employee benefit plan


class FinancialFramework(str, Enum):
    """Financial reporting frameworks"""
    GAAP_US = "gaap_us"
    IFRS = "ifrs"
    TAX_BASIS = "tax_basis"
    CASH_BASIS = "cash_basis"
    REGULATORY_BASIS = "regulatory_basis"
    CONTRACTUAL_BASIS = "contractual_basis"


class ComplianceReportGenerator:
    """
    Generates fully compliant financial statement reports per:
    - AICPA Professional Standards
    - PCAOB Auditing Standards
    - GAAP/FASB Codification
    - SEC Regulations (where applicable)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the compliance report generator.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.template_env = jinja2.Environment(
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True
        )
        self._register_template_filters()

    def _register_template_filters(self):
        """Register custom Jinja2 filters for report generation"""
        self.template_env.filters['currency'] = lambda v: f"${v:,.0f}" if v else "$0"
        self.template_env.filters['percentage'] = lambda v: f"{v:.1%}" if v else "0.0%"
        self.template_env.filters['date_format'] = lambda v, fmt="%B %d, %Y": v.strftime(fmt) if v else ""

    # =========================================================================
    # ACCOUNTANT'S REPORT GENERATORS
    # =========================================================================

    def generate_compilation_report(
        self,
        context: Dict[str, Any],
        opinion_type: OpinionType = OpinionType.COMPILATION_STANDARD,
        framework: FinancialFramework = FinancialFramework.GAAP_US
    ) -> str:
        """
        Generate Compilation Report per SSARS AR-C 80.

        Required context keys:
        - addressee: Report addressee
        - entity_name: Name of the entity
        - financial_statements: List of statements compiled
        - period_end_date: Balance sheet date
        - period_description: E.g., "year ended December 31, 2024"
        - firm_name: CPA firm name
        - report_date: Date of report
        - has_independence: Whether firm is independent

        Args:
            context: Report context data
            opinion_type: Type of compilation report
            framework: Financial reporting framework

        Returns:
            HTML-formatted compilation report
        """
        self._validate_context(context, [
            'addressee', 'entity_name', 'financial_statements',
            'period_end_date', 'period_description', 'firm_name', 'report_date'
        ])

        template = self._get_compilation_template(opinion_type, framework)
        return self._render_template(template, context)

    def _get_compilation_template(
        self,
        opinion_type: OpinionType,
        framework: FinancialFramework
    ) -> str:
        """Get compilation report template per AR-C 80"""

        framework_text = self._get_framework_text(framework)
        omit_disclosures_para = ""
        no_independence_para = ""

        if opinion_type == OpinionType.COMPILATION_OMIT_DISCLOSURES:
            omit_disclosures_para = """
<p><strong>Management has elected to omit substantially all of the disclosures required by {{ framework_name }}.</strong>
If the omitted disclosures were included in the financial statements, they might influence the user's
conclusions about the entity's financial position, results of operations, and cash flows. Accordingly,
the financial statements are not designed for those who are not informed about such matters.</p>
"""
        elif opinion_type == OpinionType.COMPILATION_NO_INDEPENDENCE:
            no_independence_para = """
<p><strong>We are not independent with respect to {{ entity_name }}.</strong></p>
"""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Independent Accountant's Compilation Report</title>
    <style>
        body {{ font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.6; margin: 1in; }}
        h1 {{ font-size: 14pt; font-weight: bold; text-align: center; margin-bottom: 24pt; }}
        p {{ margin: 12pt 0; text-align: justify; }}
        .addressee {{ margin-bottom: 18pt; }}
        .signature-block {{ margin-top: 36pt; }}
        .firm-name {{ font-weight: bold; }}
    </style>
</head>
<body>

<h1>INDEPENDENT ACCOUNTANT'S COMPILATION REPORT</h1>

<div class="addressee">
<p>{{{{ addressee }}}}</p>
</div>

<p>Management is responsible for the accompanying financial statements of {{{{ entity_name }}}}
(the "{{{{ entity_type | default('Company') }}}}"), which comprise the balance sheet as of {{{{ period_end_date | date_format }}}},
and the related statements of {{% for stmt in financial_statements %}}{{{{ stmt }}}}{{% if not loop.last %}}, {{% endif %}}{{% endfor %}}
for the {{{{ period_description }}}}, and the related notes to the financial statements
in accordance with {framework_text}.</p>

<p>We have performed a compilation engagement in accordance with Statements on Standards for
Accounting and Review Services promulgated by the Accounting and Review Services Committee of the AICPA.
We did not audit or review the financial statements nor were we required to perform any procedures to
verify the accuracy or completeness of the information provided by management. We do not express an
opinion, a conclusion, nor provide any form of assurance on these financial statements.</p>

{omit_disclosures_para}
{no_independence_para}

<div class="signature-block">
<p class="firm-name">{{{{ firm_name }}}}</p>
<p>{{{{ firm_city }}}}, {{{{ firm_state }}}}</p>
<p>{{{{ report_date | date_format }}}}</p>
</div>

</body>
</html>
"""

    def generate_review_report(
        self,
        context: Dict[str, Any],
        opinion_type: OpinionType = OpinionType.REVIEW_UNMODIFIED,
        framework: FinancialFramework = FinancialFramework.GAAP_US,
        emphasis_paragraphs: Optional[List[str]] = None
    ) -> str:
        """
        Generate Review Report per SSARS AR-C 90.

        Required context keys:
        - addressee: Report addressee
        - entity_name: Name of the entity
        - financial_statements: List of statements reviewed
        - period_end_date: Balance sheet date
        - period_description: E.g., "year ended December 31, 2024"
        - firm_name: CPA firm name
        - report_date: Date of report

        Args:
            context: Report context data
            opinion_type: Type of review conclusion
            framework: Financial reporting framework
            emphasis_paragraphs: Optional emphasis of matter paragraphs

        Returns:
            HTML-formatted review report
        """
        self._validate_context(context, [
            'addressee', 'entity_name', 'financial_statements',
            'period_end_date', 'period_description', 'firm_name', 'report_date'
        ])

        context['emphasis_paragraphs'] = emphasis_paragraphs or []
        template = self._get_review_template(opinion_type, framework)
        return self._render_template(template, context)

    def _get_review_template(
        self,
        opinion_type: OpinionType,
        framework: FinancialFramework
    ) -> str:
        """Get review report template per AR-C 90"""

        framework_text = self._get_framework_text(framework)

        # Standard unmodified conclusion
        if opinion_type == OpinionType.REVIEW_UNMODIFIED:
            conclusion = f"""
<p><strong>Accountant's Conclusion</strong></p>
<p>Based on our review, we are not aware of any material modifications that should be made to the
accompanying financial statements in order for them to be in accordance with {framework_text}.</p>
"""
        else:
            conclusion = """
<p><strong>Accountant's Conclusion</strong></p>
<p>Based on our review, except for the effects of the matter described in the Basis for Modified Conclusion
paragraph, we are not aware of any material modifications that should be made to the accompanying
financial statements in order for them to be in accordance with {{ framework_name }}.</p>

<p><strong>Basis for Modified Conclusion</strong></p>
<p>{{ modification_basis }}</p>
"""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Independent Accountant's Review Report</title>
    <style>
        body {{ font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.6; margin: 1in; }}
        h1 {{ font-size: 14pt; font-weight: bold; text-align: center; margin-bottom: 24pt; }}
        p {{ margin: 12pt 0; text-align: justify; }}
        .section-header {{ font-weight: bold; margin-top: 18pt; }}
        .addressee {{ margin-bottom: 18pt; }}
        .signature-block {{ margin-top: 36pt; }}
        .firm-name {{ font-weight: bold; }}
    </style>
</head>
<body>

<h1>INDEPENDENT ACCOUNTANT'S REVIEW REPORT</h1>

<div class="addressee">
<p>{{{{ addressee }}}}</p>
</div>

<p>We have reviewed the accompanying financial statements of {{{{ entity_name }}}}
(the "{{{{ entity_type | default('Company') }}}}"), which comprise the balance sheet as of {{{{ period_end_date | date_format }}}},
and the related statements of {{% for stmt in financial_statements %}}{{{{ stmt }}}}{{% if not loop.last %}}, {{% endif %}}{{% endfor %}}
for the {{{{ period_description }}}}, and the related notes to the financial statements.</p>

<p class="section-header">Management's Responsibility for the Financial Statements</p>
<p>Management is responsible for the preparation and fair presentation of these financial statements
in accordance with {framework_text}; this includes the design, implementation,
and maintenance of internal control relevant to the preparation and fair presentation of financial
statements that are free from material misstatement whether due to fraud or error.</p>

<p class="section-header">Accountant's Responsibility</p>
<p>Our responsibility is to conduct the review engagement in accordance with Statements on Standards
for Accounting and Review Services promulgated by the Accounting and Review Services Committee of the AICPA.
Those standards require us to perform procedures to obtain limited assurance as a basis for reporting
whether we are aware of any material modifications that should be made to the financial statements
for them to be in accordance with {framework_text}. We believe that the results
of our procedures provide a reasonable basis for our conclusion.</p>

<p>We are required to be independent of {{{{ entity_name }}}} and to meet our other ethical responsibilities,
in accordance with the relevant ethical requirements related to our review.</p>

{conclusion}

{{% for para in emphasis_paragraphs %}}
<p><strong>Emphasis of Matter</strong></p>
<p>{{{{ para }}}}</p>
{{% endfor %}}

<div class="signature-block">
<p class="firm-name">{{{{ firm_name }}}}</p>
<p>{{{{ firm_city }}}}, {{{{ firm_state }}}}</p>
<p>{{{{ report_date | date_format }}}}</p>
</div>

</body>
</html>
"""

    def generate_audit_report(
        self,
        context: Dict[str, Any],
        opinion_type: OpinionType = OpinionType.UNMODIFIED,
        entity_type: EntityType = EntityType.PRIVATE_COMPANY,
        framework: FinancialFramework = FinancialFramework.GAAP_US,
        going_concern: bool = False,
        key_audit_matters: Optional[List[Dict[str, str]]] = None,
        emphasis_paragraphs: Optional[List[str]] = None,
        other_matter_paragraphs: Optional[List[str]] = None
    ) -> str:
        """
        Generate Audit Report per AU-C 700 / PCAOB AS 3101.

        Required context keys:
        - addressee: Report addressee (e.g., "Board of Directors and Shareholders")
        - entity_name: Name of the entity
        - financial_statements: List of statements audited
        - period_end_date: Balance sheet date
        - period_description: E.g., "year ended December 31, 2024"
        - firm_name: CPA firm name
        - report_date: Date of report
        - partner_name: Engagement partner name (required for public companies)

        Args:
            context: Report context data
            opinion_type: Type of audit opinion
            entity_type: Type of entity (public, private, nonprofit)
            framework: Financial reporting framework
            going_concern: Whether going concern paragraph is needed
            key_audit_matters: Critical audit matters (public companies)
            emphasis_paragraphs: Emphasis of matter paragraphs
            other_matter_paragraphs: Other matter paragraphs

        Returns:
            HTML-formatted audit report
        """
        self._validate_context(context, [
            'addressee', 'entity_name', 'financial_statements',
            'period_end_date', 'period_description', 'firm_name', 'report_date'
        ])

        context['going_concern'] = going_concern
        context['key_audit_matters'] = key_audit_matters or []
        context['emphasis_paragraphs'] = emphasis_paragraphs or []
        context['other_matter_paragraphs'] = other_matter_paragraphs or []
        context['is_public'] = entity_type == EntityType.PUBLIC_COMPANY

        template = self._get_audit_template(opinion_type, entity_type, framework)
        return self._render_template(template, context)

    def _get_audit_template(
        self,
        opinion_type: OpinionType,
        entity_type: EntityType,
        framework: FinancialFramework
    ) -> str:
        """Get audit report template per AU-C 700 / AS 3101"""

        framework_text = self._get_framework_text(framework)
        is_public = entity_type == EntityType.PUBLIC_COMPANY

        # Opinion paragraph based on type
        opinion_paragraphs = self._get_opinion_paragraphs(opinion_type, framework_text)

        # PCAOB-specific elements for public companies
        pcaob_elements = ""
        if is_public:
            pcaob_elements = """
<p class="section-header">Critical Audit Matters</p>
<p>Critical audit matters are matters arising from the current period audit of the financial statements
that were communicated or required to be communicated to the audit committee and that: (1) relate to
accounts or disclosures that are material to the financial statements and (2) involved our especially
challenging, subjective, or complex judgments. The communication of critical audit matters does not alter
in any way our opinion on the financial statements, taken as a whole, and we are not, by communicating
the critical audit matters below, providing separate opinions on the critical audit matters or on the
accounts or disclosures to which they relate.</p>

{% for kam in key_audit_matters %}
<p><strong>{{ kam.title }}</strong></p>
<p>{{ kam.description }}</p>
<p><strong>How the Critical Audit Matter Was Addressed in the Audit:</strong></p>
<p>{{ kam.audit_response }}</p>
{% endfor %}

{% if not key_audit_matters %}
<p>We determined that there are no critical audit matters.</p>
{% endif %}
"""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Independent Auditor's Report</title>
    <style>
        body {{ font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.6; margin: 1in; }}
        h1 {{ font-size: 14pt; font-weight: bold; text-align: center; margin-bottom: 24pt; }}
        p {{ margin: 12pt 0; text-align: justify; }}
        .section-header {{ font-weight: bold; margin-top: 18pt; }}
        .addressee {{ margin-bottom: 18pt; }}
        .signature-block {{ margin-top: 36pt; }}
        .firm-name {{ font-weight: bold; }}
        ul {{ margin: 6pt 0 6pt 24pt; }}
        li {{ margin: 3pt 0; }}
    </style>
</head>
<body>

<h1>REPORT OF INDEPENDENT {'REGISTERED PUBLIC ACCOUNTING FIRM' if is_public else 'AUDITOR'}</h1>

<div class="addressee">
<p>To the {{{{ addressee }}}} of {{{{ entity_name }}}}:</p>
</div>

{opinion_paragraphs}

<p class="section-header">Basis for Opinion</p>
<p>We conducted our audit in accordance with {'the standards of the Public Company Accounting Oversight Board (United States) (PCAOB)' if is_public else 'auditing standards generally accepted in the United States of America (GAAS)'}.
Our responsibilities under those standards are further described in the Auditor's Responsibilities for
the Audit of the Financial Statements section of our report. We are required to be independent of
{{{{ entity_name }}}} and to meet our other ethical responsibilities, in accordance with the relevant
ethical requirements relating to our audit. We believe that the audit evidence we have obtained is
sufficient and appropriate to provide a basis for our audit opinion.</p>

{{% if going_concern %}}
<p class="section-header">{'Substantial Doubt About the Entity\\'s Ability to Continue as a Going Concern' if is_public else 'Going Concern'}</p>
<p>The accompanying financial statements have been prepared assuming that the {{{{ entity_type | default('Company') }}}}
will continue as a going concern. As discussed in Note {{{{ going_concern_note_number | default('X') }}}} to the financial
statements, the {{{{ entity_type | default('Company') }}}} has {{{{ going_concern_conditions }}}} that raise substantial doubt
about its ability to continue as a going concern. Management's evaluation of the events and conditions
and management's plans regarding these matters are also described in Note {{{{ going_concern_note_number | default('X') }}}}.
The financial statements do not include any adjustments that might result from the outcome of this uncertainty.
Our opinion is not modified with respect to this matter.</p>
{{% endif %}}

{{% for para in emphasis_paragraphs %}}
<p class="section-header">Emphasis of Matter</p>
<p>{{{{ para }}}} Our opinion is not modified with respect to this matter.</p>
{{% endfor %}}

{pcaob_elements}

<p class="section-header">Responsibilities of Management for the Financial Statements</p>
<p>Management is responsible for the preparation and fair presentation of the financial statements
in accordance with {framework_text}, and for the design, implementation, and maintenance of internal
control relevant to the preparation and fair presentation of financial statements that are free from
material misstatement, whether due to fraud or error.</p>

<p>In preparing the financial statements, management is required to evaluate whether there are
conditions or events, considered in the aggregate, that raise substantial doubt about the
{{{{ entity_type | default('Company') }}}}'s ability to continue as a going concern for
{'one year after the date that the financial statements are available to be issued' if framework == FinancialFramework.GAAP_US else 'twelve months from the balance sheet date'}.</p>

<p class="section-header">Auditor's Responsibilities for the Audit of the Financial Statements</p>
<p>Our objectives are to obtain reasonable assurance about whether the financial statements as a whole
are free from material misstatement, whether due to fraud or error, and to issue an auditor's report
that includes our opinion. Reasonable assurance is a high level of assurance but is not absolute
assurance and therefore is not a guarantee that an audit conducted in accordance with
{'PCAOB standards' if is_public else 'GAAS'} will always detect a material misstatement when it exists.
The risk of not detecting a material misstatement resulting from fraud is higher than for one resulting
from error, as fraud may involve collusion, forgery, intentional omissions, misrepresentations, or
the override of internal control. Misstatements are considered material if there is a substantial
likelihood that, individually or in the aggregate, they would influence the judgment made by a
reasonable user based on the financial statements.</p>

<p>In performing an audit in accordance with {'PCAOB standards' if is_public else 'GAAS'}, we:</p>
<ul>
<li>Exercise professional judgment and maintain professional skepticism throughout the audit.</li>
<li>Identify and assess the risks of material misstatement of the financial statements, whether due to
fraud or error, and design and perform audit procedures responsive to those risks. Such procedures
include examining, on a test basis, evidence regarding the amounts and disclosures in the financial
statements.</li>
<li>Obtain an understanding of internal control relevant to the audit in order to design audit
procedures that are appropriate in the circumstances{', but not for the purpose of expressing an opinion on the effectiveness of the entity\\'s internal control' if not is_public else '. Accordingly, we express such an opinion'}.</li>
<li>Evaluate the appropriateness of accounting policies used and the reasonableness of significant
accounting estimates made by management, as well as evaluate the overall presentation of the
financial statements.</li>
<li>Conclude whether, in our judgment, there are conditions or events, considered in the aggregate,
that raise substantial doubt about the {{{{ entity_type | default('Company') }}}}'s ability to continue
as a going concern for a reasonable period of time.</li>
</ul>

<p>We are required to communicate with those charged with governance regarding, among other matters,
the planned scope and timing of the audit, significant audit findings, and certain internal control-related
matters that we identified during the audit.</p>

{{% for para in other_matter_paragraphs %}}
<p class="section-header">Other Matter</p>
<p>{{{{ para }}}}</p>
{{% endfor %}}

{'<p>We have served as the Company\\'s auditor since {{ auditor_tenure_year }}.</p>' if is_public else ''}

<div class="signature-block">
<p class="firm-name">{{{{ firm_name }}}}</p>
{{% if is_public and partner_name %}}
<p>{{{{ partner_name }}}}</p>
{{% endif %}}
<p>{{{{ firm_city }}}}, {{{{ firm_state }}}}</p>
<p>{{{{ report_date | date_format }}}}</p>
</div>

</body>
</html>
"""

    def _get_opinion_paragraphs(
        self,
        opinion_type: OpinionType,
        framework_text: str
    ) -> str:
        """Generate opinion paragraph based on opinion type"""

        if opinion_type == OpinionType.UNMODIFIED:
            return f"""
<p class="section-header">Opinion</p>
<p>We have audited the financial statements of {{{{ entity_name }}}} (the "{{{{ entity_type | default('Company') }}}}"),
which comprise the balance sheet as of {{{{ period_end_date | date_format }}}}, and the related statements of
{{% for stmt in financial_statements %}}{{{{ stmt }}}}{{% if not loop.last %}}, {{% endif %}}{{% endfor %}}
for the {{{{ period_description }}}}, and the related notes to the financial statements.</p>

<p>In our opinion, the accompanying financial statements present fairly, in all material respects,
the financial position of {{{{ entity_name }}}} as of {{{{ period_end_date | date_format }}}}, and the results
of its operations and its cash flows for the {{{{ period_description }}}} in accordance with {framework_text}.</p>
"""
        elif opinion_type == OpinionType.QUALIFIED_GAAP:
            return f"""
<p class="section-header">Qualified Opinion</p>
<p>We have audited the financial statements of {{{{ entity_name }}}} (the "{{{{ entity_type | default('Company') }}}}"),
which comprise the balance sheet as of {{{{ period_end_date | date_format }}}}, and the related statements of
{{% for stmt in financial_statements %}}{{{{ stmt }}}}{{% if not loop.last %}}, {{% endif %}}{{% endfor %}}
for the {{{{ period_description }}}}, and the related notes to the financial statements.</p>

<p>In our opinion, except for the effects of the matter described in the Basis for Qualified Opinion
section of our report, the accompanying financial statements present fairly, in all material respects,
the financial position of {{{{ entity_name }}}} as of {{{{ period_end_date | date_format }}}}, and the results
of its operations and its cash flows for the {{{{ period_description }}}} in accordance with {framework_text}.</p>

<p class="section-header">Basis for Qualified Opinion</p>
<p>{{{{ qualification_basis }}}}</p>
"""
        elif opinion_type == OpinionType.QUALIFIED_SCOPE:
            return f"""
<p class="section-header">Qualified Opinion</p>
<p>We have audited the financial statements of {{{{ entity_name }}}} (the "{{{{ entity_type | default('Company') }}}}"),
which comprise the balance sheet as of {{{{ period_end_date | date_format }}}}, and the related statements of
{{% for stmt in financial_statements %}}{{{{ stmt }}}}{{% if not loop.last %}}, {{% endif %}}{{% endfor %}}
for the {{{{ period_description }}}}, and the related notes to the financial statements.</p>

<p>In our opinion, except for the possible effects of the matter described in the Basis for Qualified
Opinion section of our report, the accompanying financial statements present fairly, in all material
respects, the financial position of {{{{ entity_name }}}} as of {{{{ period_end_date | date_format }}}}, and the
results of its operations and its cash flows for the {{{{ period_description }}}} in accordance with {framework_text}.</p>

<p class="section-header">Basis for Qualified Opinion</p>
<p>{{{{ scope_limitation_basis }}}}</p>
"""
        elif opinion_type == OpinionType.ADVERSE:
            return f"""
<p class="section-header">Adverse Opinion</p>
<p>We have audited the financial statements of {{{{ entity_name }}}} (the "{{{{ entity_type | default('Company') }}}}"),
which comprise the balance sheet as of {{{{ period_end_date | date_format }}}}, and the related statements of
{{% for stmt in financial_statements %}}{{{{ stmt }}}}{{% if not loop.last %}}, {{% endif %}}{{% endfor %}}
for the {{{{ period_description }}}}, and the related notes to the financial statements.</p>

<p>In our opinion, because of the significance of the matter described in the Basis for Adverse
Opinion section of our report, the accompanying financial statements do not present fairly the
financial position of {{{{ entity_name }}}} as of {{{{ period_end_date | date_format }}}}, or the results of its
operations or its cash flows for the {{{{ period_description }}}} in accordance with {framework_text}.</p>

<p class="section-header">Basis for Adverse Opinion</p>
<p>{{{{ adverse_basis }}}}</p>
"""
        elif opinion_type == OpinionType.DISCLAIMER:
            return f"""
<p class="section-header">Disclaimer of Opinion</p>
<p>We were engaged to audit the financial statements of {{{{ entity_name }}}} (the "{{{{ entity_type | default('Company') }}}}"),
which comprise the balance sheet as of {{{{ period_end_date | date_format }}}}, and the related statements of
{{% for stmt in financial_statements %}}{{{{ stmt }}}}{{% if not loop.last %}}, {{% endif %}}{{% endfor %}}
for the {{{{ period_description }}}}, and the related notes to the financial statements.</p>

<p>We do not express an opinion on the accompanying financial statements of {{{{ entity_name }}}}.
Because of the significance of the matter described in the Basis for Disclaimer of Opinion section
of our report, we have not been able to obtain sufficient appropriate audit evidence to provide a
basis for an audit opinion on these financial statements.</p>

<p class="section-header">Basis for Disclaimer of Opinion</p>
<p>{{{{ disclaimer_basis }}}}</p>
"""
        return ""

    # =========================================================================
    # MANAGEMENT REPRESENTATION LETTER GENERATOR
    # =========================================================================

    def generate_management_rep_letter(
        self,
        context: Dict[str, Any],
        engagement_type: EngagementType = EngagementType.AUDIT,
        include_fraud_representations: bool = True,
        include_going_concern: bool = False,
        additional_representations: Optional[List[str]] = None
    ) -> str:
        """
        Generate Management Representation Letter per AU-C 580 / AS 2805.

        Required context keys:
        - firm_name: CPA firm name and address
        - entity_name: Company name
        - period_end_date: Balance sheet date
        - period_description: E.g., "year ended December 31, 2024"
        - ceo_name: CEO name and title
        - cfo_name: CFO name and title
        - letter_date: Date of letter

        Args:
            context: Letter context data
            engagement_type: Type of engagement
            include_fraud_representations: Include fraud-related representations
            include_going_concern: Include going concern representations
            additional_representations: Additional custom representations

        Returns:
            HTML-formatted management representation letter
        """
        self._validate_context(context, [
            'firm_name', 'entity_name', 'period_end_date',
            'period_description', 'ceo_name', 'cfo_name', 'letter_date'
        ])

        context['engagement_type'] = engagement_type.value
        context['include_fraud'] = include_fraud_representations
        context['include_going_concern'] = include_going_concern
        context['additional_representations'] = additional_representations or []

        template = self._get_management_rep_template(engagement_type)
        return self._render_template(template, context)

    def _get_management_rep_template(self, engagement_type: EngagementType) -> str:
        """Get management representation letter template per AU-C 580 / AS 2805"""

        engagement_description = {
            EngagementType.AUDIT: "audit of the financial statements",
            EngagementType.REVIEW: "review of the financial statements",
            EngagementType.COMPILATION: "compilation of the financial statements"
        }.get(engagement_type, "examination")

        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Management Representation Letter</title>
    <style>
        body { font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.6; margin: 1in; }
        .letterhead { margin-bottom: 24pt; }
        .date { margin-bottom: 18pt; }
        .addressee { margin-bottom: 18pt; }
        p { margin: 12pt 0; text-align: justify; }
        ol { margin: 12pt 0 12pt 24pt; }
        li { margin: 6pt 0; }
        .signature-block { margin-top: 48pt; }
        .signature-line { margin-top: 36pt; border-top: 1px solid black; width: 250px; }
    </style>
</head>
<body>

<div class="letterhead">
<p><strong>{{ entity_name }}</strong></p>
<p>{{ entity_address | default('') }}</p>
</div>

<div class="date">
<p>{{ letter_date | date_format }}</p>
</div>

<div class="addressee">
<p>{{ firm_name }}</p>
<p>{{ firm_address | default('') }}</p>
</div>

<p>This representation letter is provided in connection with your """ + engagement_description + """ of
{{ entity_name }} (the "Company") as of and for the {{ period_description }}, for the purpose of expressing
an opinion{% if engagement_type == 'review' %} (or conclusion){% endif %} as to whether the financial statements are presented fairly,
in all material respects, in accordance with accounting principles generally accepted in the United States of America (U.S. GAAP).</p>

<p>We confirm, to the best of our knowledge and belief, as of {{ letter_date | date_format }}:</p>

<p><strong>Financial Statements</strong></p>
<ol>
<li>We have fulfilled our responsibilities, as set out in the terms of the engagement letter, for the
preparation and fair presentation of the financial statements in accordance with U.S. GAAP.</li>

<li>Significant assumptions used by us in making accounting estimates, including those measured at fair
value, are reasonable.</li>

<li>Related party relationships and transactions have been appropriately accounted for and disclosed in
accordance with U.S. GAAP.</li>

<li>All events subsequent to the date of the financial statements and for which U.S. GAAP requires
adjustment or disclosure have been adjusted or disclosed.</li>

<li>The effects of uncorrected misstatements are immaterial, both individually and in the aggregate, to
the financial statements as a whole. A list of the uncorrected misstatements is attached to this letter.</li>

<li>The effects of all known actual or possible litigation and claims have been accounted for and
disclosed in accordance with U.S. GAAP.</li>
</ol>

<p><strong>Information Provided</strong></p>
<ol start="7">
<li>We have provided you with:
    <ol type="a">
    <li>Access to all information, of which we are aware, that is relevant to the preparation and fair
    presentation of the financial statements, such as records, documentation, and other matters;</li>
    <li>Additional information that you have requested from us for the purpose of the """ + engagement_description + """; and</li>
    <li>Unrestricted access to persons within the Company from whom you determined it necessary to
    obtain audit evidence.</li>
    </ol>
</li>

<li>All transactions have been recorded in the accounting records and are reflected in the financial
statements.</li>

<li>We have disclosed to you the results of our assessment of the risk that the financial statements
may be materially misstated as a result of fraud.</li>

<li>We have no knowledge of any fraud or suspected fraud that affects the Company and involves:
    <ol type="a">
    <li>Management;</li>
    <li>Employees who have significant roles in internal control; or</li>
    <li>Others where the fraud could have a material effect on the financial statements.</li>
    </ol>
</li>

<li>We have no knowledge of any allegations of fraud, or suspected fraud, affecting the Company's
financial statements communicated by employees, former employees, analysts, regulators, or others.</li>

<li>We have disclosed to you all known instances of noncompliance or suspected noncompliance with
laws and regulations whose effects should be considered when preparing financial statements.</li>

<li>We have disclosed to you the identity of the Company's related parties and all related party
relationships and transactions of which we are aware.</li>
</ol>

{% if include_going_concern %}
<p><strong>Going Concern</strong></p>
<ol start="14">
<li>We have disclosed to you all information relevant to the use of the going concern assumption,
including significant conditions and events, our plans, and the adequacy of related disclosures.</li>

<li>We confirm that we believe the effects of the matters disclosed above have been adequately disclosed
and that the Company has the ability to continue as a going concern for the twelve months following
the balance sheet date.</li>
</ol>
{% endif %}

{% if include_fraud %}
<p><strong>Fraud and Illegal Acts (AU-C 240/250, AS 2401)</strong></p>
<ol start="16">
<li>We acknowledge our responsibility for the design, implementation, and maintenance of internal
control to prevent and detect fraud.</li>

<li>We have disclosed to you all significant deficiencies and material weaknesses in the design or
operation of internal control over financial reporting of which we are aware.</li>

<li>We have made available to you all minutes of the meetings of stockholders, directors, and committees
of directors, or summaries of actions of recent meetings for which minutes have not yet been prepared.</li>
</ol>
{% endif %}

{% for rep in additional_representations %}
<p>{{ rep }}</p>
{% endfor %}

<div class="signature-block">
<p>Very truly yours,</p>

<p class="signature-line"></p>
<p>{{ ceo_name }}<br>{{ ceo_title | default('Chief Executive Officer') }}</p>

<p class="signature-line"></p>
<p>{{ cfo_name }}<br>{{ cfo_title | default('Chief Financial Officer') }}</p>
</div>

</body>
</html>
"""

    # =========================================================================
    # COVER LETTER GENERATOR
    # =========================================================================

    def generate_cover_letter(
        self,
        context: Dict[str, Any],
        engagement_type: EngagementType = EngagementType.AUDIT,
        include_deliverables_list: bool = True
    ) -> str:
        """
        Generate Cover Letter for financial statement package.

        Required context keys:
        - recipient_name: Name of recipient
        - recipient_title: Title of recipient
        - recipient_company: Company name
        - recipient_address: Address
        - entity_name: Entity name
        - period_description: E.g., "year ended December 31, 2024"
        - firm_name: CPA firm name
        - partner_name: Engagement partner name
        - letter_date: Date of letter
        - deliverables: List of documents being provided

        Args:
            context: Letter context data
            engagement_type: Type of engagement
            include_deliverables_list: Include detailed deliverables list

        Returns:
            HTML-formatted cover letter
        """
        self._validate_context(context, [
            'recipient_name', 'entity_name', 'period_description',
            'firm_name', 'partner_name', 'letter_date'
        ])

        context['engagement_type_display'] = {
            EngagementType.AUDIT: "audit",
            EngagementType.REVIEW: "review",
            EngagementType.COMPILATION: "compilation"
        }.get(engagement_type, "engagement")

        context['include_deliverables_list'] = include_deliverables_list

        template = self._get_cover_letter_template(engagement_type)
        return self._render_template(template, context)

    def _get_cover_letter_template(self, engagement_type: EngagementType) -> str:
        """Get cover letter template"""

        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Cover Letter</title>
    <style>
        body { font-family: "Times New Roman", Times, serif; font-size: 12pt; line-height: 1.6; margin: 1in; }
        .firm-letterhead { text-align: center; margin-bottom: 36pt; border-bottom: 2px solid #333; padding-bottom: 12pt; }
        .firm-name { font-size: 16pt; font-weight: bold; }
        .firm-info { font-size: 10pt; color: #666; }
        .date { margin-bottom: 18pt; }
        .addressee { margin-bottom: 24pt; }
        p { margin: 12pt 0; text-align: justify; }
        ul { margin: 12pt 0 12pt 24pt; }
        li { margin: 6pt 0; }
        .signature-block { margin-top: 36pt; }
    </style>
</head>
<body>

<div class="firm-letterhead">
<p class="firm-name">{{ firm_name }}</p>
<p class="firm-info">{{ firm_address | default('') }}</p>
<p class="firm-info">{{ firm_phone | default('') }} | {{ firm_email | default('') }}</p>
</div>

<div class="date">
<p>{{ letter_date | date_format }}</p>
</div>

<div class="addressee">
<p>{{ recipient_name }}<br>
{% if recipient_title %}{{ recipient_title }}<br>{% endif %}
{{ recipient_company | default(entity_name) }}<br>
{{ recipient_address | default('') }}</p>
</div>

<p>Dear {{ recipient_salutation | default(recipient_name) }}:</p>

<p>We are pleased to submit the enclosed financial statements and related {{ engagement_type_display }} report
for {{ entity_name }} for the {{ period_description }}.</p>

{% if include_deliverables_list and deliverables %}
<p>Enclosed please find the following documents:</p>
<ul>
{% for item in deliverables %}
<li>{{ item }}</li>
{% endfor %}
</ul>
{% endif %}

{% if engagement_type_display == 'audit' %}
<p>Our audit was conducted in accordance with auditing standards generally accepted in the United States of America.
Those standards require that we plan and perform the audit to obtain reasonable assurance about whether the
financial statements are free of material misstatement. Our report on the financial statements is included
in this package.</p>
{% elif engagement_type_display == 'review' %}
<p>Our review was conducted in accordance with Statements on Standards for Accounting and Review Services
promulgated by the AICPA. A review consists primarily of inquiries of company personnel and analytical
procedures applied to financial data. Our report on the financial statements is included in this package.</p>
{% else %}
<p>Our compilation was conducted in accordance with Statements on Standards for Accounting and Review Services
promulgated by the AICPA. A compilation is limited to presenting in the form of financial statements
information that is the representation of management. Our report on the financial statements is included
in this package.</p>
{% endif %}

{% if management_letter_included %}
<p>Additionally, we have included a management letter that discusses certain matters that came to our attention
during our {{ engagement_type_display }}. These comments and recommendations are intended to help you improve
your internal controls and operating efficiency.</p>
{% endif %}

<p>We appreciate the opportunity to serve {{ entity_name }} and thank you for your cooperation during our
engagement. Should you have any questions regarding the enclosed documents or if we may be of further
assistance, please do not hesitate to contact us.</p>

<div class="signature-block">
<p>Sincerely,</p>
<p><strong>{{ firm_name }}</strong></p>
<p>{{ partner_name }}<br>{{ partner_title | default('Partner') }}</p>
</div>

</body>
</html>
"""

    # =========================================================================
    # NOTES TO FINANCIAL STATEMENTS GENERATOR
    # =========================================================================

    def generate_notes_to_financial_statements(
        self,
        context: Dict[str, Any],
        framework: FinancialFramework = FinancialFramework.GAAP_US,
        disclosure_selections: Optional[Dict[str, bool]] = None
    ) -> str:
        """
        Generate Notes to Financial Statements per GAAP/FASB ASC.

        Required context keys:
        - entity_name: Company name
        - period_end_date: Balance sheet date
        - period_description: E.g., "year ended December 31, 2024"
        - nature_of_business: Description of business
        - fiscal_year_end: Fiscal year end date description

        Optional context for specific disclosures (based on disclosure_selections):
        - significant_accounting_policies: Dict of policies
        - revenue_recognition: Revenue recognition policy details
        - property_plant_equipment: PPE details
        - leases: Lease obligations details
        - debt: Debt/borrowings details
        - commitments_contingencies: Commitments and contingencies
        - related_party_transactions: Related party details
        - subsequent_events: Subsequent events
        - going_concern: Going concern details
        - segment_information: Segment reporting data

        Args:
            context: Notes context data
            framework: Financial reporting framework
            disclosure_selections: Dict of which disclosures to include

        Returns:
            HTML-formatted notes to financial statements
        """
        self._validate_context(context, [
            'entity_name', 'period_end_date', 'nature_of_business'
        ])

        # Default disclosure selections
        default_disclosures = {
            'summary_of_significant_policies': True,
            'nature_of_business': True,
            'revenue_recognition': True,
            'cash_and_cash_equivalents': True,
            'accounts_receivable': True,
            'inventory': True,
            'property_plant_equipment': True,
            'intangible_assets': True,
            'leases': True,
            'debt': True,
            'income_taxes': True,
            'stockholders_equity': True,
            'commitments_contingencies': True,
            'related_party_transactions': True,
            'subsequent_events': True,
            'going_concern': False,
            'segment_information': False,
            'fair_value_measurements': True,
            'concentration_of_risk': True
        }

        disclosures = {**default_disclosures, **(disclosure_selections or {})}
        context['disclosures'] = disclosures

        template = self._get_notes_template(framework)
        return self._render_template(template, context)

    def _get_notes_template(self, framework: FinancialFramework) -> str:
        """Get notes to financial statements template per FASB ASC"""

        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Notes to Financial Statements</title>
    <style>
        body { font-family: "Times New Roman", Times, serif; font-size: 11pt; line-height: 1.5; margin: 1in; }
        h1 { font-size: 14pt; font-weight: bold; text-align: center; margin-bottom: 24pt; }
        h2 { font-size: 12pt; font-weight: bold; margin-top: 18pt; margin-bottom: 12pt; }
        h3 { font-size: 11pt; font-weight: bold; font-style: italic; margin-top: 12pt; margin-bottom: 6pt; }
        p { margin: 6pt 0; text-align: justify; }
        .note-header { text-align: center; margin-bottom: 24pt; }
        table { border-collapse: collapse; width: 100%; margin: 12pt 0; }
        th, td { border: 1px solid #999; padding: 6pt; text-align: left; }
        th { background-color: #f0f0f0; }
        .amount { text-align: right; }
    </style>
</head>
<body>

<div class="note-header">
<h1>{{ entity_name }}</h1>
<p><strong>NOTES TO FINANCIAL STATEMENTS</strong></p>
<p>{{ period_description | title }}</p>
</div>

{% set note_number = namespace(value=1) %}

{% if disclosures.nature_of_business %}
<h2>NOTE {{ note_number.value }} - NATURE OF BUSINESS AND ORGANIZATION</h2>
{% set note_number.value = note_number.value + 1 %}

<p>{{ entity_name }} (the "{{ entity_type | default('Company') }}") {{ nature_of_business }}</p>

{% if formation_date %}
<p>The {{ entity_type | default('Company') }} was {{ formation_type | default('incorporated') }}
in the State of {{ formation_state }} on {{ formation_date | date_format }}.</p>
{% endif %}

{% if fiscal_year_end %}
<p>The {{ entity_type | default('Company') }}'s fiscal year ends on {{ fiscal_year_end }}.</p>
{% endif %}
{% endif %}

{% if disclosures.going_concern and going_concern %}
<h2>NOTE {{ note_number.value }} - GOING CONCERN</h2>
{% set note_number.value = note_number.value + 1 %}

<p>The accompanying financial statements have been prepared assuming that the {{ entity_type | default('Company') }}
will continue as a going concern. {{ going_concern_conditions }}</p>

<p>Management's plans regarding these matters are as follows: {{ going_concern_plans }}</p>

<p>The financial statements do not include any adjustments that might result from the outcome of this uncertainty.
If the {{ entity_type | default('Company') }} is unable to continue as a going concern, the recoverability
and classification of recorded asset amounts and the classification of liabilities may require adjustment.</p>
{% endif %}

{% if disclosures.summary_of_significant_policies %}
<h2>NOTE {{ note_number.value }} - SUMMARY OF SIGNIFICANT ACCOUNTING POLICIES</h2>
{% set note_number.value = note_number.value + 1 %}

<h3>Basis of Presentation</h3>
<p>The accompanying financial statements have been prepared in accordance with accounting principles
generally accepted in the United States of America ("U.S. GAAP"). The preparation of financial statements
in conformity with U.S. GAAP requires management to make estimates and assumptions that affect the reported
amounts of assets and liabilities and disclosure of contingent assets and liabilities at the date of the
financial statements and the reported amounts of revenues and expenses during the reporting period.
Actual results could differ from those estimates.</p>

<h3>Use of Estimates</h3>
<p>The preparation of financial statements in conformity with U.S. GAAP requires management to make estimates
and assumptions that affect the reported amounts of assets and liabilities and disclosure of contingent
assets and liabilities at the date of the financial statements. Significant estimates include, but are not
limited to, {{ significant_estimates | default('the allowance for doubtful accounts, useful lives of property and equipment, valuation of inventory, and accrued liabilities') }}.
Actual results could differ from those estimates.</p>

{% if disclosures.cash_and_cash_equivalents %}
<h3>Cash and Cash Equivalents</h3>
<p>The {{ entity_type | default('Company') }} considers all highly liquid investments with an original
maturity of three months or less when purchased to be cash equivalents. Cash and cash equivalents are
maintained at financial institutions and, at times, balances may exceed federally insured limits. The
{{ entity_type | default('Company') }} has never experienced any losses related to these balances.</p>
{% endif %}

{% if disclosures.accounts_receivable %}
<h3>Accounts Receivable</h3>
<p>Accounts receivable are recorded at the invoiced amount and do not bear interest. The allowance for
doubtful accounts is the {{ entity_type | default('Company') }}'s best estimate of the amount of probable
credit losses in the existing accounts receivable. The {{ entity_type | default('Company') }} determines
the allowance based on historical write-off experience and current economic conditions. Account balances
are charged off against the allowance after all means of collection have been exhausted and the potential
for recovery is considered remote.</p>
{% endif %}

{% if disclosures.inventory %}
<h3>Inventory</h3>
<p>Inventory is stated at the lower of cost or net realizable value. Cost is determined using the
{{ inventory_method | default('first-in, first-out (FIFO)') }} method. Inventory consists of
{{ inventory_components | default('raw materials, work in process, and finished goods') }}.
The {{ entity_type | default('Company') }} periodically reviews inventory for slow-moving or obsolete items
and provides reserves as necessary.</p>
{% endif %}

{% if disclosures.property_plant_equipment %}
<h3>Property and Equipment</h3>
<p>Property and equipment are stated at cost, less accumulated depreciation. Depreciation is calculated
using the {{ depreciation_method | default('straight-line') }} method over the estimated useful lives of
the assets, which range from {{ useful_lives | default('3 to 39 years') }}. Leasehold improvements are
amortized over the shorter of the lease term or the estimated useful life of the improvement. Expenditures
for maintenance and repairs are charged to expense as incurred. When assets are retired or otherwise
disposed of, the cost and related accumulated depreciation are removed from the accounts, and any resulting
gain or loss is included in the results of operations.</p>
{% endif %}

{% if disclosures.intangible_assets %}
<h3>Intangible Assets</h3>
<p>Intangible assets consist primarily of {{ intangible_types | default('goodwill, customer relationships, and trademarks') }}.
Intangible assets with finite useful lives are amortized on a straight-line basis over their estimated useful lives.
Goodwill and indefinite-lived intangible assets are not amortized but are tested for impairment at least annually,
or more frequently if events or changes in circumstances indicate that the asset might be impaired, in accordance
with ASC 350, <em>Intangibles-Goodwill and Other</em>.</p>
{% endif %}

{% if disclosures.revenue_recognition %}
<h3>Revenue Recognition (ASC 606)</h3>
<p>The {{ entity_type | default('Company') }} recognizes revenue in accordance with ASC 606, <em>Revenue from
Contracts with Customers</em>. Revenue is recognized when control of the promised goods or services is
transferred to customers, in an amount that reflects the consideration the {{ entity_type | default('Company') }}
expects to be entitled to in exchange for those goods or services.</p>

<p>The {{ entity_type | default('Company') }} applies the following five-step model to recognize revenue:</p>
<ol>
<li>Identification of the contract with a customer</li>
<li>Identification of the performance obligations in the contract</li>
<li>Determination of the transaction price</li>
<li>Allocation of the transaction price to the performance obligations in the contract</li>
<li>Recognition of revenue when (or as) each performance obligation is satisfied</li>
</ol>

{% if revenue_streams %}
<p>The {{ entity_type | default('Company') }}'s revenue is derived from the following sources:</p>
<ul>
{% for stream in revenue_streams %}
<li><strong>{{ stream.name }}:</strong> {{ stream.description }}</li>
{% endfor %}
</ul>
{% endif %}
{% endif %}

{% if disclosures.leases %}
<h3>Leases (ASC 842)</h3>
<p>The {{ entity_type | default('Company') }} determines if an arrangement is a lease at inception. Operating
leases are included in operating lease right-of-use ("ROU") assets and operating lease liabilities in the
balance sheet. Finance leases are included in property and equipment, finance lease liabilities, current,
and finance lease liabilities, noncurrent in the balance sheet.</p>

<p>ROU assets represent the {{ entity_type | default('Company') }}'s right to use an underlying asset for the
lease term and lease liabilities represent the {{ entity_type | default('Company') }}'s obligation to make
lease payments arising from the lease. Operating lease ROU assets and liabilities are recognized at the
commencement date based on the present value of lease payments over the lease term. The {{ entity_type | default('Company') }}
uses its incremental borrowing rate based on the information available at the commencement date to determine
the present value of lease payments when the rate implicit in the lease is not readily determinable.</p>
{% endif %}

{% if disclosures.income_taxes %}
<h3>Income Taxes</h3>
<p>The {{ entity_type | default('Company') }} accounts for income taxes in accordance with ASC 740, <em>Income Taxes</em>.
Deferred tax assets and liabilities are recognized for the future tax consequences attributable to differences
between the financial statement carrying amounts of existing assets and liabilities and their respective tax bases.
Deferred tax assets and liabilities are measured using enacted tax rates expected to apply to taxable income in
the years in which those temporary differences are expected to be recovered or settled.</p>

<p>The {{ entity_type | default('Company') }} evaluates uncertain tax positions using a two-step approach. Recognition
(step one) occurs when the {{ entity_type | default('Company') }} concludes that a tax position, based solely on its
technical merits, is more-likely-than-not to be sustained upon examination. Measurement (step two) determines the
amount of benefit that is more-likely-than-not to be realized upon settlement. The {{ entity_type | default('Company') }}
accrues interest and penalties related to uncertain tax positions as a component of income tax expense.</p>
{% endif %}

{% if disclosures.fair_value_measurements %}
<h3>Fair Value Measurements (ASC 820)</h3>
<p>The {{ entity_type | default('Company') }} applies the provisions of ASC 820, <em>Fair Value Measurement</em>,
which establishes a framework for measuring fair value and expands disclosures about fair value measurements.
ASC 820 defines fair value as the price that would be received to sell an asset or paid to transfer a liability
in an orderly transaction between market participants at the measurement date. ASC 820 also establishes a
three-level hierarchy for fair value measurements based upon the transparency of inputs to the valuation of
an asset or liability as of the measurement date.</p>
{% endif %}

{% if disclosures.concentration_of_risk %}
<h3>Concentration of Credit Risk</h3>
<p>Financial instruments that potentially subject the {{ entity_type | default('Company') }} to credit risk
consist primarily of cash and cash equivalents and accounts receivable. The {{ entity_type | default('Company') }}
maintains its cash and cash equivalents with high-quality financial institutions. The {{ entity_type | default('Company') }}
performs ongoing credit evaluations of its customers and generally does not require collateral. The
{{ entity_type | default('Company') }} maintains reserves for potential credit losses and such losses have been
within management's expectations.</p>

{% if major_customers %}
<p>For the {{ period_description }}, the following customers represented more than 10% of total revenues:</p>
<ul>
{% for customer in major_customers %}
<li>{{ customer.name }}: {{ customer.percentage }}%</li>
{% endfor %}
</ul>
{% endif %}
{% endif %}
{% endif %}

{% if disclosures.debt and debt_details %}
<h2>NOTE {{ note_number.value }} - DEBT</h2>
{% set note_number.value = note_number.value + 1 %}

<p>Debt consists of the following at {{ period_end_date | date_format }}:</p>

<table>
<tr>
    <th>Description</th>
    <th class="amount">Amount</th>
</tr>
{% for item in debt_details %}
<tr>
    <td>{{ item.description }}</td>
    <td class="amount">{{ item.amount | currency }}</td>
</tr>
{% endfor %}
<tr>
    <td><strong>Total Debt</strong></td>
    <td class="amount"><strong>{{ total_debt | currency }}</strong></td>
</tr>
<tr>
    <td>Less: Current portion</td>
    <td class="amount">({{ current_debt | currency }})</td>
</tr>
<tr>
    <td><strong>Long-term Debt</strong></td>
    <td class="amount"><strong>{{ long_term_debt | currency }}</strong></td>
</tr>
</table>

{% if debt_maturities %}
<p>Future minimum principal payments on long-term debt are as follows:</p>
<table>
<tr>
    <th>Year Ending</th>
    <th class="amount">Amount</th>
</tr>
{% for year in debt_maturities %}
<tr>
    <td>{{ year.period }}</td>
    <td class="amount">{{ year.amount | currency }}</td>
</tr>
{% endfor %}
</table>
{% endif %}
{% endif %}

{% if disclosures.commitments_contingencies %}
<h2>NOTE {{ note_number.value }} - COMMITMENTS AND CONTINGENCIES</h2>
{% set note_number.value = note_number.value + 1 %}

<h3>Leases</h3>
<p>{{ lease_commitments | default('The ' + (entity_type | default('Company')) + ' leases certain office space and equipment under operating lease agreements. See Note X for additional lease disclosures.') }}</p>

<h3>Legal Matters</h3>
<p>{{ legal_contingencies | default('In the ordinary course of business, the ' + (entity_type | default('Company')) + ' may be subject to various legal proceedings and claims. Management believes that any ultimate liability arising from these matters would not have a material adverse effect on the ' + (entity_type | default('Company')) + '\\'s financial position, results of operations, or cash flows.') }}</p>

{% if other_commitments %}
<h3>Other Commitments</h3>
<p>{{ other_commitments }}</p>
{% endif %}
{% endif %}

{% if disclosures.related_party_transactions and related_parties %}
<h2>NOTE {{ note_number.value }} - RELATED PARTY TRANSACTIONS</h2>
{% set note_number.value = note_number.value + 1 %}

{% for transaction in related_parties %}
<p>{{ transaction.description }}</p>
{% endfor %}
{% endif %}

{% if disclosures.stockholders_equity %}
<h2>NOTE {{ note_number.value }} - STOCKHOLDERS' EQUITY</h2>
{% set note_number.value = note_number.value + 1 %}

<h3>Authorized Stock</h3>
<p>The {{ entity_type | default('Company') }} is authorized to issue {{ authorized_shares | default('10,000,000') }}
shares of common stock with a par value of ${{ par_value | default('0.001') }} per share.</p>

{% if stock_transactions %}
<h3>Stock Transactions</h3>
{% for transaction in stock_transactions %}
<p>{{ transaction }}</p>
{% endfor %}
{% endif %}

{% if dividends %}
<h3>Dividends</h3>
<p>{{ dividends }}</p>
{% endif %}
{% endif %}

{% if disclosures.subsequent_events %}
<h2>NOTE {{ note_number.value }} - SUBSEQUENT EVENTS</h2>
{% set note_number.value = note_number.value + 1 %}

<p>Management has evaluated subsequent events through {{ subsequent_events_date | date_format | default(report_date | date_format) }},
the date the financial statements were available to be issued.</p>

{% if subsequent_events_items %}
{% for event in subsequent_events_items %}
<p>{{ event }}</p>
{% endfor %}
{% else %}
<p>No material subsequent events have occurred since {{ period_end_date | date_format }} that would require
recognition or disclosure in the financial statements.</p>
{% endif %}
{% endif %}

</body>
</html>
"""

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _validate_context(self, context: Dict[str, Any], required_keys: List[str]):
        """Validate that required context keys are present"""
        missing = [key for key in required_keys if key not in context or context[key] is None]
        if missing:
            raise ValueError(f"Missing required context keys: {', '.join(missing)}")

    def _render_template(self, template_str: str, context: Dict[str, Any]) -> str:
        """Render Jinja2 template with context"""
        try:
            template = self.template_env.from_string(template_str)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template rendering error: {e}")
            raise ValueError(f"Failed to render template: {e}")

    def _get_framework_text(self, framework: FinancialFramework) -> str:
        """Get display text for financial framework"""
        return {
            FinancialFramework.GAAP_US: "accounting principles generally accepted in the United States of America",
            FinancialFramework.IFRS: "International Financial Reporting Standards as issued by the International Accounting Standards Board",
            FinancialFramework.TAX_BASIS: "the income tax basis of accounting",
            FinancialFramework.CASH_BASIS: "the cash basis of accounting",
            FinancialFramework.REGULATORY_BASIS: "the regulatory basis of accounting prescribed by {{ regulatory_body }}",
            FinancialFramework.CONTRACTUAL_BASIS: "the contractual basis of accounting specified in {{ contract_reference }}"
        }.get(framework, "accounting principles generally accepted in the United States of America")


# =========================================================================
# COMPLETE REPORT PACKAGE GENERATOR
# =========================================================================

class CompleteReportPackageGenerator:
    """
    Generates a complete financial statement package including:
    - Cover Letter
    - Accountant's Report
    - Financial Statements
    - Notes to Financial Statements
    - Management Representation Letter (internal)
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the package generator"""
        self.config = config or {}
        self.report_generator = ComplianceReportGenerator(config)

    def generate_complete_package(
        self,
        context: Dict[str, Any],
        engagement_type: EngagementType,
        opinion_type: OpinionType,
        entity_type: EntityType = EntityType.PRIVATE_COMPANY,
        framework: FinancialFramework = FinancialFramework.GAAP_US,
        include_sections: Optional[Dict[str, bool]] = None
    ) -> Dict[str, str]:
        """
        Generate complete financial statement package.

        Args:
            context: Full context data for all components
            engagement_type: Type of engagement
            opinion_type: Type of opinion/report
            entity_type: Type of entity
            framework: Financial reporting framework
            include_sections: Which sections to include

        Returns:
            Dict with section names as keys and HTML content as values
        """
        default_sections = {
            'cover_letter': True,
            'accountants_report': True,
            'balance_sheet': True,
            'income_statement': True,
            'statement_of_cash_flows': True,
            'statement_of_changes_in_equity': True,
            'notes': True,
            'management_rep_letter': True
        }

        sections = {**default_sections, **(include_sections or {})}
        package = {}

        # Generate each section
        if sections.get('cover_letter'):
            package['cover_letter'] = self.report_generator.generate_cover_letter(
                context, engagement_type
            )

        if sections.get('accountants_report'):
            if engagement_type == EngagementType.COMPILATION:
                package['accountants_report'] = self.report_generator.generate_compilation_report(
                    context, opinion_type, framework
                )
            elif engagement_type == EngagementType.REVIEW:
                package['accountants_report'] = self.report_generator.generate_review_report(
                    context, opinion_type, framework
                )
            else:
                package['accountants_report'] = self.report_generator.generate_audit_report(
                    context, opinion_type, entity_type, framework
                )

        if sections.get('notes'):
            package['notes'] = self.report_generator.generate_notes_to_financial_statements(
                context, framework
            )

        if sections.get('management_rep_letter'):
            package['management_rep_letter'] = self.report_generator.generate_management_rep_letter(
                context, engagement_type
            )

        return package


# Singleton instance for easy access
compliance_report_generator = ComplianceReportGenerator()
complete_package_generator = CompleteReportPackageGenerator()
