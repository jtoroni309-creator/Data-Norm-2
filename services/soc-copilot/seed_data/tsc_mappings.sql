-- SOC 2 Trust Services Criteria Mappings
-- Based on AICPA TSC 2017 with 2022 Points of Focus updates

-- This seed data provides the foundation for SOC 2 control objectives
-- based on the Trust Services Criteria framework

SET search_path TO soc_copilot, public;

-- ============================================================================
-- COMMON CRITERIA (CC) - SECURITY (Required for all SOC 2 engagements)
-- ============================================================================

-- CC1: Control Environment
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC1.1', 'COSO Principle 1: Integrity and Ethical Values',
 'The entity demonstrates a commitment to integrity and ethical values.',
 'SECURITY', 'CC1.1',
 ARRAY[
     'Board of directors oversight',
     'Standards of conduct and accountability',
     'Financial reporting pressures evaluation',
     'Incentive and reward programs alignment'
 ], true),

(uuid_generate_v4(), NULL, 'CC1.2', 'COSO Principle 2: Board of Directors',
 'The board of directors demonstrates independence from management and exercises oversight of the development and performance of internal control.',
 'SECURITY', 'CC1.2',
 ARRAY[
     'Board independence from management',
     'Oversight of system of internal control',
     'Oversight of management design and implementation',
     'Authority to execute oversight responsibilities'
 ], true),

(uuid_generate_v4(), NULL, 'CC1.3', 'COSO Principle 3: Organizational Structure',
 'Management establishes, with board oversight, structures, reporting lines, and appropriate authorities and responsibilities in the pursuit of objectives.',
 'SECURITY', 'CC1.3',
 ARRAY[
     'Organizational structure appropriate for objectives',
     'Authority and responsibility assignment',
     'Reporting lines established',
     'Service delivery models and third-party relationships'
 ], true),

(uuid_generate_v4(), NULL, 'CC1.4', 'COSO Principle 4: Competence',
 'The entity demonstrates a commitment to attract, develop, and retain competent individuals in alignment with objectives.',
 'SECURITY', 'CC1.4',
 ARRAY[
     'Competence requirements policies and practices',
     'Board and management competence evaluation',
     'Knowledge, skills, and abilities development',
     'Succession planning'
 ], true),

(uuid_generate_v4(), NULL, 'CC1.5', 'COSO Principle 5: Accountability',
 'The entity holds individuals accountable for their internal control responsibilities in the pursuit of objectives.',
 'SECURITY', 'CC1.5',
 ARRAY[
     'Performance measures and incentives established',
     'Accountability for internal control responsibilities',
     'Excessive pressures evaluation',
     'Rewards and corrective actions'
 ], true);

-- CC2: Communication and Information
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC2.1', 'COSO Principle 13: Relevant Information',
 'The entity obtains or generates and uses relevant, quality information to support the functioning of internal control.',
 'SECURITY', 'CC2.1',
 ARRAY[
     'Information system identification and development',
     'Quality information sources (internal and external)',
     'Data processing relevant to objectives',
     'Information system maintenance'
 ], true),

(uuid_generate_v4(), NULL, 'CC2.2', 'COSO Principle 14: Internal Communication',
 'The entity internally communicates information, including objectives and responsibilities for internal control, necessary to support the functioning of internal control.',
 'SECURITY', 'CC2.2',
 ARRAY[
     'Internal control communication methods',
     'Communication with board of directors',
     'Separate communication lines (e.g., whistleblower)',
     'Commitment refresh mechanisms'
 ], true),

(uuid_generate_v4(), NULL, 'CC2.3', 'COSO Principle 15: External Communication',
 'The entity communicates with external parties regarding matters affecting the functioning of internal control.',
 'SECURITY', 'CC2.3',
 ARRAY[
     'External stakeholder communication',
     'Inbound communications from external parties',
     'Board communication with external parties',
     'Regulators and standard-setters communication'
 ], true);

