/**
 * SOC Engagement Workspace
 * Comprehensive SOC 1 & SOC 2 audit workspace with all phases
 * Supports SSAE 18 / AT-C 105, 205, 320 + Trust Services Criteria
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield,
  ArrowLeft,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileText,
  Upload,
  Download,
  Settings,
  Users,
  Target,
  ClipboardList,
  FileCheck,
  PenTool,
  Lock,
  Server,
  Database,
  UserCheck,
  ChevronRight,
  Plus,
  Edit,
  Trash2,
  Eye,
  X,
  Send,
  MessageSquare,
  AlertCircle,
  Calendar,
  Building2,
  Sparkles,
  RefreshCw,
  MoreVertical,
  Check,
  XCircle,
} from 'lucide-react';
import { socCopilotService, SOCEngagement, ControlObjectiveCreate, ControlCreate, TestPlanCreate } from '../services/soc-copilot.service';
import toast from 'react-hot-toast';

// Trust Services Criteria mapping
const TSC_CRITERIA = {
  SECURITY: {
    name: 'Security',
    icon: Shield,
    color: 'blue',
    criteria: [
      { code: 'CC1.1', name: 'COSO Principle 1', description: 'Demonstrates commitment to integrity and ethical values' },
      { code: 'CC1.2', name: 'COSO Principle 2', description: 'Board independence and oversight' },
      { code: 'CC1.3', name: 'COSO Principle 3', description: 'Management establishes structures, reporting lines, and authorities' },
      { code: 'CC1.4', name: 'COSO Principle 4', description: 'Commitment to attract, develop, and retain competent individuals' },
      { code: 'CC1.5', name: 'COSO Principle 5', description: 'Holds individuals accountable for internal control responsibilities' },
      { code: 'CC2.1', name: 'COSO Principle 13', description: 'Obtains or generates relevant, quality information' },
      { code: 'CC2.2', name: 'COSO Principle 14', description: 'Internally communicates information' },
      { code: 'CC2.3', name: 'COSO Principle 15', description: 'Communicates with external parties' },
      { code: 'CC3.1', name: 'COSO Principle 6', description: 'Specifies suitable risk assessment objectives' },
      { code: 'CC3.2', name: 'COSO Principle 7', description: 'Identifies and analyzes risks' },
      { code: 'CC3.3', name: 'COSO Principle 8', description: 'Assesses fraud risk' },
      { code: 'CC3.4', name: 'COSO Principle 9', description: 'Identifies and assesses significant changes' },
      { code: 'CC4.1', name: 'COSO Principle 16', description: 'Selects, develops, and performs ongoing evaluations' },
      { code: 'CC4.2', name: 'COSO Principle 17', description: 'Evaluates and communicates deficiencies' },
      { code: 'CC5.1', name: 'COSO Principle 10', description: 'Selects and develops control activities' },
      { code: 'CC5.2', name: 'COSO Principle 11', description: 'Selects and develops technology controls' },
      { code: 'CC5.3', name: 'COSO Principle 12', description: 'Deploys policies and procedures' },
      { code: 'CC6.1', name: 'Logical Access', description: 'Implements logical access security software' },
      { code: 'CC6.2', name: 'Authentication', description: 'Prior to registration, users are authenticated' },
      { code: 'CC6.3', name: 'Authorization', description: 'Manages access credentials' },
      { code: 'CC6.4', name: 'Access Restrictions', description: 'Restricts physical access to facilities and assets' },
      { code: 'CC6.5', name: 'Access Removal', description: 'Manages removal of access when terminated' },
      { code: 'CC6.6', name: 'External Threats', description: 'Implements controls against external threats' },
      { code: 'CC6.7', name: 'Data Transmission', description: 'Restricts transmission, movement, and removal of data' },
      { code: 'CC6.8', name: 'Malicious Software', description: 'Implements controls to prevent malicious software' },
      { code: 'CC7.1', name: 'Intrusion Detection', description: 'Detects and monitors security events' },
      { code: 'CC7.2', name: 'Anomaly Detection', description: 'Monitors system components for anomalies' },
      { code: 'CC7.3', name: 'Security Evaluation', description: 'Evaluates security events to determine incidents' },
      { code: 'CC7.4', name: 'Incident Response', description: 'Responds to identified security incidents' },
      { code: 'CC7.5', name: 'Incident Recovery', description: 'Identifies and recovers from security incidents' },
      { code: 'CC8.1', name: 'Change Management', description: 'Authorizes, designs, develops, and implements changes' },
      { code: 'CC9.1', name: 'Risk Mitigation', description: 'Identifies, selects, and develops risk mitigation activities' },
      { code: 'CC9.2', name: 'Vendor Management', description: 'Assesses and manages risks from vendors and partners' },
    ],
  },
  AVAILABILITY: {
    name: 'Availability',
    icon: Server,
    color: 'green',
    criteria: [
      { code: 'A1.1', name: 'Capacity Management', description: 'Maintains, monitors, and evaluates current processing capacity' },
      { code: 'A1.2', name: 'Recovery Planning', description: 'Authorizes, designs, develops, and implements recovery procedures' },
      { code: 'A1.3', name: 'Recovery Testing', description: 'Tests recovery plan procedures periodically' },
    ],
  },
  PROCESSING_INTEGRITY: {
    name: 'Processing Integrity',
    icon: Database,
    color: 'purple',
    criteria: [
      { code: 'PI1.1', name: 'Processing Accuracy', description: 'Input data integrity from authorized sources' },
      { code: 'PI1.2', name: 'Processing Completeness', description: 'System processing is complete, accurate, and timely' },
      { code: 'PI1.3', name: 'Output Delivery', description: 'Output is complete and distributed to intended parties' },
      { code: 'PI1.4', name: 'Processing Validation', description: 'Processing is audited and validated' },
      { code: 'PI1.5', name: 'Error Correction', description: 'Errors are identified and corrected timely' },
    ],
  },
  CONFIDENTIALITY: {
    name: 'Confidentiality',
    icon: Lock,
    color: 'amber',
    criteria: [
      { code: 'C1.1', name: 'Data Classification', description: 'Identifies and maintains confidential information' },
      { code: 'C1.2', name: 'Data Disposal', description: 'Disposes of confidential information in a secure manner' },
    ],
  },
  PRIVACY: {
    name: 'Privacy',
    icon: UserCheck,
    color: 'pink',
    criteria: [
      { code: 'P1.1', name: 'Privacy Notice', description: 'Provides notice about privacy practices' },
      { code: 'P2.1', name: 'Choice and Consent', description: 'Communicates choices and obtains consent' },
      { code: 'P3.1', name: 'Collection Limitation', description: 'Collects personal information by defined objectives' },
      { code: 'P3.2', name: 'Collection from Third Parties', description: 'Informs data subjects about third-party sources' },
      { code: 'P4.1', name: 'Use and Retention', description: 'Limits use and retains data only as necessary' },
      { code: 'P4.2', name: 'Retention Period', description: 'Retains data for specified period only' },
      { code: 'P4.3', name: 'Secure Disposal', description: 'Securely disposes of personal information' },
      { code: 'P5.1', name: 'Access Rights', description: 'Grants data subjects access to their information' },
      { code: 'P5.2', name: 'Correction Rights', description: 'Permits data subjects to update their information' },
      { code: 'P6.1', name: 'Disclosure Limitation', description: 'Discloses data only to authorized parties' },
      { code: 'P6.2', name: 'Authorized Disclosure', description: 'Creates and retains disclosure authorization records' },
      { code: 'P6.3', name: 'Third-Party Compliance', description: 'Third parties handle data in accordance with policies' },
      { code: 'P6.4', name: 'Consent for New Purposes', description: 'Obtains consent for new disclosure purposes' },
      { code: 'P6.5', name: 'Unauthorized Disclosure', description: 'Unauthorized disclosures are identified and addressed' },
      { code: 'P6.6', name: 'Notification of Disclosure', description: 'Data subjects are notified of disclosures' },
      { code: 'P6.7', name: 'Disclosure Restrictions', description: 'Data subjects can restrict disclosure' },
      { code: 'P7.1', name: 'Data Quality', description: 'Collects and maintains accurate, complete information' },
      { code: 'P8.1', name: 'Complaints and Disputes', description: 'Receives and addresses privacy complaints' },
    ],
  },
};

// PBC (Provided by Client) request list template for SOC 2
const PBC_TEMPLATE = [
  // Governance / Policies
  { id: 'pbc-1', category: 'Governance', name: 'Information Security Policy', description: 'Current approved information security policy document', required: true, tscRef: ['CC1.1', 'CC5.3'] },
  { id: 'pbc-2', category: 'Governance', name: 'Acceptable Use Policy', description: 'Employee acceptable use policy for IT resources', required: true, tscRef: ['CC1.4', 'CC5.3'] },
  { id: 'pbc-3', category: 'Governance', name: 'Change Management Policy', description: 'Documented change management procedures', required: true, tscRef: ['CC8.1'] },
  { id: 'pbc-4', category: 'Governance', name: 'Incident Response Plan', description: 'Security incident response procedures', required: true, tscRef: ['CC7.4', 'CC7.5'] },
  { id: 'pbc-5', category: 'Governance', name: 'BCP/DR Policy', description: 'Business continuity and disaster recovery plan', required: true, tscRef: ['A1.2', 'A1.3'] },
  { id: 'pbc-6', category: 'Governance', name: 'Vendor Risk Management Policy', description: 'Third-party vendor risk assessment procedures', required: true, tscRef: ['CC9.2'] },
  // Operational Evidence
  { id: 'pbc-7', category: 'Operations', name: 'Access Listing', description: 'Complete user access listing from identity provider (Okta/Azure AD)', required: true, tscRef: ['CC6.1', 'CC6.2', 'CC6.3'] },
  { id: 'pbc-8', category: 'Operations', name: 'Quarterly Access Review', description: 'Evidence of quarterly user access reviews with sign-off', required: true, tscRef: ['CC6.1'] },
  { id: 'pbc-9', category: 'Operations', name: 'Termination Tickets', description: '3 sample termination tickets showing access removal', required: true, tscRef: ['CC6.5'] },
  { id: 'pbc-10', category: 'Operations', name: 'Change Tickets', description: '5 sample production change tickets with approvals', required: true, tscRef: ['CC8.1'] },
  { id: 'pbc-11', category: 'Operations', name: 'CI/CD Pipeline Logs', description: 'CI/CD deployment logs for sample changes', required: true, tscRef: ['CC8.1'] },
  { id: 'pbc-12', category: 'Operations', name: 'Incident Log', description: 'Security incident log for audit period with 2 RCA samples', required: true, tscRef: ['CC7.3', 'CC7.4'] },
  { id: 'pbc-13', category: 'Operations', name: 'Vulnerability Management Records', description: 'Vulnerability scan results and remediation tracking', required: true, tscRef: ['CC6.6', 'CC7.1'] },
  { id: 'pbc-14', category: 'Operations', name: 'Patch/Upgrade Logs', description: 'OS and container patching records', required: true, tscRef: ['CC6.8', 'CC8.1'] },
  { id: 'pbc-15', category: 'Operations', name: 'Backup Logs', description: 'Backup execution logs and restore test evidence', required: true, tscRef: ['A1.2'] },
  { id: 'pbc-16', category: 'Operations', name: 'DR Test Results', description: 'Disaster recovery test results and documentation', required: true, tscRef: ['A1.3'] },
  { id: 'pbc-17', category: 'Operations', name: 'Monitoring Configuration', description: 'Screenshots of monitoring/alerting configurations', required: true, tscRef: ['CC7.1', 'CC7.2'] },
  { id: 'pbc-18', category: 'Operations', name: 'Capacity/Uptime Reports', description: 'SLA dashboard and uptime metrics for audit period', required: true, tscRef: ['A1.1'] },
  // Security Testing
  { id: 'pbc-19', category: 'Security Testing', name: 'Penetration Test Report', description: 'Third-party penetration test report dated within audit period', required: true, tscRef: ['CC4.1', 'CC6.6'] },
  { id: 'pbc-20', category: 'Security Testing', name: 'Pen Test Remediation', description: 'Remediation plan and proof of fixes for pen test findings', required: true, tscRef: ['CC4.2', 'CC7.5'] },
  { id: 'pbc-21', category: 'Security Testing', name: 'Vulnerability Scan Summary', description: 'Quarterly vulnerability scan summary reports', required: true, tscRef: ['CC7.1', 'CC7.2'] },
];

// Audit phases configuration
const AUDIT_PHASES = [
  { id: 'planning', name: 'Planning', icon: Target, status: 'PLANNING' },
  { id: 'risk-assessment', name: 'Risk Assessment', icon: AlertTriangle, status: 'PLANNING' },
  { id: 'control-design', name: 'Control Design', icon: ClipboardList, status: 'FIELDWORK' },
  { id: 'operating-effectiveness', name: 'Operating Effectiveness', icon: FileCheck, status: 'FIELDWORK' },
  { id: 'completion', name: 'Completion', icon: CheckCircle2, status: 'REVIEW' },
  { id: 'reporting', name: 'Reporting', icon: FileText, status: 'PARTNER_REVIEW' },
];

interface PBCItem {
  id: string;
  category: string;
  name: string;
  description: string;
  required: boolean;
  tscRef: string[];
  status: 'pending' | 'requested' | 'submitted' | 'approved' | 'rejected';
  uploadedFile?: string;
  uploadedAt?: string;
  notes?: string;
}

interface ControlObjective {
  id: string;
  code: string;
  name: string;
  description: string;
  tscCategory: string;
  tscCriteria: string;
  controls: Control[];
}

interface Control {
  id: string;
  code: string;
  name: string;
  description: string;
  owner: string;
  frequency: string;
  automationLevel: string;
  designEvaluation?: 'passed' | 'failed' | 'pending';
  operatingEffectiveness?: 'effective' | 'exception' | 'pending';
  testResults: TestResult[];
}

interface TestResult {
  id: string;
  testDate: string;
  testType: string;
  sampleItem: string;
  passed: boolean;
  findings?: string;
  evidence?: string;
}

interface SystemDescription {
  id?: string;
  overview: string;
  principalServiceCommitments: string;
  systemComponents: string;
  boundaries: string;
  subserviceOrganizations: string;
  incidentResponse: string;
  changeManagement: string;
  availabilitySLA: string;
}

const SOCEngagementWorkspace: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [engagement, setEngagement] = useState<SOCEngagement | null>(null);
  const [loading, setLoading] = useState(true);
  const [activePhase, setActivePhase] = useState('planning');
  const [activeTab, setActiveTab] = useState('overview');

  // Data states
  const [pbcItems, setPbcItems] = useState<PBCItem[]>([]);
  const [controlObjectives, setControlObjectives] = useState<ControlObjective[]>([]);
  const [systemDescription, setSystemDescription] = useState<SystemDescription>({
    overview: '',
    principalServiceCommitments: '',
    systemComponents: '',
    boundaries: '',
    subserviceOrganizations: '',
    incidentResponse: '',
    changeManagement: '',
    availabilitySLA: '',
  });
  const [auditTrail, setAuditTrail] = useState<any[]>([]);

  // Modal states
  const [showAddControlModal, setShowAddControlModal] = useState(false);
  const [showTestResultModal, setShowTestResultModal] = useState(false);
  const [showSignatureModal, setShowSignatureModal] = useState(false);
  const [selectedControl, setSelectedControl] = useState<Control | null>(null);
  const [isGeneratingAI, setIsGeneratingAI] = useState(false);

  // Load engagement data
  useEffect(() => {
    const loadEngagement = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const data = await socCopilotService.getEngagement(id);
        setEngagement(data);

        // Initialize PBC items based on TSC categories
        const selectedCategories = data.tsc_categories || ['SECURITY'];
        let relevantPBC = PBC_TEMPLATE.filter(pbc => {
          // Always include governance items
          if (pbc.category === 'Governance') return true;
          // Include operational items for all
          if (pbc.category === 'Operations') return true;
          // Security testing items for Security category
          if (pbc.category === 'Security Testing' && selectedCategories.includes('SECURITY')) return true;
          return false;
        });

        // Add Availability-specific items if selected
        if (selectedCategories.includes('AVAILABILITY')) {
          relevantPBC = [
            ...relevantPBC,
            { id: 'pbc-avail-1', category: 'Availability', name: 'SLA Documentation', description: 'Service Level Agreement documents', required: true, tscRef: ['A1.1'] },
            { id: 'pbc-avail-2', category: 'Availability', name: 'Failover Test Results', description: 'Evidence of failover testing', required: true, tscRef: ['A1.2', 'A1.3'] },
          ];
        }

        setPbcItems(relevantPBC.map(pbc => ({ ...pbc, status: 'pending' as const })));

        // Load audit trail
        const trail = await socCopilotService.getAuditTrail(id);
        setAuditTrail(trail);

        // Set active phase based on status
        const statusPhaseMap: Record<string, string> = {
          'DRAFT': 'planning',
          'PLANNING': 'planning',
          'FIELDWORK': 'control-design',
          'REVIEW': 'completion',
          'PARTNER_REVIEW': 'reporting',
          'SIGNED': 'reporting',
          'RELEASED': 'reporting',
        };
        setActivePhase(statusPhaseMap[data.status] || 'planning');

      } catch (error) {
        console.error('Failed to load SOC engagement:', error);
        toast.error('Failed to load engagement');
      } finally {
        setLoading(false);
      }
    };

    loadEngagement();
  }, [id]);

  // AI-assisted system description generation
  const generateSystemDescription = async () => {
    if (!engagement) return;

    setIsGeneratingAI(true);
    toast.loading('AI is generating system description...', { id: 'ai-gen' });

    // Simulate AI generation (in production, this would call the AI service)
    setTimeout(() => {
      setSystemDescription({
        overview: `${engagement.client_name} provides ${engagement.service_description}. The system is designed to deliver secure, reliable cloud-based services to enterprise customers.`,
        principalServiceCommitments: `${engagement.client_name} commits to:
- Maintaining 99.9% system availability during business hours
- Protecting customer data through encryption at rest and in transit
- Providing timely incident response within defined SLAs
- Implementing industry-standard security controls aligned with SOC 2 Trust Services Criteria`,
        systemComponents: `Infrastructure Components:
- Cloud Provider: AWS (us-east-1, us-west-2)
- Compute: Amazon EKS (Kubernetes) for container orchestration
- Database: Amazon RDS PostgreSQL with Multi-AZ deployment
- Storage: Amazon S3 with server-side encryption
- CDN: Amazon CloudFront for content delivery
- Identity: Okta for Single Sign-On (SSO)

Application Components:
- Web Application: React frontend served via CloudFront
- API Services: Python/FastAPI microservices on EKS
- CI/CD: GitHub Actions for automated deployments`,
        boundaries: `System boundaries include:
- In Scope: Production AWS environment, web application, API services, CI/CD pipeline, identity management
- Out of Scope: Development/staging environments, third-party SaaS tools (except where noted)
- Network Boundaries: VPC with private subnets, NAT gateways, and Application Load Balancer`,
        subserviceOrganizations: `Subservice Organizations (CSOC):
1. Amazon Web Services (AWS) - Infrastructure hosting
   - SOC 2 Type II report reviewed and no exceptions noted
2. Okta - Identity and access management
   - SOC 2 Type II report reviewed and no exceptions noted
3. SendGrid - Email delivery
   - SOC 2 Type II report reviewed and no exceptions noted
4. Stripe - Payment processing
   - PCI DSS and SOC 2 Type II reports reviewed`,
        incidentResponse: `Incident Response Process:
1. Detection: Security events monitored via Datadog SIEM
2. Triage: PagerDuty alerts on-call team within 5 minutes
3. Classification: P1 (critical), P2 (major), P3 (minor), P4 (low)
4. Response: P1/P2 require immediate response; P3/P4 within business hours
5. Resolution: Root cause analysis required for P1/P2 incidents
6. Communication: Customer notification per SLA requirements`,
        changeManagement: `Change Management Process:
1. Change Request: Developer creates PR in GitHub
2. Peer Review: Minimum one peer code review required
3. Automated Testing: CI pipeline runs unit, integration, and security tests
4. Approval: Manager approval for production deployments
5. Deployment: Automated deployment via GitHub Actions
6. Validation: Post-deployment smoke tests and monitoring`,
        availabilitySLA: `Availability Commitments:
- Target Availability: 99.9% uptime (excluding planned maintenance)
- Planned Maintenance: Scheduled during low-traffic windows with 72-hour notice
- Recovery Time Objective (RTO): 4 hours for critical services
- Recovery Point Objective (RPO): 1 hour for database backups
- DR Testing: Quarterly disaster recovery exercises`,
      });

      setIsGeneratingAI(false);
      toast.success('System description generated!', { id: 'ai-gen' });
    }, 3000);
  };

  // Generate control objectives from TSC
  const generateControlObjectives = async () => {
    if (!engagement) return;

    setIsGeneratingAI(true);
    toast.loading('AI is mapping controls to TSC criteria...', { id: 'ai-controls' });

    setTimeout(() => {
      const selectedCategories = engagement.tsc_categories || ['SECURITY'];
      const objectives: ControlObjective[] = [];

      selectedCategories.forEach(category => {
        const tscConfig = TSC_CRITERIA[category as keyof typeof TSC_CRITERIA];
        if (!tscConfig) return;

        // Create control objectives for key criteria
        const keyCriteria = tscConfig.criteria.slice(0, 5); // Limit for demo
        keyCriteria.forEach(criterion => {
          objectives.push({
            id: `obj-${criterion.code}`,
            code: criterion.code,
            name: criterion.name,
            description: criterion.description,
            tscCategory: category,
            tscCriteria: criterion.code,
            controls: [],
          });
        });
      });

      setControlObjectives(objectives);
      setIsGeneratingAI(false);
      toast.success('Control objectives generated!', { id: 'ai-controls' });
    }, 2000);
  };

  // Transition engagement status
  const transitionStatus = async (newStatus: string) => {
    if (!engagement || !id) return;

    try {
      await socCopilotService.transitionEngagementStatus(id, newStatus);
      setEngagement({ ...engagement, status: newStatus as any });
      toast.success(`Status updated to ${newStatus}`);
    } catch (error: any) {
      console.error('Failed to transition status:', error);
      toast.error(error.response?.data?.detail || 'Failed to update status');
    }
  };

  // Get status color
  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      DRAFT: 'gray',
      PLANNING: 'blue',
      FIELDWORK: 'yellow',
      REVIEW: 'purple',
      PARTNER_REVIEW: 'indigo',
      SIGNED: 'green',
      RELEASED: 'emerald',
      ARCHIVED: 'neutral',
    };
    return colors[status] || 'gray';
  };

  // Calculate phase progress
  const getPhaseProgress = () => {
    const statusIndex = ['DRAFT', 'PLANNING', 'FIELDWORK', 'REVIEW', 'PARTNER_REVIEW', 'SIGNED', 'RELEASED'].indexOf(engagement?.status || 'DRAFT');
    return ((statusIndex + 1) / 7) * 100;
  };

  // PBC status counts
  const pbcStats = {
    total: pbcItems.length,
    pending: pbcItems.filter(p => p.status === 'pending').length,
    requested: pbcItems.filter(p => p.status === 'requested').length,
    submitted: pbcItems.filter(p => p.status === 'submitted').length,
    approved: pbcItems.filter(p => p.status === 'approved').length,
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-body text-neutral-600">Loading SOC engagement...</p>
        </div>
      </div>
    );
  }

  if (!engagement) {
    return (
      <div className="text-center py-16">
        <Shield className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
        <h3 className="text-title text-neutral-900 mb-2">Engagement not found</h3>
        <button onClick={() => navigate('/firm/soc-engagements')} className="fluent-btn-primary mt-4">
          Back to SOC Engagements
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-[1800px]">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between"
      >
        <div>
          <button
            onClick={() => navigate('/firm/soc-engagements')}
            className="flex items-center gap-2 text-neutral-600 hover:text-neutral-900 mb-3"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to SOC Engagements
          </button>
          <div className="flex items-center gap-3 mb-1">
            <Shield className="w-8 h-8 text-primary-500" />
            <div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-bold ${
                  engagement.engagement_type === 'SOC1' ? 'bg-blue-100 text-blue-700' : 'bg-purple-100 text-purple-700'
                }`}>
                  {engagement.engagement_type}
                </span>
                <span className="text-caption text-neutral-500">
                  Type {engagement.report_type === 'TYPE1' ? 'I' : 'II'}
                </span>
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-${getStatusColor(engagement.status)}-100 text-${getStatusColor(engagement.status)}-700`}>
                  {engagement.status.replace('_', ' ')}
                </span>
              </div>
              <h1 className="text-display text-neutral-900">{engagement.client_name}</h1>
              <p className="text-body text-neutral-600">{engagement.service_description}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {engagement.status === 'DRAFT' && (
            <button onClick={() => transitionStatus('PLANNING')} className="fluent-btn-primary">
              Start Planning
            </button>
          )}
          {engagement.status === 'PLANNING' && (
            <button onClick={() => transitionStatus('FIELDWORK')} className="fluent-btn-primary">
              Begin Fieldwork
            </button>
          )}
          {engagement.status === 'FIELDWORK' && (
            <button onClick={() => transitionStatus('REVIEW')} className="fluent-btn-primary">
              Submit for Review
            </button>
          )}
          {engagement.status === 'REVIEW' && (
            <button onClick={() => transitionStatus('PARTNER_REVIEW')} className="fluent-btn-primary">
              Partner Review
            </button>
          )}
          {engagement.status === 'PARTNER_REVIEW' && (
            <button onClick={() => setShowSignatureModal(true)} className="fluent-btn-primary">
              <PenTool className="w-4 h-4" />
              Sign Report
            </button>
          )}
        </div>
      </motion.div>

      {/* Progress Bar */}
      <div className="fluent-card p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-caption text-neutral-600">Engagement Progress</span>
          <span className="text-caption text-neutral-900 font-medium">{Math.round(getPhaseProgress())}%</span>
        </div>
        <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${getPhaseProgress()}%` }}
            className="h-full bg-primary-500 rounded-full"
          />
        </div>
        <div className="flex items-center justify-between mt-3">
          {['DRAFT', 'PLANNING', 'FIELDWORK', 'REVIEW', 'PARTNER_REVIEW', 'SIGNED', 'RELEASED'].map((status, index) => {
            const currentIndex = ['DRAFT', 'PLANNING', 'FIELDWORK', 'REVIEW', 'PARTNER_REVIEW', 'SIGNED', 'RELEASED'].indexOf(engagement.status);
            const isComplete = index <= currentIndex;
            const isCurrent = status === engagement.status;

            return (
              <div key={status} className={`flex flex-col items-center ${index === 0 ? '' : 'flex-1'}`}>
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                  isComplete ? 'bg-primary-500 text-white' : 'bg-neutral-200 text-neutral-500'
                } ${isCurrent ? 'ring-2 ring-primary-300' : ''}`}>
                  {isComplete ? <Check className="w-3 h-3" /> : index + 1}
                </div>
                <span className={`text-xs mt-1 ${isCurrent ? 'text-primary-600 font-medium' : 'text-neutral-500'}`}>
                  {status.replace('_', ' ')}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* TSC Categories */}
      <div className="flex flex-wrap gap-2">
        {(engagement.tsc_categories || ['SECURITY']).map(cat => {
          const tscConfig = TSC_CRITERIA[cat as keyof typeof TSC_CRITERIA];
          if (!tscConfig) return null;
          const Icon = tscConfig.icon;
          return (
            <span key={cat} className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-fluent bg-${tscConfig.color}-50 text-${tscConfig.color}-700`}>
              <Icon className="w-4 h-4" />
              {tscConfig.name}
            </span>
          );
        })}
        {engagement.review_period_start && engagement.review_period_end && (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-fluent bg-neutral-100 text-neutral-700">
            <Calendar className="w-4 h-4" />
            {new Date(engagement.review_period_start).toLocaleDateString()} - {new Date(engagement.review_period_end).toLocaleDateString()}
          </span>
        )}
      </div>

      {/* Main Content Tabs */}
      <div className="fluent-card">
        <div className="border-b border-neutral-200">
          <nav className="flex space-x-1 p-2">
            {[
              { id: 'overview', label: 'Overview', icon: Target },
              { id: 'system-description', label: 'System Description', icon: Building2 },
              { id: 'pbc-requests', label: 'PBC Requests', icon: Upload },
              { id: 'controls', label: 'Controls', icon: ClipboardList },
              { id: 'testing', label: 'Testing', icon: FileCheck },
              { id: 'reports', label: 'Reports', icon: FileText },
              { id: 'audit-trail', label: 'Audit Trail', icon: Clock },
            ].map(tab => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-fluent-sm text-body transition-all ${
                    activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700 font-medium'
                      : 'text-neutral-600 hover:bg-neutral-50'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                  {tab.id === 'pbc-requests' && pbcStats.submitted > 0 && (
                    <span className="ml-1 px-1.5 py-0.5 rounded-full text-xs bg-amber-100 text-amber-700">
                      {pbcStats.submitted}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="fluent-card-interactive p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <Upload className="w-5 h-5 text-primary-500" />
                    <span className="text-body-strong">PBC Evidence</span>
                  </div>
                  <div className="text-title-large text-primary-600 font-semibold mb-1">
                    {pbcStats.approved}/{pbcStats.total}
                  </div>
                  <p className="text-caption text-neutral-600">Items approved</p>
                  <div className="mt-3 h-2 bg-neutral-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full"
                      style={{ width: `${(pbcStats.approved / pbcStats.total) * 100}%` }}
                    />
                  </div>
                </div>

                <div className="fluent-card-interactive p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <ClipboardList className="w-5 h-5 text-accent-500" />
                    <span className="text-body-strong">Control Objectives</span>
                  </div>
                  <div className="text-title-large text-accent-600 font-semibold mb-1">
                    {controlObjectives.length}
                  </div>
                  <p className="text-caption text-neutral-600">Objectives mapped</p>
                  <button
                    onClick={generateControlObjectives}
                    disabled={isGeneratingAI}
                    className="mt-3 text-sm text-primary-600 hover:text-primary-700 flex items-center gap-1"
                  >
                    <Sparkles className="w-3 h-3" />
                    AI Generate from TSC
                  </button>
                </div>

                <div className="fluent-card-interactive p-4">
                  <div className="flex items-center gap-3 mb-3">
                    <FileCheck className="w-5 h-5 text-success-500" />
                    <span className="text-body-strong">Tests Completed</span>
                  </div>
                  <div className="text-title-large text-success-600 font-semibold mb-1">
                    0/{controlObjectives.reduce((acc, obj) => acc + obj.controls.length, 0) || 0}
                  </div>
                  <p className="text-caption text-neutral-600">Control tests</p>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="fluent-card p-4">
                  <h3 className="text-body-strong mb-3">Quick Actions</h3>
                  <div className="space-y-2">
                    <button
                      onClick={() => setActiveTab('system-description')}
                      className="w-full flex items-center justify-between p-3 rounded-fluent hover:bg-neutral-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Building2 className="w-5 h-5 text-neutral-500" />
                        <span>Draft System Description</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-neutral-400" />
                    </button>
                    <button
                      onClick={() => setActiveTab('pbc-requests')}
                      className="w-full flex items-center justify-between p-3 rounded-fluent hover:bg-neutral-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Send className="w-5 h-5 text-neutral-500" />
                        <span>Send PBC Requests to Client</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-neutral-400" />
                    </button>
                    <button
                      onClick={() => setActiveTab('controls')}
                      className="w-full flex items-center justify-between p-3 rounded-fluent hover:bg-neutral-50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <ClipboardList className="w-5 h-5 text-neutral-500" />
                        <span>Map Controls to TSC</span>
                      </div>
                      <ChevronRight className="w-4 h-4 text-neutral-400" />
                    </button>
                  </div>
                </div>

                <div className="fluent-card p-4">
                  <h3 className="text-body-strong mb-3">Recent Activity</h3>
                  <div className="space-y-3">
                    {auditTrail.slice(0, 5).map((entry, index) => (
                      <div key={index} className="flex items-start gap-3 text-sm">
                        <div className="w-2 h-2 mt-1.5 rounded-full bg-primary-500" />
                        <div>
                          <p className="text-neutral-900">{entry.event_type.replace(/_/g, ' ')}</p>
                          <p className="text-neutral-500 text-xs">
                            {new Date(entry.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    ))}
                    {auditTrail.length === 0 && (
                      <p className="text-neutral-500 text-sm">No activity yet</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* System Description Tab */}
          {activeTab === 'system-description' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-title">System Description (SOC 2 DC 2018)</h3>
                <button
                  onClick={generateSystemDescription}
                  disabled={isGeneratingAI}
                  className="fluent-btn-secondary"
                >
                  {isGeneratingAI ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Sparkles className="w-4 h-4" />
                  )}
                  AI Generate
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Overview of Operations
                    </label>
                    <textarea
                      value={systemDescription.overview}
                      onChange={(e) => setSystemDescription({ ...systemDescription, overview: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="Describe the nature of the entity's operations..."
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Principal Service Commitments
                    </label>
                    <textarea
                      value={systemDescription.principalServiceCommitments}
                      onChange={(e) => setSystemDescription({ ...systemDescription, principalServiceCommitments: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="Describe commitments made to user entities..."
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      System Components
                    </label>
                    <textarea
                      value={systemDescription.systemComponents}
                      onChange={(e) => setSystemDescription({ ...systemDescription, systemComponents: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="Infrastructure, software, people, procedures, data..."
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      System Boundaries
                    </label>
                    <textarea
                      value={systemDescription.boundaries}
                      onChange={(e) => setSystemDescription({ ...systemDescription, boundaries: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="Define what is in scope and out of scope..."
                    />
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Subservice Organizations
                    </label>
                    <textarea
                      value={systemDescription.subserviceOrganizations}
                      onChange={(e) => setSystemDescription({ ...systemDescription, subserviceOrganizations: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="List vendors and their SOC reports (carve-out vs inclusive)..."
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Incident Response & Monitoring
                    </label>
                    <textarea
                      value={systemDescription.incidentResponse}
                      onChange={(e) => setSystemDescription({ ...systemDescription, incidentResponse: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="Describe security monitoring and incident response procedures..."
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Change Management & SDLC
                    </label>
                    <textarea
                      value={systemDescription.changeManagement}
                      onChange={(e) => setSystemDescription({ ...systemDescription, changeManagement: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="Describe change management and development lifecycle..."
                    />
                  </div>

                  <div>
                    <label className="block text-body-strong text-neutral-700 mb-2">
                      Availability SLAs & DR Approach
                    </label>
                    <textarea
                      value={systemDescription.availabilitySLA}
                      onChange={(e) => setSystemDescription({ ...systemDescription, availabilitySLA: e.target.value })}
                      className="fluent-input min-h-[120px]"
                      placeholder="Define SLA commitments, RTO, RPO, DR testing..."
                    />
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-3">
                <button className="fluent-btn-secondary">Save Draft</button>
                <button className="fluent-btn-primary">
                  <Check className="w-4 h-4" />
                  Finalize Description
                </button>
              </div>
            </div>
          )}

          {/* PBC Requests Tab */}
          {activeTab === 'pbc-requests' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-title">PBC Request List</h3>
                  <p className="text-caption text-neutral-600">Evidence items required from {engagement.client_name}</p>
                </div>
                <div className="flex items-center gap-3">
                  <button className="fluent-btn-secondary">
                    <Download className="w-4 h-4" />
                    Export PBC List
                  </button>
                  <button className="fluent-btn-primary">
                    <Send className="w-4 h-4" />
                    Send to Client
                  </button>
                </div>
              </div>

              {/* PBC Stats */}
              <div className="grid grid-cols-5 gap-3">
                {[
                  { label: 'Total', value: pbcStats.total, color: 'neutral' },
                  { label: 'Pending', value: pbcStats.pending, color: 'gray' },
                  { label: 'Requested', value: pbcStats.requested, color: 'blue' },
                  { label: 'Submitted', value: pbcStats.submitted, color: 'amber' },
                  { label: 'Approved', value: pbcStats.approved, color: 'green' },
                ].map(stat => (
                  <div key={stat.label} className={`p-3 rounded-fluent bg-${stat.color}-50`}>
                    <p className={`text-title-large font-semibold text-${stat.color}-700`}>{stat.value}</p>
                    <p className="text-caption text-neutral-600">{stat.label}</p>
                  </div>
                ))}
              </div>

              {/* PBC Items by Category */}
              {['Governance', 'Operations', 'Security Testing', 'Availability'].map(category => {
                const categoryItems = pbcItems.filter(p => p.category === category);
                if (categoryItems.length === 0) return null;

                return (
                  <div key={category} className="space-y-3">
                    <h4 className="text-body-strong text-neutral-800">{category}</h4>
                    <div className="space-y-2">
                      {categoryItems.map(item => (
                        <div
                          key={item.id}
                          className="flex items-center justify-between p-4 border border-neutral-200 rounded-fluent hover:border-neutral-300 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-body-strong">{item.name}</span>
                              {item.required && (
                                <span className="text-xs bg-error-100 text-error-700 px-1.5 py-0.5 rounded">Required</span>
                              )}
                            </div>
                            <p className="text-caption text-neutral-600">{item.description}</p>
                            <div className="flex items-center gap-2 mt-2">
                              {item.tscRef.map(ref => (
                                <span key={ref} className="text-xs bg-neutral-100 text-neutral-600 px-1.5 py-0.5 rounded">
                                  {ref}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <select
                              value={item.status}
                              onChange={(e) => {
                                setPbcItems(pbcItems.map(p =>
                                  p.id === item.id ? { ...p, status: e.target.value as any } : p
                                ));
                              }}
                              className={`text-sm px-3 py-1.5 rounded-fluent border ${
                                item.status === 'approved' ? 'bg-green-50 border-green-200 text-green-700' :
                                item.status === 'submitted' ? 'bg-amber-50 border-amber-200 text-amber-700' :
                                item.status === 'requested' ? 'bg-blue-50 border-blue-200 text-blue-700' :
                                item.status === 'rejected' ? 'bg-red-50 border-red-200 text-red-700' :
                                'bg-neutral-50 border-neutral-200'
                              }`}
                            >
                              <option value="pending">Pending</option>
                              <option value="requested">Requested</option>
                              <option value="submitted">Submitted</option>
                              <option value="approved">Approved</option>
                              <option value="rejected">Needs Revision</option>
                            </select>
                            <button className="p-2 hover:bg-neutral-100 rounded-fluent-sm">
                              <MessageSquare className="w-4 h-4 text-neutral-500" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Controls Tab */}
          {activeTab === 'controls' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-title">Control Objectives & Controls</h3>
                  <p className="text-caption text-neutral-600">Map controls to Trust Services Criteria</p>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={generateControlObjectives}
                    disabled={isGeneratingAI}
                    className="fluent-btn-secondary"
                  >
                    {isGeneratingAI ? (
                      <RefreshCw className="w-4 h-4 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4" />
                    )}
                    AI Generate from TSC
                  </button>
                  <button
                    onClick={() => setShowAddControlModal(true)}
                    className="fluent-btn-primary"
                  >
                    <Plus className="w-4 h-4" />
                    Add Control
                  </button>
                </div>
              </div>

              {controlObjectives.length === 0 ? (
                <div className="text-center py-12 border-2 border-dashed border-neutral-200 rounded-fluent">
                  <ClipboardList className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
                  <h4 className="text-body-strong text-neutral-700 mb-2">No control objectives defined</h4>
                  <p className="text-caption text-neutral-500 mb-4">
                    Generate control objectives from TSC criteria or add them manually
                  </p>
                  <button
                    onClick={generateControlObjectives}
                    className="fluent-btn-primary"
                  >
                    <Sparkles className="w-4 h-4" />
                    AI Generate from TSC
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {controlObjectives.map(objective => {
                    const tscConfig = TSC_CRITERIA[objective.tscCategory as keyof typeof TSC_CRITERIA];
                    const Icon = tscConfig?.icon || Shield;

                    return (
                      <div key={objective.id} className="border border-neutral-200 rounded-fluent overflow-hidden">
                        <div className={`px-4 py-3 bg-${tscConfig?.color || 'neutral'}-50 border-b border-neutral-200`}>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <Icon className={`w-5 h-5 text-${tscConfig?.color || 'neutral'}-600`} />
                              <div>
                                <div className="flex items-center gap-2">
                                  <span className="font-mono text-sm font-bold">{objective.code}</span>
                                  <span className="text-body-strong">{objective.name}</span>
                                </div>
                                <p className="text-caption text-neutral-600">{objective.description}</p>
                              </div>
                            </div>
                            <button className="p-2 hover:bg-white/50 rounded-fluent-sm">
                              <Plus className="w-4 h-4" />
                            </button>
                          </div>
                        </div>

                        {objective.controls.length > 0 ? (
                          <div className="divide-y divide-neutral-100">
                            {objective.controls.map(control => (
                              <div key={control.id} className="px-4 py-3 flex items-center justify-between hover:bg-neutral-50">
                                <div>
                                  <div className="flex items-center gap-2">
                                    <span className="font-mono text-xs bg-neutral-100 px-1.5 py-0.5 rounded">{control.code}</span>
                                    <span className="text-body">{control.name}</span>
                                  </div>
                                  <p className="text-caption text-neutral-500">{control.description}</p>
                                </div>
                                <div className="flex items-center gap-2">
                                  <span className={`text-xs px-2 py-1 rounded ${
                                    control.designEvaluation === 'passed' ? 'bg-green-100 text-green-700' :
                                    control.designEvaluation === 'failed' ? 'bg-red-100 text-red-700' :
                                    'bg-neutral-100 text-neutral-600'
                                  }`}>
                                    Design: {control.designEvaluation || 'Pending'}
                                  </span>
                                  <span className={`text-xs px-2 py-1 rounded ${
                                    control.operatingEffectiveness === 'effective' ? 'bg-green-100 text-green-700' :
                                    control.operatingEffectiveness === 'exception' ? 'bg-red-100 text-red-700' :
                                    'bg-neutral-100 text-neutral-600'
                                  }`}>
                                    OE: {control.operatingEffectiveness || 'Pending'}
                                  </span>
                                  <button className="p-1.5 hover:bg-neutral-100 rounded">
                                    <MoreVertical className="w-4 h-4 text-neutral-500" />
                                  </button>
                                </div>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="px-4 py-6 text-center text-neutral-500">
                            <p className="text-caption">No controls mapped to this objective</p>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Testing Tab */}
          {activeTab === 'testing' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-title">Control Testing</h3>
                  <p className="text-caption text-neutral-600">Document test procedures and results</p>
                </div>
                <button className="fluent-btn-primary">
                  <Plus className="w-4 h-4" />
                  Create Test Plan
                </button>
              </div>

              <div className="border border-neutral-200 rounded-fluent p-8 text-center">
                <FileCheck className="w-12 h-12 text-neutral-300 mx-auto mb-3" />
                <h4 className="text-body-strong text-neutral-700 mb-2">No test plans created</h4>
                <p className="text-caption text-neutral-500 mb-4">
                  Create test plans for each control to document testing procedures and results
                </p>
                <button className="fluent-btn-secondary">
                  View Testing Guide
                </button>
              </div>
            </div>
          )}

          {/* Reports Tab */}
          {activeTab === 'reports' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-title">SOC Report</h3>
                  <p className="text-caption text-neutral-600">Generate and manage the final SOC report</p>
                </div>
                <button className="fluent-btn-primary">
                  <FileText className="w-4 h-4" />
                  Generate Report Draft
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="fluent-card p-6">
                  <h4 className="text-body-strong mb-4">Report Sections</h4>
                  <div className="space-y-3">
                    {[
                      { name: "Independent Service Auditor's Report", status: 'pending' },
                      { name: "Management's Assertion", status: 'pending' },
                      { name: 'Description of the System', status: systemDescription.overview ? 'draft' : 'pending' },
                      { name: 'Trust Services Categories & Criteria', status: 'pending' },
                      { name: 'Control Activities & Tests', status: 'pending' },
                      { name: 'Results of Tests & Exceptions', status: 'pending' },
                      { name: 'Complementary User Entity Controls', status: 'pending' },
                      { name: 'Subservice Organization Controls', status: 'pending' },
                    ].map((section, index) => (
                      <div key={index} className="flex items-center justify-between p-3 border border-neutral-200 rounded-fluent">
                        <div className="flex items-center gap-3">
                          {section.status === 'complete' ? (
                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                          ) : section.status === 'draft' ? (
                            <Edit className="w-5 h-5 text-amber-500" />
                          ) : (
                            <Clock className="w-5 h-5 text-neutral-400" />
                          )}
                          <span className="text-body">{section.name}</span>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${
                          section.status === 'complete' ? 'bg-green-100 text-green-700' :
                          section.status === 'draft' ? 'bg-amber-100 text-amber-700' :
                          'bg-neutral-100 text-neutral-600'
                        }`}>
                          {section.status.charAt(0).toUpperCase() + section.status.slice(1)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="fluent-card p-6">
                    <h4 className="text-body-strong mb-4">Report Status</h4>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-body">Report Type</span>
                        <span className="font-medium">{engagement.engagement_type} Type {engagement.report_type === 'TYPE1' ? 'I' : 'II'}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-body">Engagement Status</span>
                        <span className={`px-2 py-1 rounded text-sm bg-${getStatusColor(engagement.status)}-100 text-${getStatusColor(engagement.status)}-700`}>
                          {engagement.status.replace('_', ' ')}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-body">Report Period</span>
                        <span className="text-sm">
                          {engagement.review_period_start && engagement.review_period_end
                            ? `${new Date(engagement.review_period_start).toLocaleDateString()} - ${new Date(engagement.review_period_end).toLocaleDateString()}`
                            : engagement.point_in_time_date
                            ? `As of ${new Date(engagement.point_in_time_date).toLocaleDateString()}`
                            : 'Not set'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="fluent-card p-6">
                    <h4 className="text-body-strong mb-4">Signature & Release</h4>
                    {engagement.status === 'PARTNER_REVIEW' ? (
                      <div className="space-y-3">
                        <p className="text-caption text-neutral-600">
                          Ready for CPA Partner signature. Review the complete report before signing.
                        </p>
                        <button
                          onClick={() => setShowSignatureModal(true)}
                          className="fluent-btn-primary w-full"
                        >
                          <PenTool className="w-4 h-4" />
                          Sign Report
                        </button>
                      </div>
                    ) : engagement.status === 'SIGNED' || engagement.status === 'RELEASED' ? (
                      <div className="space-y-3">
                        <div className="flex items-center gap-2 text-green-600">
                          <CheckCircle2 className="w-5 h-5" />
                          <span className="font-medium">Report Signed</span>
                        </div>
                        <button className="fluent-btn-primary w-full">
                          <Download className="w-4 h-4" />
                          Download Final PDF
                        </button>
                      </div>
                    ) : (
                      <p className="text-caption text-neutral-500">
                        Complete all audit phases before signing the report.
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Audit Trail Tab */}
          {activeTab === 'audit-trail' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-title">Audit Trail</h3>
                  <p className="text-caption text-neutral-600">Immutable log of all engagement activities</p>
                </div>
                <button className="fluent-btn-secondary">
                  <Download className="w-4 h-4" />
                  Export Trail
                </button>
              </div>

              <div className="border border-neutral-200 rounded-fluent overflow-hidden">
                <table className="w-full">
                  <thead className="bg-neutral-50">
                    <tr>
                      <th className="text-left text-caption font-medium text-neutral-600 px-4 py-3">Timestamp</th>
                      <th className="text-left text-caption font-medium text-neutral-600 px-4 py-3">Event</th>
                      <th className="text-left text-caption font-medium text-neutral-600 px-4 py-3">Action</th>
                      <th className="text-left text-caption font-medium text-neutral-600 px-4 py-3">Details</th>
                      <th className="text-left text-caption font-medium text-neutral-600 px-4 py-3">Hash</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-100">
                    {auditTrail.map((entry, index) => (
                      <tr key={index} className="hover:bg-neutral-50">
                        <td className="px-4 py-3 text-sm">{new Date(entry.created_at).toLocaleString()}</td>
                        <td className="px-4 py-3 text-sm font-medium">{entry.event_type.replace(/_/g, ' ')}</td>
                        <td className="px-4 py-3 text-sm">{entry.action}</td>
                        <td className="px-4 py-3 text-sm text-neutral-600">
                          {entry.after_state ? JSON.stringify(entry.after_state).slice(0, 50) + '...' : '-'}
                        </td>
                        <td className="px-4 py-3 text-xs font-mono text-neutral-500">{entry.event_hash}</td>
                      </tr>
                    ))}
                    {auditTrail.length === 0 && (
                      <tr>
                        <td colSpan={5} className="px-4 py-8 text-center text-neutral-500">
                          No audit trail entries yet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Signature Modal */}
      <AnimatePresence>
        {showSignatureModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={() => setShowSignatureModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-fluent-lg p-6 max-w-lg w-full shadow-fluent-16"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <PenTool className="w-6 h-6 text-primary-500" />
                  <h2 className="text-title-large text-neutral-900">Sign SOC Report</h2>
                </div>
                <button onClick={() => setShowSignatureModal(false)} className="p-2 hover:bg-neutral-100 rounded-fluent-sm">
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-fluent">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
                    <div>
                      <p className="text-body-strong text-amber-800">CPA Partner Certification</p>
                      <p className="text-sm text-amber-700 mt-1">
                        By signing this report, you certify that the engagement was conducted in accordance with SSAE 18 / AT-C 320 and that the opinion expressed is based on sufficient appropriate evidence.
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Digital Signature</label>
                  <div className="border-2 border-dashed border-neutral-300 rounded-fluent p-8 text-center">
                    <PenTool className="w-8 h-8 text-neutral-400 mx-auto mb-2" />
                    <p className="text-caption text-neutral-500">Click to apply your CPA digital signature</p>
                  </div>
                </div>

                <div>
                  <label className="block text-body-strong text-neutral-700 mb-2">Signature Date</label>
                  <input
                    type="date"
                    defaultValue={new Date().toISOString().split('T')[0]}
                    className="fluent-input"
                  />
                </div>

                <div className="flex items-start gap-2">
                  <input type="checkbox" id="confirm" className="mt-1" />
                  <label htmlFor="confirm" className="text-sm text-neutral-600">
                    I confirm that I have reviewed the complete SOC {engagement?.engagement_type} Type {engagement?.report_type === 'TYPE1' ? 'I' : 'II'} report and all supporting documentation.
                  </label>
                </div>
              </div>

              <div className="flex gap-3 mt-6 pt-6 border-t border-neutral-200">
                <button onClick={() => setShowSignatureModal(false)} className="fluent-btn-secondary flex-1">
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    await transitionStatus('SIGNED');
                    setShowSignatureModal(false);
                    toast.success('Report signed successfully!');
                  }}
                  className="fluent-btn-primary flex-1"
                >
                  <PenTool className="w-4 h-4" />
                  Apply Signature
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SOCEngagementWorkspace;
