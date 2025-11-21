# SOC 2 Type 2 Report Template

**REPORT OF INDEPENDENT SERVICE AUDITOR ON CONTROLS AT A SERVICE ORGANIZATION**

---

## SECTION I: INDEPENDENT SERVICE AUDITOR'S REPORT

### To Management of {{CLIENT_NAME}}:

#### Scope
We have examined {{CLIENT_NAME}}'s (the "Service Organization") description of its {{SERVICE_DESCRIPTION}} (the "System") as of {{POINT_IN_TIME_DATE}} and throughout the period from {{REVIEW_PERIOD_START}} to {{REVIEW_PERIOD_END}} (the "Review Period"), and the suitability of the design and operating effectiveness of the Service Organization's controls relevant to the {{TSC_CATEGORIES}} Trust Services Criteria (the "Applicable Trust Services Criteria") set forth in TSC Section 100, 2017 Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy (AICPA, Trust Services Criteria), to achieve the related control objectives stated in the description throughout that period.

#### Service Organization's Responsibilities
{{CLIENT_NAME}} is responsible for:

1. **Preparing the description and assertion**, including the completeness, accuracy, and method of presentation of the description and the assertion in Section II
2. **Providing the services** covered by the description
3. **Selecting the Applicable Trust Services Criteria** and **identifying the risks** that threaten the achievement of the Service Organization's service commitments and system requirements
4. **Designing, implementing, and documenting controls** to meet the Service Organization's service commitments and system requirements based on the Applicable Trust Services Criteria
5. **Ensuring the controls were operating effectively** throughout the Review Period

#### Service Auditor's Responsibilities
Our responsibility is to express an opinion on the Service Organization's description and on the suitability of the design and operating effectiveness of the controls to achieve the related control objectives stated in the Service Organization's description, based on our examination.

Our examination was conducted in accordance with attestation standards established by the American Institute of Certified Public Accountants (AICPA). Those standards require that we plan and perform our examination to obtain reasonable assurance about whether, in all material respects:

1. The description is presented in accordance with the description criteria in DC Section 200, 2018 Description Criteria for a Description of a Service Organization's System in a SOC 2 Report
2. The controls stated in the description were suitably designed throughout the Review Period to provide reasonable assurance that the Service Organization's service commitments and system requirements would be achieved based on the Applicable Trust Services Criteria, if the controls operated effectively and if subservice organizations and user entities applied the complementary controls assumed in the design of the Service Organization's controls throughout the Review Period
3. The controls stated in the description operated effectively throughout the Review Period to provide reasonable assurance that the Service Organization's service commitments and system requirements were achieved based on the Applicable Trust Services Criteria, if complementary subservice organization controls and complementary user entity controls assumed in the design of the Service Organization's controls operated effectively throughout the Review Period

Our examination included:
- Obtaining an understanding of the System and the Service Organization's control environment
- Assessing the risks that the Service Organization's service commitments and system requirements were not achieved based on the Applicable Trust Services Criteria
- Performing procedures to obtain evidence about whether the controls stated in the description were suitably designed to provide reasonable assurance that the Service Organization's service commitments and system requirements would be achieved based on the Applicable Trust Services Criteria
- Testing the operating effectiveness of those controls throughout the Review Period
- Evaluating the overall presentation of the description, including whether the description of the System fairly presents the System processed or used during the Review Period and whether the control objectives stated in the description are consistent with the Applicable Trust Services Criteria

We believe that the evidence we obtained is sufficient and appropriate to provide a reasonable basis for our opinion.

#### Inherent Limitations
The Service Organization's controls are designed to provide reasonable, but not absolute, assurance that the Service Organization's service commitments and system requirements were achieved based on the Applicable Trust Services Criteria. The Service Organization uses subservice organizations for certain aspects of its operations. This report does not extend to the controls of those subservice organizations. Because of their nature, controls may not prevent, or detect and correct, all matters that may be relevant to the Service Organization's service commitments and system requirements based on the Applicable Trust Services Criteria. Also, the projection to the future of any evaluation of the effectiveness of the controls is subject to the risk that controls may become inadequate because of changes in conditions or that the degree of compliance with the policies or procedures may deteriorate.