-- CC3: Risk Assessment
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC3.1', 'COSO Principle 6: Objectives Specification',
 'The entity specifies objectives with sufficient clarity to enable the identification and assessment of risks relating to objectives.',
 'SECURITY', 'CC3.1',
 ARRAY[
     'Service commitments reflected in objectives',
     'System requirements reflected in objectives',
     'Tolerance for risk established',
     'Subservice organization objectives consideration'
 ], true),

(uuid_generate_v4(), NULL, 'CC3.2', 'COSO Principle 7: Risk Identification',
 'The entity identifies risks to the achievement of its objectives across the entity and analyzes risks as a basis for determining how the risks should be managed.',
 'SECURITY', 'CC3.2',
 ARRAY[
     'Comprehensive risk identification',
     'Internal and external risk factors',
     'Risk analysis and significance assessment',
     'Risk response selection'
 ], true),

(uuid_generate_v4(), NULL, 'CC3.3', 'COSO Principle 8: Fraud Risk',
 'The entity considers the potential for fraud in assessing risks to the achievement of objectives.',
 'SECURITY', 'CC3.3',
 ARRAY[
     'Fraud risk factor consideration',
     'Fraud risk assessment',
     'Fraud risk response identification'
 ], true),

(uuid_generate_v4(), NULL, 'CC3.4', 'COSO Principle 9: Change Identification',
 'The entity identifies and assesses changes that could significantly impact the system of internal control.',
 'SECURITY', 'CC3.4',
 ARRAY[
     'Environmental changes assessment',
     'Business model changes',
     'Leadership changes impact',
     'System changes (subservice organizations, technology)'
 ], true);

-- CC4: Monitoring Activities
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC4.1', 'COSO Principle 16: Ongoing and Separate Evaluations',
 'The entity selects, develops, and performs ongoing and/or separate evaluations to ascertain whether the components of internal control are present and functioning.',
 'SECURITY', 'CC4.1',
 ARRAY[
     'Ongoing and separate evaluations blend',
     'Baseline understanding establishment',
     'Objectivity and competence of evaluators',
     'Evaluation results documentation and remediation'
 ], true),

(uuid_generate_v4(), NULL, 'CC4.2', 'COSO Principle 17: Deficiency Evaluation',
 'The entity evaluates and communicates internal control deficiencies in a timely manner to those parties responsible for taking corrective action, including senior management and the board of directors, as appropriate.',
 'SECURITY', 'CC4.2',
 ARRAY[
     'Deficiency assessment processes',
     'Severity and priority determination',
     'Corrective actions communication',
     'Monitoring of corrective actions'
 ], true);

-- CC5: Control Activities
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC5.1', 'COSO Principle 10: Control Activities Selection',
 'The entity selects and develops control activities that contribute to the mitigation of risks to the achievement of objectives to acceptable levels.',
 'SECURITY', 'CC5.1',
 ARRAY[
     'Risk mitigation integration',
     'Entity-specific considerations',
     'Business process level integration',
     'Technology-based controls where appropriate'
 ], true),

(uuid_generate_v4(), NULL, 'CC5.2', 'COSO Principle 11: Technology Controls',
 'The entity also selects and develops general control activities over technology to support the achievement of objectives.',
 'SECURITY', 'CC5.2',
 ARRAY[
     'Technology infrastructure design and implementation',
     'Security management process',
     'Technology acquisition and maintenance'
 ], true),

(uuid_generate_v4(), NULL, 'CC5.3', 'COSO Principle 12: Policies and Procedures',
 'The entity deploys control activities through policies that establish what is expected and in procedures that put policies into action.',
 'SECURITY', 'CC5.3',
 ARRAY[
     'Policies and procedures establishment and review',
     'Accountability assignment for execution',
     'Performance in a timely manner',
     'Appropriate action on identified deficiencies'
 ], true);

-- CC6: Logical and Physical Access Controls
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC6.1', 'Logical Access Controls',
 'The entity implements logical access security software, infrastructure, and architectures over protected information assets to protect them from security events to meet the entity's objectives.',
 'SECURITY', 'CC6.1',
 ARRAY[
     'Identification and authentication of users',
     'Access rights and privileges',
     'Segregation of duties in security-relevant activities',
     'Authorized access restrictions to protect assets'
 ], true),