#### Opinion
In our opinion, in all material respects, based on the Applicable Trust Services Criteria:

a. The description fairly presents the {{SERVICE_DESCRIPTION}} that was designed and implemented throughout the period {{REVIEW_PERIOD_START}} to {{REVIEW_PERIOD_END}}.

b. The controls stated in the description were suitably designed throughout the period {{REVIEW_PERIOD_START}} to {{REVIEW_PERIOD_END}} to provide reasonable assurance that the Service Organization's service commitments and system requirements would be achieved based on the Applicable Trust Services Criteria, if the controls operated effectively and if subservice organizations and user entities applied the complementary controls assumed in the design of the Service Organization's controls throughout the Review Period.

c. The controls stated in the description operated effectively throughout the period {{REVIEW_PERIOD_START}} to {{REVIEW_PERIOD_END}} to provide reasonable assurance that the Service Organization's service commitments and system requirements were achieved based on the Applicable Trust Services Criteria, if complementary subservice organization controls and complementary user entity controls assumed in the design of the Service Organization's controls operated effectively throughout the Review Period.

#### Description of Trust Services Criteria

**Security:** Information and systems are protected against unauthorized access, unauthorized disclosure of information, and damage to systems that could compromise the availability, integrity, confidentiality, and privacy of information or systems and affect the entity's ability to meet its objectives.