(uuid_generate_v4(), NULL, 'CC6.2', 'Provisioning and Modification',
 'Prior to issuing system credentials and granting system access, the entity registers and authorizes new internal and external users whose access is administered by the entity.',
 'SECURITY', 'CC6.2',
 ARRAY[
     'User registration and authorization',
     'Access modification and termination',
     'Credentials delivery mechanisms',
     'Periodic review of access rights'
 ], true),

(uuid_generate_v4(), NULL, 'CC6.3', 'User Access Removal',
 'The entity removes access to the system for users whose access is no longer authorized.',
 'SECURITY', 'CC6.3',
 ARRAY[
     'Access removal procedures',
     'Timely deprovisioning of terminated users',
     'Asset recovery (laptops, tokens)',
     'Logical access termination verification'
 ], true),

(uuid_generate_v4(), NULL, 'CC6.4', 'Access Review',
 'The entity restricts physical access to facilities and protected information assets to authorized personnel to meet the entity's objectives.',
 'SECURITY', 'CC6.4',
 ARRAY[
     'Physical access restrictions',
     'Visitor access controls',
     'Physical access device management',
     'Environmental threat protection'
 ], true),

(uuid_generate_v4(), NULL, 'CC6.5', 'Remote Access',
 'The entity authenticates users for remote access to the system to meet the entity's objectives.',
 'SECURITY', 'CC6.5',
 ARRAY[
     'Multi-factor authentication for remote access',
     'VPN and encrypted communications',
     'Remote access session management',
     'Remote access monitoring'
 ], true),

(uuid_generate_v4(), NULL, 'CC6.6', 'Encryption',
 'The entity uses encryption to protect data and system components to meet the entity's objectives.',
 'SECURITY', 'CC6.6',
 ARRAY[
     'Data in transit encryption (TLS 1.2+)',
     'Data at rest encryption',
     'Encryption key management',
     'Cryptographic algorithm selection'
 ], true),

(uuid_generate_v4(), NULL, 'CC6.7', 'Transmission Integrity',
 'The entity restricts the transmission, movement, and removal of information to authorized internal and external users and processes, and protects it during transmission, movement, or removal to meet the entity's objectives.',
 'SECURITY', 'CC6.7',
 ARRAY[
     'Transmission security policies',
     'Data loss prevention controls',
     'Authorized transmission methods',
     'Transmission monitoring and logging'
 ], true),

(uuid_generate_v4(), NULL, 'CC6.8', 'Asset Management',
 'The entity implements controls to prevent unauthorized access to system resources to meet the entity's objectives.',
 'SECURITY', 'CC6.8',
 ARRAY[
     'Asset inventory management',
     'Asset classification and handling',
     'Media sanitization and disposal',
     'Asset tracking and accountability'
 ], true);

-- CC7: System Operations
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC7.1', 'Security Event Detection',
 'To meet its objectives, the entity uses detection and monitoring procedures to identify anomalies and indicators of compromise.',
 'SECURITY', 'CC7.1',
 ARRAY[
     'SIEM or equivalent monitoring tools',
     'Log aggregation and analysis',
     'Anomaly detection mechanisms',
     'Real-time alerting for security events'
 ], true),

(uuid_generate_v4(), NULL, 'CC7.2', 'Incident Response',
 'The entity monitors system components and the operation of those components for anomalies that are indicative of malicious acts, natural disasters, and errors affecting the entity's ability to meet its objectives; anomalies are analyzed to determine whether they represent security events.',
 'SECURITY', 'CC7.2',
 ARRAY[
     'Incident response plan documented',
     'Incident triage and classification',
     'Containment and eradication procedures',
     'Post-incident review and lessons learned'
 ], true),

(uuid_generate_v4(), NULL, 'CC7.3', 'System Monitoring',
 'The entity evaluates security events to determine whether they could or have resulted in a failure of the entity to meet its objectives (security incidents) and, if so, takes actions to prevent or address such failures.',
 'SECURITY', 'CC7.3',
 ARRAY[
     'Capacity and performance monitoring',
     'Threshold-based alerting',
     'Resource utilization tracking',
     'Trend analysis'
 ], true),