{{#if TSC_AVAILABILITY}}
**Availability:** Information and systems are available for operation and use to meet the entity's objectives.
{{/if}}

{{#if TSC_PROCESSING_INTEGRITY}}
**Processing Integrity:** System processing is complete, valid, accurate, timely, and authorized to meet the entity's objectives.
{{/if}}

{{#if TSC_CONFIDENTIALITY}}
**Confidentiality:** Information designated as confidential is protected to meet the entity's objectives.
{{/if}}

{{#if TSC_PRIVACY}}
**Privacy:** Personal information is collected, used, retained, disclosed, and disposed of to meet the entity's objectives.
{{/if}}

#### Restricted Use
This report, including the description of tests of controls and results thereof in Section IV, is intended solely for the information and use of {{CLIENT_NAME}}, user entities of {{CLIENT_NAME}}'s {{SERVICE_DESCRIPTION}} during some or all of the period {{REVIEW_PERIOD_START}} to {{REVIEW_PERIOD_END}}, business partners of {{CLIENT_NAME}} subject to risks arising from interactions with the System, practitioners providing services to such user entities and business partners, prospective user entities and business partners, and regulators who have sufficient knowledge and understanding of the following:
- The nature of the service provided by the Service Organization
- How the Service Organization's System interacts with user entities, business partners, subservice organizations, and other parties
- Internal control and its limitations
- Complementary user entity controls and how those controls interact with the controls at the Service Organization to achieve the Service Organization's service commitments and system requirements
- User entity responsibilities and how they may affect the user entity's ability to effectively use the Service Organization's services
- The applicable trust services criteria

This report is not intended to be, and should not be, used by anyone other than these specified parties.

**{{FIRM_NAME}}**
{{CPA_NAME}}, CPA
{{CPA_LICENSE_NUMBER}}

{{REPORT_DATE}}

---

## SECTION II: {{CLIENT_NAME}}'S MANAGEMENT ASSERTION

### Management's Assertion

We, as management of {{CLIENT_NAME}}, are responsible for:

1. Designing, implementing, operating, and maintaining effective controls within the {{SERVICE_DESCRIPTION}} (the "System") to provide reasonable assurance that {{CLIENT_NAME}}'s service commitments and system requirements were achieved based on the {{TSC_CATEGORIES}} Trust Services Criteria ("Applicable Trust Services Criteria") set forth in TSC Section 100, 2017 Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy (AICPA, Trust Services Criteria)

2. Selecting the Applicable Trust Services Criteria and identifying the risks that threaten the achievement of {{CLIENT_NAME}}'s service commitments and system requirements

3. Designing, implementing, and documenting controls to meet {{CLIENT_NAME}}'s service commitments and system requirements based on the Applicable Trust Services Criteria

4. Presenting the attached description of the System, including:
   - Identification of the aspects of the Applicable Trust Services Criteria that are covered by the System
   - Disclosure of the related risks that threaten the achievement of {{CLIENT_NAME}}'s service commitments and system requirements
   - The controls intended to address those risks
   - The complementary user entity controls assumed in the design of the controls

We confirm, to the best of our knowledge and belief, that:

a. The attached description fairly presents the {{SERVICE_DESCRIPTION}} made available to user entities of the System during the period {{REVIEW_PERIOD_START}} to {{REVIEW_PERIOD_END}} (the "Review Period"). The criteria we used in making this assertion were that the attached description:
   1. Presents how the System was designed and implemented to meet {{CLIENT_NAME}}'s service commitments and system requirements based on the Applicable Trust Services Criteria, including:
      - The types of services provided
      - The components of the System used to provide the services, which are:
        * Infrastructure
        * Software
        * People
        * Procedures
        * Data
      - The boundaries of the System
      - How the System captures and addresses significant events and conditions relevant to {{CLIENT_NAME}}'s service commitments and system requirements
      - The Applicable Trust Services Criteria and related control objectives
      - The complementary user entity controls assumed in the design of {{CLIENT_NAME}}'s controls
      - Other aspects of {{CLIENT_NAME}}'s control environment, risk assessment process, information and communication systems (including related business processes), control activities, and monitoring controls that are relevant to the Applicable Trust Services Criteria

   2. Includes relevant details about changes to the System during the Review Period

   3. Does not omit or distort information relevant to the System while acknowledging that the description is prepared to meet the common needs of a broad range of users and may not include every aspect of the System that each individual user may consider important in its particular environment

b. The controls stated in the description were suitably designed throughout the Review Period to provide reasonable assurance that {{CLIENT_NAME}}'s service commitments and system requirements would be achieved based on the Applicable Trust Services Criteria, if:
   - The controls operated effectively throughout the Review Period
   - Subservice organizations and user entities applied the complementary controls assumed in the design of {{CLIENT_NAME}}'s controls throughout the Review Period

c. The controls stated in the description operated effectively throughout the Review Period to provide reasonable assurance that {{CLIENT_NAME}}'s service commitments and system requirements were achieved based on the Applicable Trust Services Criteria, if complementary subservice organization controls and complementary user entity controls assumed in the design of {{CLIENT_NAME}}'s controls operated effectively throughout the Review Period.

**{{CLIENT_NAME}}**
{{MANAGEMENT_NAME}}, {{MANAGEMENT_TITLE}}
{{ASSERTION_DATE}}

---

## SECTION III: DESCRIPTION OF {{CLIENT_NAME}}'S SYSTEM

### A. Overview of the Service Organization

**Company Background:**
{{COMPANY_BACKGROUND}}

**Services Provided:**
{{SERVICE_DESCRIPTION_DETAIL}}

**Principal Service Commitments:**
{{PRINCIPAL_SERVICE_COMMITMENTS}}

**System Requirements:**
{{SYSTEM_REQUIREMENTS}}

**Trust Services Categories Covered:**
- **Security** (CC1-CC9) [Required]
{{#if TSC_AVAILABILITY}}- **Availability** (A1.1-A1.3){{/if}}
{{#if TSC_PROCESSING_INTEGRITY}}- **Processing Integrity** (PI1.1-PI1.5){{/if}}
{{#if TSC_CONFIDENTIALITY}}- **Confidentiality** (C1.1-C1.2){{/if}}
{{#if TSC_PRIVACY}}- **Privacy** (P1.1-P8.1){{/if}}

**Review Period:** {{REVIEW_PERIOD_START}} to {{REVIEW_PERIOD_END}}

### B. System Description (per SOC 2 Description Criteria 2018)

#### 1. Principal Service Users

{{PRINCIPAL_SERVICE_USERS}}

#### 2. System Boundaries

**In-Scope Components:**
{{IN_SCOPE_COMPONENTS}}

**Out-of-Scope Components:**
{{OUT_OF_SCOPE_COMPONENTS}}

**Geographic Boundaries:**
{{GEOGRAPHIC_BOUNDARIES}}

#### 3. Components of the System

##### Infrastructure

**Physical Infrastructure:**
{{PHYSICAL_INFRASTRUCTURE}}

**Data Centers:**
{{DATA_CENTERS}}

**Network Architecture:**
{{NETWORK_ARCHITECTURE}}

**Hosting Environment:**
{{HOSTING_ENVIRONMENT}}

##### Software

**Applications:**
{{APPLICATION_LIST}}

**Database Systems:**
{{DATABASE_SYSTEMS}}

**Operating Systems:**
{{OPERATING_SYSTEMS}}

**Third-Party Software:**
{{THIRD_PARTY_SOFTWARE}}

##### People

**Organizational Structure:**
{{ORGANIZATIONAL_STRUCTURE}}

**Key Roles and Responsibilities:**
{{ROLES_AND_RESPONSIBILITIES}}

**Segregation of Duties:**
{{SEGREGATION_OF_DUTIES}}

**Training and Awareness:**
{{TRAINING_PROGRAMS}}

##### Procedures

**Standard Operating Procedures:**
{{STANDARD_PROCEDURES}}

**Change Management:**
{{CHANGE_MANAGEMENT}}

**Incident Response:**
{{INCIDENT_RESPONSE}}

**Business Continuity:**
{{BUSINESS_CONTINUITY}}

##### Data

**Types of Data Processed:**
{{DATA_TYPES}}

**Data Classification:**
{{DATA_CLASSIFICATION}}

**Data Flows:**
{{DATA_FLOWS}}

**Data Retention and Disposal:**
{{DATA_RETENTION}}

### C. Control Objectives and Related Controls

#### Common Criteria (CC) - Security

##### CC1: Control Environment

###### CC1.1: Integrity and Ethical Values
**Control:** {{CC1_1_CONTROL}}
**Implementation:** {{CC1_1_IMPLEMENTATION}}

###### CC1.2: Board of Directors
**Control:** {{CC1_2_CONTROL}}
**Implementation:** {{CC1_2_IMPLEMENTATION}}

*[Continue for CC1.3-CC1.5]*

##### CC2: Communication and Information

*[CC2.1-CC2.3]*

##### CC3: Risk Assessment

*[CC3.1-CC3.4]*

##### CC4: Monitoring Activities

*[CC4.1-CC4.2]*

##### CC5: Control Activities

*[CC5.1-CC5.3]*

##### CC6: Logical and Physical Access Controls

*[CC6.1-CC6.8]*

##### CC7: System Operations

*[CC7.1-CC7.5]*

##### CC8: Change Management

*[CC8.1]*

##### CC9: Risk Mitigation

*[CC9.1-CC9.2]*

{{#if TSC_AVAILABILITY}}
#### Availability Criteria (A)

##### A1: Availability
###### A1.1: Performance
**Control:** {{A1_1_CONTROL}}

###### A1.2: Recovery
**Control:** {{A1_2_CONTROL}}

###### A1.3: Monitoring
**Control:** {{A1_3_CONTROL}}
{{/if}}

{{#if TSC_PROCESSING_INTEGRITY}}
#### Processing Integrity Criteria (PI)

##### PI1: Processing Integrity
*[PI1.1-PI1.5]*
{{/if}}

{{#if TSC_CONFIDENTIALITY}}
#### Confidentiality Criteria (C)

##### C1: Confidentiality
*[C1.1-C1.2]*
{{/if}}

{{#if TSC_PRIVACY}}
#### Privacy Criteria (P)

##### P1: Collection and Retention
*[P1.1-P1.2]*

##### P2: Use and Disclosure
*[P2.1-P2.2]*

##### P3-P8: Access, Disclosure, Quality, Monitoring, etc.
*[P3.1-P8.1]*
{{/if}}

### D. Complementary User Entity Controls (CUECs)

{{CLIENT_NAME}}'s System was designed with the assumption that certain controls would be implemented by user entities. User entities should consider these complementary user entity controls in designing their own internal control structures:

**CUEC-1:** {{CUEC_1_DESCRIPTION}}
**TSC Criteria:** {{CUEC_1_CRITERIA}}

**CUEC-2:** {{CUEC_2_DESCRIPTION}}
**TSC Criteria:** {{CUEC_2_CRITERIA}}

*[Repeat for each CUEC]*

### E. Subservice Organizations

{{#if SUBSERVICE_ORGS_USED}}
{{CLIENT_NAME}} uses the following subservice organizations as part of its System:

#### Subservice Organization: {{SUBSERVICE_ORG_1_NAME}}

**Services Provided:** {{SUBSERVICE_1_SERVICES}}
**Treatment:** {{SUBSERVICE_1_TREATMENT}}

{{#if SUBSERVICE_1_CARVE_OUT}}
**Rationale for Carve-Out:**
{{SUBSERVICE_1_CARVE_OUT_RATIONALE}}

**Complementary Subservice Organization Controls (CSOCs):**
- {{CSOC_1}}
- {{CSOC_2}}

**Monitoring Procedures:**
{{SUBSERVICE_1_MONITORING}}
{{/if}}

{{#if SUBSERVICE_1_INCLUSIVE}}
**Inclusive Treatment:**
Controls at {{SUBSERVICE_ORG_1_NAME}} are included in the scope of this report. See Section III.C for details.
{{/if}}

*[Repeat for each subservice organization]*
{{/if}}

---

## SECTION IV: TESTS OF CONTROLS AND RESULTS

### A. Testing Methodology

Our examination was conducted in accordance with attestation standards established by the AICPA. We performed the following procedures:

1. **Inquiry:** Interviewed personnel responsible for control execution
2. **Observation:** Observed control execution in real-time
3. **Inspection:** Reviewed documentation and evidence
4. **Reperformance:** Independently executed controls to verify results

For the {{REVIEW_PERIOD_LENGTH}}-month Review Period, we:
- Tested operating effectiveness of manual controls using {{SAMPLING_METHOD}} sampling
- Tested automated controls by verifying design, implementation, and operating effectiveness
- Tested general IT controls (GITC) that support automated application controls

### B. Control Tests and Results by Trust Services Criteria

#### Common Criteria (CC) - Security

##### CC1.1: {{CC1_1_CONTROL_NAME}}

**Control Description:**
{{CC1_1_FULL_DESCRIPTION}}

**Test Performed:**
{{CC1_1_TEST_DESCRIPTION}}

**Sample Size:** {{CC1_1_SAMPLE_SIZE}}
**Sampling Method:** {{CC1_1_SAMPLING_METHOD}}
**Population:** {{CC1_1_POPULATION}}

**Test Results:**
{{CC1_1_RESULTS}}

**Exceptions:** {{CC1_1_EXCEPTIONS}}

**Conclusion:** {{CC1_1_CONCLUSION}}

*[Repeat for each control tested across all applicable TSC categories]*

### C. Summary of Test Results

| TSC Criteria | Control | Tests Performed | Sample Size | Exceptions | Result |
|--------------|---------|-----------------|-------------|------------|--------|
| CC1.1 | {{CONTROL_1}} | {{TEST_COUNT_1}} | {{SAMPLE_1}} | {{EXC_1}} | {{RESULT_1}} |
| CC1.2 | {{CONTROL_2}} | {{TEST_COUNT_2}} | {{SAMPLE_2}} | {{EXC_2}} | {{RESULT_2}} |
| ... | ... | ... | ... | ... | ... |

### D. Other Information

#### Changes to the System

{{#if SYSTEM_CHANGES}}
The following significant changes occurred during the Review Period:

**Change 1:** {{CHANGE_1_DESCRIPTION}}
**Date:** {{CHANGE_1_DATE}}
**Impact:** {{CHANGE_1_IMPACT}}

*[Repeat for each significant change]*
{{else}}
No significant changes to the System occurred during the Review Period.
{{/if}}

#### Incidents and Breaches

{{#if INCIDENTS}}
The following security incidents occurred during the Review Period:

**Incident 1:** {{INCIDENT_1_DESCRIPTION}}
**Date:** {{INCIDENT_1_DATE}}
**Impact:** {{INCIDENT_1_IMPACT}}
**Resolution:** {{INCIDENT_1_RESOLUTION}}

*[Repeat for each incident]*
{{else}}
No material security incidents occurred during the Review Period.
{{/if}}

---

**WATERMARK: {{FIRM_NAME}} - Restricted Distribution**
**Report Date:** {{REPORT_DATE}}
**Engagement ID:** {{ENGAGEMENT_ID}}
**Page {{PAGE_NUMBER}} of {{TOTAL_PAGES}}**