(uuid_generate_v4(), NULL, 'CC7.4', 'Incident Response Communication',
 'The entity responds to identified security incidents by executing a defined incident response program to understand, contain, remediate, and communicate security incidents, as appropriate.',
 'SECURITY', 'CC7.4',
 ARRAY[
     'Stakeholder notification procedures',
     'Regulatory reporting obligations',
     'Customer breach notification',
     'Internal escalation paths'
 ], true),

(uuid_generate_v4(), NULL, 'CC7.5', 'Environmental Protections',
 'The entity identifies, develops, and implements activities to recover from identified security incidents.',
 'SECURITY', 'CC7.5',
 ARRAY[
     'Fire suppression systems',
     'Temperature and humidity controls',
     'Power supply redundancy (UPS, generators)',
     'Environmental monitoring'
 ], true);

-- CC8: Change Management
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC8.1', 'Change Management',
 'The entity authorizes, designs, develops or acquires, configures, documents, tests, approves, and implements changes to infrastructure, data, software, and procedures to meet its objectives.',
 'SECURITY', 'CC8.1',
 ARRAY[
     'Change request and approval process',
     'Change Advisory Board (CAB) or equivalent',
     'Testing in non-production environments',
     'Emergency change procedures',
     'Post-implementation review',
     'Change documentation and audit trail'
 ], true);

-- CC9: Risk Mitigation
INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'CC9.1', 'Vendor Management',
 'The entity identifies, selects, and manages business partners, outsourced service providers, and other parties from whom the entity obtains infrastructure, software, or services as part of its system to support the achievement of the entity's objectives.',
 'SECURITY', 'CC9.1',
 ARRAY[
     'Vendor risk assessment prior to engagement',
     'Vendor contract security requirements',
     'Ongoing vendor performance monitoring',
     'Vendor access controls and termination',
     'Subservice organization SOC report review'
 ], true),

(uuid_generate_v4(), NULL, 'CC9.2', 'Business Continuity and Disaster Recovery',
 'The entity implements activities to recover from unexpected events that threaten the achievement of the entity's objectives.',
 'SECURITY', 'CC9.2',
 ARRAY[
     'Business continuity plan (BCP) documented',
     'Disaster recovery plan (DRP) documented',
     'Recovery Time Objective (RTO) defined',
     'Recovery Point Objective (RPO) defined',
     'Annual BCP/DRP testing',
     'Backup retention and restoration procedures'
 ], true);

-- ============================================================================
-- AVAILABILITY CRITERIA (A) - Optional
-- ============================================================================

INSERT INTO control_objectives (
    id, engagement_id, objective_code, objective_name, objective_description,
    tsc_category, tsc_criteria, points_of_focus_2022, is_active
) VALUES
(uuid_generate_v4(), NULL, 'A1.1', 'Availability Performance',
 'The entity maintains, monitors, and evaluates current processing capacity and use of system components (infrastructure, data, and software) to manage capacity demand and to enable the implementation of additional capacity to help meet its objectives.',
 'AVAILABILITY', 'A1.1',
 ARRAY[
     'Capacity planning processes',
     'Resource utilization monitoring',
     'Performance benchmarking',
     'Scalability testing'
 ], true),

(uuid_generate_v4(), NULL, 'A1.2', 'Environmental Protections for Availability',
 'The entity authorizes, designs, develops or acquires, implements, operates, approves, maintains, and monitors environmental protections, software, data backup processes, and recovery infrastructure to meet its objectives.',
 'AVAILABILITY', 'A1.2',
 ARRAY[
     'Redundant systems and failover mechanisms',
     'Backup frequency and retention',
     'Recovery testing procedures',
     'Environmental controls (power, cooling)'
 ], true),

(uuid_generate_v4(), NULL, 'A1.3', 'Recovery and Failover',
 'The entity provides for the recovery of systems, data, and business processes in the event of a disruption to meet its objectives.',
 'AVAILABILITY', 'A1.3',
 ARRAY[
     'Documented recovery procedures',
     'RTO and RPO achievement validation',
     'Alternate processing facilities',
     'Annual disaster recovery testing'
 ], true);

COMMIT;
