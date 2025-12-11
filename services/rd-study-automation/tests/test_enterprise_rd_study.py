"""
Enterprise-Level E2E Test for R&D Tax Credit Services

Comprehensive test featuring:
- 3 R&D projects with extensive 4-Part Test documentation
- Enterprise-scale data: 750 employees, 350 contractors, 800+ expenses
- All expense categories: wages, supplies, subcontractor, computer supplies
- 2 State R&D studies: Pennsylvania (PA) and California (CA)
- Detailed qualification narratives passing all 4 parts of the R&D test
- PDF study generation with Aura AI branding
- Excel export with state calculations
- CPA sign-off workflow
"""

import os
import sys
import json
import random
import string
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from uuid import uuid4
import io

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.generators.pdf_generator import PDFStudyGenerator
from app.generators.excel_generator import ExcelWorkbookGenerator
from app.engines.calculation_engine import CalculationEngine
from app.engines.qre_engine import QREEngine
from app.engines.qualification_engine import QualificationEngine
from app.engines.rules_engine import FederalRules, StateRules, STATE_RULES_2024


# =============================================================================
# ENTERPRISE TEST DATA GENERATORS
# =============================================================================

class EnterpriseTestDataGenerator:
    """Generates enterprise-scale test data for R&D studies."""

    # Focus on PA and CA for state studies
    STATES = ["CA", "PA"]
    STATE_DISTRIBUTION = {"CA": 0.55, "PA": 0.45}

    # Job titles for R&D employees
    JOB_TITLES = [
        "Software Engineer", "Senior Software Engineer", "Staff Engineer",
        "Principal Engineer", "Data Scientist", "Machine Learning Engineer",
        "Research Scientist", "DevOps Engineer", "Systems Architect",
        "QA Engineer", "Test Engineer", "Platform Engineer",
        "Frontend Developer", "Backend Developer", "Full Stack Developer",
        "Engineering Manager", "Technical Lead", "R&D Director",
        "Product Engineer", "Automation Engineer", "Security Engineer",
        "Cloud Engineer", "Infrastructure Engineer", "Site Reliability Engineer",
        "AI Research Scientist", "Computer Vision Engineer", "NLP Engineer",
        "Robotics Engineer", "Hardware Engineer", "Embedded Systems Engineer"
    ]

    DEPARTMENTS = [
        "Engineering", "R&D", "Product Development", "AI/ML Research",
        "Platform", "Infrastructure", "Quality Engineering", "DevOps",
        "Advanced Research", "Innovation Lab", "Applied Science"
    ]

    # Supply vendors by category
    SUPPLY_VENDORS = {
        "cloud_computing": ["AWS", "Azure", "Google Cloud", "DigitalOcean", "Cloudflare", "Oracle Cloud"],
        "software_licenses": ["GitHub Enterprise", "GitLab", "Atlassian", "JetBrains", "Microsoft 365"],
        "monitoring_tools": ["DataDog", "New Relic", "Splunk", "PagerDuty", "Sentry", "Prometheus"],
        "computer_supplies": ["Dell Technologies", "HP Enterprise", "Lenovo", "Apple", "NVIDIA", "Intel", "AMD"],
        "research_supplies": ["Fisher Scientific", "VWR International", "Sigma-Aldrich", "ThermoFisher", "Bio-Rad"]
    }

    # Subcontractor categories
    SUBCONTRACTORS = {
        "research_institutions": [
            "MIT Lincoln Labs", "Stanford Research Institute", "Carnegie Mellon SEI",
            "UC Berkeley Research", "CalTech Research", "Penn State Research",
            "University of Pennsylvania", "Drexel University", "Temple University"
        ],
        "consulting_firms": [
            "Accenture Labs", "Deloitte AI", "McKinsey Advanced Analytics",
            "Boston Consulting Group", "Bain & Company Research"
        ],
        "specialized_contractors": [
            "NVIDIA AI Services", "IBM Research", "Microsoft Research",
            "Google Research", "Amazon Research", "Meta AI"
        ],
        "engineering_firms": [
            "Booz Allen Hamilton", "MITRE Corporation", "Battelle Memorial",
            "Southwest Research Institute", "Applied Research Associates"
        ]
    }

    FIRST_NAMES = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
        "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
        "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
        "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
        "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
        "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
        "Wei", "Priya", "Raj", "Mei", "Yuki", "Ahmed", "Fatima", "Carlos", "Sofia"
    ]

    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
        "Chen", "Kim", "Patel", "Shah", "Kumar", "Singh", "Zhang", "Wang", "Li",
        "Tanaka", "Suzuki", "Nakamura", "Gupta", "Sharma", "Reddy", "Iyer", "Rao"
    ]

    def __init__(self, seed: int = 42):
        """Initialize with a seed for reproducibility."""
        random.seed(seed)
        self.employee_id_counter = 1000

    def generate_employee_id(self) -> str:
        self.employee_id_counter += 1
        return f"EMP-{self.employee_id_counter}"

    def generate_name(self) -> str:
        return f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"

    def get_state_for_index(self, index: int, total: int) -> str:
        position = index / total
        cumulative = 0.0
        for state, pct in self.STATE_DISTRIBUTION.items():
            cumulative += pct
            if position < cumulative:
                return state
        return "CA"

    def generate_projects(self) -> List[Dict[str, Any]]:
        """Generate 3 comprehensive R&D projects with detailed 4-Part Test answers."""

        projects = []

        # Project 1: AI Document Intelligence Platform
        project1 = {
            "id": str(uuid4()),
            "name": "Aura AI - Intelligent Document Processing & Analysis Platform",
            "code": "AURA-IDP-2024",
            "description": """
Development of an advanced AI-powered document processing and analysis platform that utilizes
machine learning, natural language processing, and computer vision to automatically extract,
classify, and analyze complex financial documents including tax returns, audit workpapers,
and general ledger data. The platform represents a significant technological advancement over
existing solutions through novel approaches to document understanding, entity extraction, and
automated reconciliation algorithms.

KEY TECHNICAL OBJECTIVES:
- Achieve 98.5% extraction accuracy on complex multi-page financial documents
- Process 100,000+ documents per hour with sub-100ms latency per page
- Support 50+ document types including handwritten annotations
- Implement self-improving ML models with continuous learning capabilities
- Develop novel multi-modal transformer architecture for document understanding
            """.strip(),
            "department": "AI/ML Research",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "project_lead": "Dr. Sarah Chen, Ph.D. - Chief AI Scientist",
            "total_budget": Decimal("18000000"),
            "qualification_status": "qualified",
            "overall_score": 94,
            "cpa_reviewed": True,
            "cpa_approved": True,
            "cpa_approval_date": date.today().isoformat(),
            "cpa_notes": "Project meets all 4-Part Test criteria with exceptional documentation.",

            "four_part_test": {
                "permitted_purpose": {
                    "score": 96,
                    "status": "qualified",
                    "answer": """
PERMITTED PURPOSE ANALYSIS - AURA AI DOCUMENT PROCESSING PLATFORM

The Aura AI Document Processing Platform qualifies under IRC Section 41(d)(1)(B) as research
undertaken for the purpose of discovering information that is technological in nature, intended
to be useful in the development of a NEW OR IMPROVED business component with substantially
improved performance, functionality, reliability, or quality.

I. NEW AND IMPROVED FUNCTIONALITY:

1. NOVEL MULTI-MODAL DOCUMENT UNDERSTANDING:
   - Development of a proprietary transformer architecture that simultaneously processes:
     * Visual layout features (document structure, tables, figures)
     * Textual content (OCR output, typed and handwritten text)
     * Structural relationships (hierarchies, cross-references, footnotes)
   - This represents a FUNDAMENTAL ADVANCE over existing single-modality OCR solutions
   - No commercially available solution combines all three modalities with our accuracy levels

2. INTELLIGENT ENTITY EXTRACTION:
   - Custom named entity recognition (NER) models trained on 2M+ proprietary financial documents
   - Domain-specific entity types: account numbers, amounts with context, regulatory citations
   - Confidence scoring with explanation generation - a novel capability not found in competitors
   - Performance: 97.3% F1 score vs. 82% industry average

3. AUTOMATED RECONCILIATION ENGINE:
   - Graph-based matching algorithms that reconcile entries across multiple documents/periods
   - Probabilistic reasoning for handling discrepancies and near-matches
   - Historical pattern analysis for anomaly detection
   - Target: 85% reduction in manual reconciliation time (validated by pilot customers)

4. ADAPTIVE LEARNING SYSTEM:
   - Self-improving models that learn from user corrections
   - Transfer learning for rapid onboarding of new document types
   - Few-shot learning capabilities requiring <100 examples for new categories

II. SUBSTANTIAL IMPROVEMENT METRICS:

| Metric                      | Industry Standard | Aura AI Target | Improvement |
|-----------------------------|-------------------|----------------|-------------|
| Extraction Accuracy         | 85-90%            | 98.5%          | +10-15%     |
| Processing Speed            | 1,000 docs/hr     | 100,000/hr     | 100x        |
| Document Types Supported    | 10-15             | 50+            | 3-5x        |
| Time to Process New Type    | 3-6 months        | 2 weeks        | 6-12x       |
| Manual Review Rate          | 30-40%            | <5%            | 6-8x        |

III. BUSINESS COMPONENT QUALIFICATION:

The improvements are embodied in a distinct business component: the Aura AI Document Processing
Platform, which is offered as a separate product/service to customers. The platform includes:
- Cloud-based API service for document processing
- On-premises enterprise deployment option
- SDK for integration with existing systems
- Pre-trained models for common document types
- Fine-tuning capabilities for custom requirements

IV. CONCLUSION:

The Aura AI platform clearly satisfies the Permitted Purpose test. We are developing genuinely
NEW capabilities (multi-modal document understanding, adaptive learning) and achieving SUBSTANTIAL
IMPROVEMENTS over existing solutions (10x+ accuracy improvement, 100x processing speed). These
are not cosmetic changes or minor incremental improvements - they represent fundamental advances
in document processing technology.
                    """.strip(),
                    "evidence": [
                        "Product Requirements Document (PRD) v4.1 - January 2024",
                        "Technical Architecture Specification - 248 pages",
                        "Competitive Analysis Report - Comparison with 18 competitors",
                        "Patent Application #PA-2024-0342 (Multi-Modal Transformer)",
                        "Patent Application #PA-2024-0567 (Adaptive Learning System)",
                        "Customer Advisory Board Feedback - 35 enterprise customers",
                        "Independent Benchmark Study - Stanford NLP Lab",
                        "Performance Validation Report - KPMG Technology Assessment"
                    ]
                },

                "technological_nature": {
                    "score": 95,
                    "status": "qualified",
                    "answer": """
TECHNOLOGICAL NATURE ANALYSIS - HARD SCIENCE FOUNDATIONS

The Aura AI Document Processing Platform is fundamentally grounded in the principles of
COMPUTER SCIENCE, MATHEMATICS, and ENGINEERING as defined under IRC Section 41(d)(1).

I. COMPUTER SCIENCE FOUNDATIONS:

1. MACHINE LEARNING & ARTIFICIAL INTELLIGENCE:

   a) Deep Learning Architectures:
      - Transformer neural networks with multi-head self-attention mechanisms
      - Vision Transformers (ViT) for layout analysis with patch embeddings
      - BERT/RoBERTa architectures for text understanding with fine-tuning
      - Custom encoder-decoder architectures for sequence-to-sequence tasks

   b) Learning Algorithms:
      - Supervised learning: Cross-entropy loss, focal loss for class imbalance
      - Self-supervised learning: Masked language modeling, contrastive learning
      - Reinforcement learning: RLHF for model alignment
      - Meta-learning: MAML for few-shot document type adaptation

   c) Optimization Techniques:
      - Adam optimizer with warmup and linear decay
      - Gradient accumulation for large batch training
      - Mixed precision training (FP16/BF16) for efficiency
      - Distributed training across GPU clusters

2. NATURAL LANGUAGE PROCESSING:

   a) Text Processing:
      - Subword tokenization (BPE, SentencePiece)
      - Contextual embeddings and positional encodings
      - Attention mechanisms for long-range dependencies

   b) Information Extraction:
      - Named Entity Recognition with CRF decoding layer
      - Relation extraction using graph neural networks
      - Coreference resolution for entity linking

   c) Semantic Understanding:
      - Semantic similarity using sentence embeddings
      - Question answering for document queries
      - Text classification with hierarchical labels

3. COMPUTER VISION:

   a) Document Image Analysis:
      - Convolutional Neural Networks for feature extraction
      - Object detection (YOLO, Faster R-CNN) for table/figure detection
      - Semantic segmentation for layout analysis

   b) OCR Enhancement:
      - Deep learning-based character recognition
      - Attention-based sequence modeling for text line recognition
      - Handwriting recognition with LSTM/Transformer hybrid models

II. MATHEMATICAL FOUNDATIONS:

1. LINEAR ALGEBRA:
   - Matrix operations for neural network computations
   - Eigenvalue decomposition for dimensionality reduction
   - Singular Value Decomposition (SVD) for matrix factorization

2. PROBABILITY & STATISTICS:
   - Bayesian inference for confidence estimation
   - Maximum likelihood estimation for model training
   - Monte Carlo methods for uncertainty quantification
   - Statistical hypothesis testing for model evaluation

3. GRAPH THEORY:
   - Graph algorithms for document structure representation
   - Shortest path algorithms for entity linking
   - Graph neural networks for relational reasoning

4. OPTIMIZATION THEORY:
   - Convex optimization for loss function minimization
   - Gradient descent and variants (SGD, Adam, AdaGrad)
   - Constraint optimization for inference decoding

III. ENGINEERING DISCIPLINES:

1. SOFTWARE ENGINEERING:
   - Microservices architecture with Kubernetes orchestration
   - Event-driven processing with Apache Kafka
   - Database optimization with vector similarity search (Pinecone, Milvus)

2. SYSTEMS ENGINEERING:
   - Distributed systems design for horizontal scalability
   - Load balancing and auto-scaling strategies
   - Fault tolerance and disaster recovery

IV. TEAM QUALIFICATIONS:

Our technical team includes:
- 15 Ph.D.s in Computer Science, Machine Learning, and Computational Linguistics
- 8 researchers from top AI labs (Google Brain, OpenAI, DeepMind alumni)
- 12 published papers in top-tier venues (NeurIPS, ICML, ACL, CVPR)
- 3 patent holders in document processing technology

CONCLUSION: The project is fundamentally technological in nature, relying entirely on
principles of computer science, mathematics, and engineering. No business, economic,
or social science principles are involved in resolving the technical uncertainties.
                    """.strip(),
                    "evidence": [
                        "Algorithm Design Documents - 24 technical specifications",
                        "PhD Team Credentials - CVs and Publication Records (32 publications)",
                        "Conference Papers: NeurIPS 2024, ICML 2024, ACL 2024 (under review)",
                        "Technical Training Records - Advanced ML Engineering Curriculum",
                        "Architecture Decision Records (ADRs) - 78 documented decisions",
                        "Code Repository Documentation - 150K+ lines of ML code",
                        "External Review: MIT CSAIL Technical Assessment - March 2024",
                        "Patent Prior Art Search Reports"
                    ]
                },

                "elimination_of_uncertainty": {
                    "score": 93,
                    "status": "qualified",
                    "answer": """
ELIMINATION OF UNCERTAINTY ANALYSIS

At project inception in January 2024, substantial TECHNOLOGICAL UNCERTAINTY existed regarding
the capability, method, and design of the proposed system. These uncertainties could NOT be
resolved through routine engineering, standard practice, or expert consultation.

I. CAPABILITY UNCERTAINTIES:

1. ACCURACY TARGETS:

   UNCERTAINTY: Can a unified model architecture achieve 98.5% extraction accuracy across
   50+ diverse document types, including handwritten annotations?

   - State of the art at project start: 85-90% on standardized benchmarks
   - Academic best results: 92% on clean, typed documents only
   - Our real-world data includes: multi-column layouts, tables spanning pages,
     handwritten notes, stamps, watermarks, poor scan quality

   WHY THIS WAS UNCERTAIN:
   - No published research demonstrated this accuracy level on comparable document complexity
   - Internal POC achieved only 78% accuracy on real customer documents
   - Experts we consulted (Stanford NLP Lab) indicated uncertainty about achievability

2. THROUGHPUT REQUIREMENTS:

   UNCERTAINTY: Can we achieve 100,000+ documents per hour while maintaining accuracy?

   - Existing solutions process ~1,000 docs/hour with acceptable accuracy
   - GPU memory constraints limit batch sizes for large documents
   - Latency requirements (<100ms/page) conflict with model complexity

   TECHNICAL CHALLENGES:
   - Model inference optimization without accuracy degradation
   - Efficient batching strategies for variable-length documents
   - GPU utilization optimization across heterogeneous workloads

3. GENERALIZATION:

   UNCERTAINTY: Can the system handle never-seen document formats without retraining?

   - Zero-shot generalization to new document types was unproven
   - Transfer learning effectiveness for financial documents was unknown
   - Few-shot learning with <100 examples for new types was aspirational

II. METHOD/METHODOLOGY UNCERTAINTIES:

1. ARCHITECTURE SELECTION:

   Multiple viable approaches existed, with unknown tradeoffs:
   - LayoutLM vs. Donut vs. UDOP vs. custom architectures
   - Each had different accuracy/speed/memory characteristics
   - Optimal choice for our requirements was unknown

   EXPERIMENTS REQUIRED:
   - Benchmark all architectures on our proprietary dataset
   - Measure accuracy, speed, memory across 50+ document types
   - Evaluate fine-tuning difficulty and transfer learning capability

2. MULTIMODAL FUSION:

   UNCERTAINTY: How to optimally combine visual, textual, and structural features?

   - Early fusion vs. late fusion vs. cross-attention approaches
   - Relative weighting of modalities was unknown
   - Impact of fusion strategy on downstream accuracy was unpredictable

   APPROACHES EVALUATED:
   - Concatenation-based early fusion
   - Cross-modal attention mechanisms
   - Hierarchical fusion with modality-specific encoders

3. TRAINING DATA STRATEGY:

   UNCERTAINTY: What training data composition yields best generalization?

   - Ratio of real vs. synthetic data was unknown
   - Augmentation strategies for document images needed exploration
   - Curriculum learning effectiveness for document types was uncertain

III. DESIGN UNCERTAINTIES:

1. MODEL ARCHITECTURE DETAILS:
   - Number of transformer layers (6, 12, 24, or more?)
   - Hidden dimension size vs. inference speed tradeoff
   - Attention head configuration for document structure

2. INFERENCE PIPELINE DESIGN:
   - Preprocessing steps and their impact on accuracy
   - Post-processing algorithms for output refinement
   - Confidence calibration methods

3. DEPLOYMENT ARCHITECTURE:
   - Cloud vs. edge deployment for latency requirements
   - Model serving infrastructure at scale
   - A/B testing framework for continuous improvement

IV. RESOLUTION APPROACH:

These uncertainties required SYSTEMATIC EXPERIMENTATION - not routine development:
- 247 tracked experiments in MLflow
- 52 documented failed approaches
- 7 major architecture pivots
- 18 months of iterative development

CONCLUSION: Substantial technological uncertainty existed at project start regarding
whether we could achieve our performance targets, what methods would work, and how to
design the system. These uncertainties were resolved through systematic experimentation,
not routine engineering or application of known techniques.
                    """.strip(),
                    "evidence": [
                        "Initial Feasibility Study - 47 documented uncertainties",
                        "Technical Risk Assessment Matrix - Risk Register v3",
                        "Failed Experiment Log - 52 documented unsuccessful approaches",
                        "Architecture Decision Records - Evaluated alternatives",
                        "Weekly R&D Status Reports - Uncertainty tracking",
                        "External Consultant Reports (McKinsey, BCG) - Risk Assessments",
                        "Internal Technical Review Board Minutes - 24 meetings",
                        "Competitive Intelligence Report - Technology Gap Analysis"
                    ]
                },

                "process_of_experimentation": {
                    "score": 92,
                    "status": "qualified",
                    "answer": """
PROCESS OF EXPERIMENTATION ANALYSIS

The development team followed a rigorous SYSTEMATIC PROCESS OF EXPERIMENTATION to evaluate
and eliminate technical uncertainties, as required under IRC Section 41(d)(1)(C).

I. HYPOTHESIS-DRIVEN DEVELOPMENT:

Each technical uncertainty was formulated as a testable hypothesis with clear success criteria:

EXAMPLE HYPOTHESES:

H1: "A LayoutLMv3 architecture can achieve >95% extraction accuracy on tax form 1040
    with inference latency <200ms on a single V100 GPU"
    - Success Criteria: F1 > 0.95, P99 latency < 200ms
    - Result: REJECTED (accuracy 91.2%, latency 340ms)
    - Learning: Need custom architecture for our accuracy/speed requirements

H2: "Cross-modal attention between visual and textual encoders improves table extraction
    accuracy by >5% compared to late fusion approaches"
    - Success Criteria: Table F1 improvement >= 5%
    - Result: CONFIRMED (7.3% improvement observed)
    - Learning: Cross-attention adopted for final architecture

H3: "Synthetic data augmentation can improve model robustness to scan quality variations
    by >10% on degraded document test set"
    - Success Criteria: Accuracy on degraded set improves >= 10%
    - Result: PARTIALLY CONFIRMED (8.2% improvement)
    - Learning: Augmentation helps but real degraded samples still needed

II. SYSTEMATIC EXPERIMENTATION:

1. EXPERIMENT TRACKING SYSTEM:
   - All experiments tracked in MLflow with versioned configurations
   - 247 experiments conducted over 12 months
   - Each experiment documented with:
     * Hypothesis being tested
     * Experimental configuration (model, data, hyperparameters)
     * Evaluation metrics and results
     * Conclusions and next steps
     * Links to code commits and artifacts

2. EXPERIMENTAL VARIABLES EXPLORED:

   Model Architecture Experiments (67 experiments):
   - 8 base architectures evaluated (LayoutLM, Donut, UDOP, custom, etc.)
   - 12 attention mechanism variations
   - 6 encoder configurations
   - 15 fusion strategy combinations

   Training Strategy Experiments (89 experiments):
   - 5 learning rate schedules
   - 8 batch size configurations
   - 12 data augmentation combinations
   - 7 curriculum learning strategies
   - 6 loss function variations

   Optimization Experiments (54 experiments):
   - 4 quantization approaches
   - 6 pruning strategies
   - 8 inference optimization techniques
   - 5 batching strategies

3. CONTROLLED EXPERIMENTAL DESIGN:
   - Held-out test sets for unbiased evaluation
   - Cross-validation for hyperparameter tuning
   - Statistical significance testing (p < 0.05)
   - Ablation studies to isolate factor contributions

III. MODELING AND SIMULATION:

1. PERFORMANCE MODELING:
   - Mathematical models of inference latency vs. model size
   - Memory consumption prediction for different architectures
   - Throughput simulation under various load patterns

2. SYNTHETIC DATA GENERATION:
   - Document layout simulation for training data augmentation
   - Noise injection models for scan quality variation
   - Font and handwriting synthesis for text diversity

3. A/B TESTING FRAMEWORK:
   - Production shadow testing for new model versions
   - Statistical analysis of accuracy differences
   - Confidence intervals for metric estimates

IV. PROTOTYPE ITERATIONS:

Major Prototype Versions:
- v0.1 (Feb 2024): Baseline LayoutLM implementation - 78% accuracy
- v0.2 (Apr 2024): Custom architecture v1 - 84% accuracy
- v0.3 (Jun 2024): Multi-modal fusion added - 89% accuracy
- v0.4 (Aug 2024): Attention optimization - 93% accuracy
- v0.5 (Oct 2024): Production optimization - 96% accuracy
- v1.0 (Dec 2024): Final release candidate - 98.2% accuracy

Each prototype underwent:
- Comprehensive benchmark testing (50+ document types)
- User acceptance testing with pilot customers
- Performance profiling and optimization
- Security and reliability testing

V. FAILURE ANALYSIS:

Documented failures and learnings:

1. ARCHITECTURE FAILURES:
   - Donut architecture: Insufficient accuracy (abandoned after 3 months)
   - Pure CNN approach: Could not capture long-range dependencies
   - RNN-based sequence models: Too slow for production requirements

2. TRAINING FAILURES:
   - Self-supervised pretraining: Insufficient benefit for our data
   - Multi-task learning: Negative transfer between document types
   - Large batch training: Convergence issues without careful tuning

3. OPTIMIZATION FAILURES:
   - INT8 quantization: Unacceptable accuracy loss (2.3%)
   - Knowledge distillation: Student model underperformed
   - Dynamic batching: Latency variance too high

VI. DOCUMENTATION AND REPRODUCIBILITY:

All experiments are:
- Version-controlled in Git with experiment branches
- Documented in Jupyter notebooks with explanations
- Logged in MLflow with full artifact tracking
- Peer-reviewed before conclusions drawn
- Reproducible with provided scripts and seeds

CONCLUSION: The project followed a systematic process of experimentation involving:
- Hypothesis formulation and testing
- Controlled experiments with statistical rigor
- Mathematical modeling and simulation
- Iterative prototyping with measurable improvements
- Comprehensive failure analysis and learning

This systematic approach distinguishes our work from routine software development.
                    """.strip(),
                    "evidence": [
                        "MLflow Experiment Tracking Dashboard - 247 experiments",
                        "Jupyter Notebooks - 156 documented experiments",
                        "A/B Test Reports - 23 comparative studies",
                        "Prototype Version History and Release Notes",
                        "Failed Experiment Post-Mortem Reports - 52 documents",
                        "Peer Review Documentation - 89 experiment reviews",
                        "Git Commit History - 3,400+ commits with experiment tags",
                        "Weekly Experiment Review Meeting Minutes - 48 meetings"
                    ]
                }
            },

            "metrics": {
                "total_employees": 210,
                "total_qre": Decimal("16200000"),
                "wage_qre": Decimal("12500000"),
                "supply_qre": Decimal("1800000"),
                "contract_qre": Decimal("1900000"),
                "experiments_conducted": 247,
                "papers_published": 5,
                "patents_filed": 3
            }
        }

        # Project 2: Predictive Analytics Engine
        project2 = {
            "id": str(uuid4()),
            "name": "Aura Predict - Advanced Financial Anomaly Detection System",
            "code": "AURA-PRED-2024",
            "description": """
Development of a sophisticated machine learning system for real-time financial anomaly detection
and predictive analytics. The system analyzes transaction patterns, identifies unusual activities,
and predicts potential issues before they materialize. This represents cutting-edge research in
time-series analysis, graph neural networks, and explainable AI for financial applications.

KEY TECHNICAL OBJECTIVES:
- Detect 99%+ of financial anomalies with <1% false positive rate
- Process 10M+ transactions per second in real-time streaming mode
- Provide explainable predictions with human-interpretable reasoning
- Adapt to new fraud patterns within 24 hours of detection
- Support multi-entity analysis with graph-based relationship modeling
            """.strip(),
            "department": "Advanced Research",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "project_lead": "Dr. Michael Rodriguez, Ph.D. - Director of Applied ML",
            "total_budget": Decimal("12000000"),
            "qualification_status": "qualified",
            "overall_score": 91,
            "cpa_reviewed": True,
            "cpa_approved": True,
            "cpa_approval_date": date.today().isoformat(),
            "cpa_notes": "Strong 4-Part Test qualification with innovative ML approaches.",

            "four_part_test": {
                "permitted_purpose": {
                    "score": 93,
                    "status": "qualified",
                    "answer": """
PERMITTED PURPOSE - AURA PREDICT ANOMALY DETECTION SYSTEM

The Aura Predict system qualifies as research undertaken to develop a NEW business component
with substantially IMPROVED functionality, performance, and reliability.

I. NEW CAPABILITIES BEING DEVELOPED:

1. REAL-TIME STREAMING ANOMALY DETECTION:
   - Process 10M+ transactions/second with sub-millisecond latency
   - Continuous learning that adapts to new patterns without retraining
   - Multi-dimensional anomaly scoring across 200+ features
   - No existing solution achieves this combination of throughput and accuracy

2. GRAPH-BASED ENTITY ANALYSIS:
   - Novel graph neural network architecture for relationship modeling
   - Identifies anomalies based on entity networks, not just individual transactions
   - Detects collusion and coordinated fraud patterns
   - Represents a fundamental advance over transaction-level analysis

3. EXPLAINABLE AI FOR COMPLIANCE:
   - Every prediction includes human-readable explanation
   - Counterfactual analysis: "What would need to change to be normal?"
   - Audit trail with full reasoning transparency
   - Critical for regulatory compliance (SOX, GDPR)

4. ADAPTIVE LEARNING SYSTEM:
   - Detects concept drift in real-time
   - Automatic model updates without service interruption
   - Transfer learning for rapid adaptation to new entity types

II. SUBSTANTIAL IMPROVEMENTS:

| Capability              | Current State-of-Art | Aura Predict | Improvement |
|-------------------------|---------------------|--------------|-------------|
| Detection Rate          | 85-90%              | 99%+         | +10-15%     |
| False Positive Rate     | 5-10%               | <1%          | 5-10x       |
| Processing Throughput   | 100K tx/sec         | 10M tx/sec   | 100x        |
| Adaptation Time         | Weeks/Months        | 24 hours     | 10-30x      |
| Explanation Quality     | None/Limited        | Full         | N/A (new)   |

These improvements are substantial, not incremental refinements.
                    """.strip(),
                    "evidence": [
                        "Product Requirements Document v2.3",
                        "Competitive Analysis - 12 vendor comparison",
                        "Patent Application #PA-2024-0891 (Graph Anomaly Detection)",
                        "Customer Requirements Analysis - 28 enterprise clients"
                    ]
                },

                "technological_nature": {
                    "score": 94,
                    "status": "qualified",
                    "answer": """
TECHNOLOGICAL NATURE - SCIENTIFIC FOUNDATIONS

The Aura Predict system relies on principles of COMPUTER SCIENCE, MATHEMATICS, and ENGINEERING:

I. MACHINE LEARNING (Computer Science):
- Graph Neural Networks (GNN) for entity relationship modeling
- Temporal Convolutional Networks for time-series analysis
- Variational Autoencoders for anomaly scoring
- Online learning algorithms for continuous adaptation

II. MATHEMATICS:
- Spectral graph theory for network analysis
- Probability distributions for anomaly scoring
- Optimization theory for real-time inference
- Information theory for feature selection

III. SYSTEMS ENGINEERING:
- Distributed stream processing (Apache Kafka, Flink)
- Low-latency inference optimization
- Horizontal scaling architecture

Team: 8 Ph.D.s in ML/Statistics, 5 published papers in anomaly detection.
                    """.strip(),
                    "evidence": [
                        "Algorithm Specifications - 15 technical documents",
                        "Team Credentials and Publications",
                        "Conference Submissions (KDD 2024, ICDM 2024)"
                    ]
                },

                "elimination_of_uncertainty": {
                    "score": 90,
                    "status": "qualified",
                    "answer": """
ELIMINATION OF UNCERTAINTY - TECHNICAL UNKNOWNS

Significant uncertainty existed at project start:

1. CAPABILITY UNCERTAINTY:
   - Can we achieve 99% detection with <1% false positives simultaneously?
   - Can the system scale to 10M transactions/second?
   - Can explanations be generated without impacting latency?

2. METHOD UNCERTAINTY:
   - Which GNN architecture best captures financial entity relationships?
   - How to combine temporal and graph-based features optimally?
   - What online learning approach adapts fastest to drift?

3. DESIGN UNCERTAINTY:
   - How to partition graph processing across distributed nodes?
   - Optimal explanation granularity for different user types?

These could not be resolved through standard practice or expert consultation.
                    """.strip(),
                    "evidence": [
                        "Feasibility Study - 31 uncertainties documented",
                        "Risk Assessment Report",
                        "Expert Consultation Records"
                    ]
                },

                "process_of_experimentation": {
                    "score": 89,
                    "status": "qualified",
                    "answer": """
PROCESS OF EXPERIMENTATION - SYSTEMATIC APPROACH

We conducted rigorous experimentation:

1. HYPOTHESIS TESTING:
   - 156 tracked experiments in MLflow
   - Each with defined hypothesis and success criteria
   - Statistical significance testing for all comparisons

2. ARCHITECTURE EXPLORATION:
   - 6 GNN architectures evaluated
   - 4 temporal modeling approaches
   - 8 combination strategies

3. PROTOTYPE ITERATIONS:
   - 5 major versions with measurable improvements
   - Comprehensive benchmarking on proprietary datasets
   - A/B testing in shadow mode

4. FAILURE ANALYSIS:
   - 38 documented failed approaches
   - Post-mortem analysis and learnings captured

This systematic process distinguishes our work from routine development.
                    """.strip(),
                    "evidence": [
                        "MLflow Tracking - 156 experiments",
                        "Prototype Version History",
                        "Failed Experiment Documentation"
                    ]
                }
            },

            "metrics": {
                "total_employees": 85,
                "total_qre": Decimal("9800000"),
                "wage_qre": Decimal("7200000"),
                "supply_qre": Decimal("1400000"),
                "contract_qre": Decimal("1200000"),
                "experiments_conducted": 156,
                "papers_published": 3,
                "patents_filed": 2
            }
        }

        # Project 3: Automated Compliance Engine
        project3 = {
            "id": str(uuid4()),
            "name": "Aura Comply - Intelligent Regulatory Compliance Automation",
            "code": "AURA-COMP-2024",
            "description": """
Research and development of an AI-powered regulatory compliance engine that automatically
interprets regulatory requirements, maps them to business processes, and generates compliance
evidence. The system uses advanced NLP to understand complex regulatory text and reason about
compliance obligations.

KEY TECHNICAL OBJECTIVES:
- Parse and understand 10,000+ regulatory requirements across jurisdictions
- Automatically map requirements to business controls with 95%+ accuracy
- Generate audit evidence and compliance reports automatically
- Detect regulatory changes and assess impact within 48 hours
- Support multi-jurisdictional compliance (US, EU, UK, APAC)
            """.strip(),
            "department": "Innovation Lab",
            "start_date": "2024-03-01",
            "end_date": "2024-12-31",
            "project_lead": "Dr. Emily Watson, J.D., Ph.D. - Chief Compliance Scientist",
            "total_budget": Decimal("8000000"),
            "qualification_status": "qualified",
            "overall_score": 89,
            "cpa_reviewed": True,
            "cpa_approved": True,
            "cpa_approval_date": date.today().isoformat(),
            "cpa_notes": "Innovative application of NLP to regulatory compliance.",

            "four_part_test": {
                "permitted_purpose": {
                    "score": 91,
                    "status": "qualified",
                    "answer": """
PERMITTED PURPOSE - AURA COMPLY REGULATORY ENGINE

I. NEW CAPABILITIES:

1. REGULATORY TEXT UNDERSTANDING:
   - Novel legal NLP models trained on 50K+ regulatory documents
   - Semantic parsing of complex conditional requirements
   - Cross-reference resolution across documents and jurisdictions
   - No existing solution handles regulatory complexity at this level

2. AUTOMATIC CONTROL MAPPING:
   - AI-driven mapping of requirements to business controls
   - Probabilistic matching with confidence scores
   - Gap analysis with remediation suggestions

3. EVIDENCE GENERATION:
   - Automatic collection of compliance evidence
   - Intelligent report generation with regulatory citations
   - Audit-ready documentation

II. IMPROVEMENTS:

| Metric                  | Manual Process | Aura Comply | Improvement |
|-------------------------|----------------|-------------|-------------|
| Requirement Analysis    | 2-4 weeks      | 2-4 hours   | 20-40x      |
| Control Mapping         | 80% accuracy   | 95%+        | +15%        |
| Change Impact Analysis  | 1-2 weeks      | 48 hours    | 5-7x        |
                    """.strip(),
                    "evidence": [
                        "Product Requirements Document",
                        "Regulatory Dataset Documentation",
                        "Patent Application #PA-2024-1023"
                    ]
                },

                "technological_nature": {
                    "score": 92,
                    "status": "qualified",
                    "answer": """
TECHNOLOGICAL NATURE - LEGAL NLP FOUNDATIONS

The system relies on:

1. NATURAL LANGUAGE PROCESSING:
   - Custom BERT models fine-tuned on legal text
   - Semantic role labeling for obligation extraction
   - Discourse parsing for document structure
   - Knowledge graph construction for cross-references

2. KNOWLEDGE REPRESENTATION:
   - Ontology development for regulatory domains
   - Logical reasoning over compliance rules
   - Temporal logic for deadline tracking

3. MACHINE LEARNING:
   - Multi-label classification for requirement categorization
   - Similarity learning for control mapping
   - Active learning for continuous improvement

Team includes 4 Ph.D.s (2 in Computational Linguistics, 2 in ML).
                    """.strip(),
                    "evidence": [
                        "Algorithm Design Documents",
                        "Legal NLP Model Documentation",
                        "Team Credentials"
                    ]
                },

                "elimination_of_uncertainty": {
                    "score": 88,
                    "status": "qualified",
                    "answer": """
ELIMINATION OF UNCERTAINTY

1. CAPABILITY UNCERTAINTY:
   - Can NLP accurately parse complex regulatory language?
   - Can we achieve 95% control mapping accuracy automatically?
   - Can the system handle multi-jurisdictional requirements?

2. METHOD UNCERTAINTY:
   - Which NLP architecture best captures legal semantics?
   - How to represent regulatory knowledge for reasoning?
   - What training data strategy yields best generalization?

These required systematic experimentation to resolve.
                    """.strip(),
                    "evidence": [
                        "Feasibility Study",
                        "Technical Risk Assessment"
                    ]
                },

                "process_of_experimentation": {
                    "score": 87,
                    "status": "qualified",
                    "answer": """
PROCESS OF EXPERIMENTATION

1. SYSTEMATIC EXPERIMENTS:
   - 98 tracked experiments in MLflow
   - 4 NLP architectures evaluated
   - 6 knowledge representation approaches tested

2. PROTOTYPE ITERATIONS:
   - 4 major versions developed
   - Validation with compliance officers at 15 enterprises

3. FAILURE DOCUMENTATION:
   - 24 failed approaches documented with learnings
                    """.strip(),
                    "evidence": [
                        "MLflow Experiment Logs",
                        "Prototype Documentation",
                        "User Validation Reports"
                    ]
                }
            },

            "metrics": {
                "total_employees": 45,
                "total_qre": Decimal("6500000"),
                "wage_qre": Decimal("4800000"),
                "supply_qre": Decimal("900000"),
                "contract_qre": Decimal("800000"),
                "experiments_conducted": 98,
                "papers_published": 2,
                "patents_filed": 1
            }
        }

        projects.append(project1)
        projects.append(project2)
        projects.append(project3)

        return projects

    def generate_employees(self, count: int = 750) -> List[Dict[str, Any]]:
        """Generate employees distributed across CA and PA."""
        employees = []

        for i in range(count):
            state = self.get_state_for_index(i, count)

            rand = random.random()
            if rand < 0.12:
                qualified_pct = 100.0
            elif rand < 0.32:
                qualified_pct = 80.0
            elif rand < 0.55:
                qualified_pct = random.uniform(50.0, 75.0)
            elif rand < 0.80:
                qualified_pct = random.uniform(25.0, 50.0)
            else:
                qualified_pct = random.uniform(5.0, 25.0)

            title = random.choice(self.JOB_TITLES)
            base_salary = self._get_base_salary(title)

            if state == "CA":
                base_salary *= 1.25
            elif state == "PA":
                base_salary *= 1.0

            total_wages = Decimal(str(round(base_salary, 2)))
            qualified_wages = total_wages * Decimal(str(qualified_pct / 100))

            employee = {
                "id": str(uuid4()),
                "employee_id": self.generate_employee_id(),
                "name": self.generate_name(),
                "title": title,
                "department": random.choice(self.DEPARTMENTS),
                "state": state,
                "total_wages": total_wages,
                "w2_wages": total_wages,
                "qualified_time_percentage": round(qualified_pct, 1),
                "qualified_wages": round(qualified_wages, 2),
                "qualified_time_source": random.choice([
                    "timesheet", "project_tracking", "manager_estimate", "jira_analysis"
                ]),
                "cpa_reviewed": qualified_pct >= 80.0,
                "hire_date": self._random_date(2015, 2024).isoformat(),
                "role_description": self._get_role_description(title)
            }

            employees.append(employee)

        return employees

    def generate_subcontractors(self, count: int = 350) -> List[Dict[str, Any]]:
        """Generate subcontractor/contract research expenses."""
        contracts = []

        categories = list(self.SUBCONTRACTORS.keys())

        for i in range(count):
            state = self.get_state_for_index(i, count)
            category = random.choice(categories)
            provider = random.choice(self.SUBCONTRACTORS[category])

            is_qualified_org = any(x in provider for x in [
                "MIT", "Stanford", "Berkeley", "CalTech", "Carnegie",
                "UCLA", "Penn State", "University", "Drexel", "Temple"
            ])

            # Subcontractor amounts
            if category == "research_institutions":
                amount = Decimal(str(random.uniform(25000, 750000)))
            elif category == "specialized_contractors":
                amount = Decimal(str(random.uniform(50000, 500000)))
            else:
                amount = Decimal(str(random.uniform(15000, 300000)))

            qualified_pct = 0.75 if is_qualified_org else 0.65
            qualified_amount = amount * Decimal(str(qualified_pct))

            contract = {
                "id": str(uuid4()),
                "contractor_name": provider,
                "description": self._generate_contract_description(category),
                "state": state,
                "category": "subcontractor",
                "subcategory": category,
                "gross_amount": round(amount, 2),
                "is_qualified_research_org": is_qualified_org,
                "qualified_percentage": qualified_pct * 100,
                "qualified_amount": round(qualified_amount, 2),
                "contract_date": self._random_date(2024, 2024).isoformat(),
                "contract_number": f"SUB-{2024}-{i+1:04d}",
                "us_performed": True,
                "evidence": ["Signed Contract", "Statement of Work", "Invoices", "Deliverables"]
            }

            contracts.append(contract)

        return contracts

    def generate_supplies(self, count: int = 500) -> List[Dict[str, Any]]:
        """Generate supply expenses (excluding computer supplies)."""
        supplies = []

        supply_categories = {
            "cloud_computing": {
                "min_amount": 500,
                "max_amount": 200000,
                "descriptions": [
                    "GPU compute instances for ML training",
                    "Cloud storage for training datasets",
                    "Kubernetes cluster hosting",
                    "Data processing and ETL services",
                    "ML model serving infrastructure",
                    "Development environment hosting"
                ]
            },
            "software_licenses": {
                "min_amount": 200,
                "max_amount": 75000,
                "descriptions": [
                    "Development IDE licenses",
                    "Version control and CI/CD platform",
                    "Project management tools",
                    "Code quality and security scanning",
                    "Database management tools"
                ]
            },
            "monitoring_tools": {
                "min_amount": 1000,
                "max_amount": 100000,
                "descriptions": [
                    "Application performance monitoring",
                    "Log aggregation and analysis",
                    "Error tracking and alerting",
                    "Infrastructure monitoring",
                    "ML model monitoring"
                ]
            },
            "research_supplies": {
                "min_amount": 100,
                "max_amount": 50000,
                "descriptions": [
                    "Laboratory consumables",
                    "Testing materials and samples",
                    "Prototype materials",
                    "Research equipment supplies",
                    "Calibration standards"
                ]
            }
        }

        for i in range(count):
            state = self.get_state_for_index(i, count)
            category_name = random.choice(list(supply_categories.keys()))
            category = supply_categories[category_name]
            vendor = random.choice(self.SUPPLY_VENDORS.get(category_name, ["Generic Vendor"]))
            description = random.choice(category["descriptions"])
            amount = Decimal(str(random.uniform(category["min_amount"], category["max_amount"])))

            qualified_pct = random.choice([100, 100, 100, 100, 90, 85, 80])
            qualified_amount = amount * Decimal(str(qualified_pct / 100))

            supply = {
                "id": str(uuid4()),
                "category": "supplies",
                "subcategory": category_name,
                "supply_description": description,
                "supply_vendor": vendor,
                "state": state,
                "gl_account": self._generate_gl_account(category_name),
                "gross_amount": round(amount, 2),
                "qualified_percentage": qualified_pct,
                "qualified_amount": round(qualified_amount, 2),
                "invoice_date": self._random_date(2024, 2024).isoformat(),
                "invoice_number": f"INV-{vendor[:3].upper()}-{i+1:05d}",
                "evidence": ["Invoice", "Purchase Order", "GL Entry"]
            }

            supplies.append(supply)

        return supplies

    def generate_computer_supplies(self, count: int = 300) -> List[Dict[str, Any]]:
        """Generate computer supplies and rental expenses."""
        computer_supplies = []

        computer_categories = {
            "hardware_purchase": {
                "vendors": ["Dell Technologies", "HP Enterprise", "Lenovo", "Apple"],
                "min_amount": 1500,
                "max_amount": 15000,
                "descriptions": [
                    "Development workstation",
                    "High-performance laptop",
                    "Server hardware components",
                    "Network equipment",
                    "Testing devices"
                ]
            },
            "gpu_hardware": {
                "vendors": ["NVIDIA", "AMD", "Intel"],
                "min_amount": 5000,
                "max_amount": 50000,
                "descriptions": [
                    "GPU accelerator cards for ML training",
                    "AI development hardware",
                    "Deep learning workstation",
                    "GPU cluster components",
                    "Inference accelerators"
                ]
            },
            "hardware_rental": {
                "vendors": ["Dell Technologies", "HP Enterprise", "NVIDIA"],
                "min_amount": 2000,
                "max_amount": 100000,
                "descriptions": [
                    "GPU server rental for ML experiments",
                    "Development workstation leases",
                    "Testing lab equipment rental",
                    "High-performance computing rental",
                    "AI infrastructure rental"
                ]
            },
            "peripherals": {
                "vendors": ["Dell Technologies", "HP Enterprise", "Lenovo", "Apple"],
                "min_amount": 200,
                "max_amount": 5000,
                "descriptions": [
                    "Monitors for development",
                    "External storage devices",
                    "Networking accessories",
                    "Testing peripherals",
                    "Development accessories"
                ]
            }
        }

        for i in range(count):
            state = self.get_state_for_index(i, count)
            category_name = random.choice(list(computer_categories.keys()))
            category = computer_categories[category_name]
            vendor = random.choice(category["vendors"])
            description = random.choice(category["descriptions"])
            amount = Decimal(str(random.uniform(category["min_amount"], category["max_amount"])))

            qualified_pct = random.choice([100, 100, 100, 95, 90, 85])
            qualified_amount = amount * Decimal(str(qualified_pct / 100))

            computer_supply = {
                "id": str(uuid4()),
                "category": "computer_supplies",
                "subcategory": category_name,
                "supply_description": description,
                "supply_vendor": vendor,
                "state": state,
                "gl_account": self._generate_gl_account("computer_" + category_name),
                "gross_amount": round(amount, 2),
                "qualified_percentage": qualified_pct,
                "qualified_amount": round(qualified_amount, 2),
                "invoice_date": self._random_date(2024, 2024).isoformat(),
                "invoice_number": f"COMP-{vendor[:3].upper()}-{i+1:05d}",
                "evidence": ["Invoice", "Purchase Order", "Asset Tag", "GL Entry"]
            }

            computer_supplies.append(computer_supply)

        return computer_supplies

    def _get_base_salary(self, title: str) -> float:
        if "Director" in title or "Principal" in title:
            return random.uniform(220000, 380000)
        elif "Senior" in title or "Staff" in title or "Lead" in title:
            return random.uniform(160000, 250000)
        elif "Manager" in title or "Architect" in title:
            return random.uniform(180000, 280000)
        elif "Ph.D" in title or "Scientist" in title:
            return random.uniform(170000, 300000)
        else:
            return random.uniform(100000, 180000)

    def _get_role_description(self, title: str) -> str:
        descriptions = {
            "Software Engineer": "Develops and implements software solutions for R&D projects",
            "Senior Software Engineer": "Leads technical implementation and mentors junior engineers",
            "Staff Engineer": "Provides technical leadership across multiple R&D initiatives",
            "Principal Engineer": "Defines technical strategy and architecture for R&D platform",
            "Data Scientist": "Develops ML models and analyzes experimental data",
            "Machine Learning Engineer": "Implements and optimizes machine learning systems",
            "Research Scientist": "Conducts fundamental research and experimental analysis",
            "AI Research Scientist": "Leads cutting-edge AI/ML research initiatives",
            "Computer Vision Engineer": "Develops image and video analysis algorithms",
            "NLP Engineer": "Builds natural language processing systems",
            "DevOps Engineer": "Builds infrastructure for R&D experimentation",
            "Engineering Manager": "Manages R&D engineering teams and resources",
            "R&D Director": "Directs overall R&D strategy and execution"
        }
        return descriptions.get(title, "Contributes to R&D activities")

    def _generate_contract_description(self, category: str) -> str:
        descriptions = {
            "research_institutions": [
                "Academic research collaboration on ML algorithms",
                "University partnership for advanced AI research",
                "Research grant for document understanding studies",
                "Joint research project on computer vision techniques"
            ],
            "consulting_firms": [
                "Technical consulting for architecture design",
                "Expert review of ML model performance",
                "Strategic advisory for R&D roadmap",
                "Technology assessment and benchmarking"
            ],
            "specialized_contractors": [
                "Custom ML model development",
                "AI infrastructure optimization",
                "Specialized algorithm implementation",
                "Advanced feature engineering services"
            ],
            "engineering_firms": [
                "Systems integration consulting",
                "Performance optimization services",
                "Security and compliance assessment",
                "Scalability architecture review"
            ]
        }
        return random.choice(descriptions.get(category, ["Research and development services"]))

    def _generate_gl_account(self, category: str) -> str:
        gl_prefixes = {
            "cloud_computing": "6100",
            "software_licenses": "6200",
            "monitoring_tools": "6210",
            "research_supplies": "6400",
            "computer_hardware_purchase": "6500",
            "computer_gpu_hardware": "6510",
            "computer_hardware_rental": "6520",
            "computer_peripherals": "6530"
        }
        prefix = gl_prefixes.get(category, "6000")
        suffix = random.randint(100, 999)
        return f"{prefix}-{suffix}"

    def _random_date(self, start_year: int, end_year: int) -> date:
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return start_date + timedelta(days=random_days)


class EnterpriseStudyGenerator:
    """Generates complete enterprise study data structure."""

    def __init__(self, seed: int = 42):
        self.data_gen = EnterpriseTestDataGenerator(seed)

    def generate_complete_study(self) -> Dict[str, Any]:
        """Generate a complete enterprise study with all data."""

        # Generate all data
        projects = self.data_gen.generate_projects()
        employees = self.data_gen.generate_employees(750)
        subcontractors = self.data_gen.generate_subcontractors(350)
        supplies = self.data_gen.generate_supplies(500)
        computer_supplies = self.data_gen.generate_computer_supplies(300)

        # Combine all QREs
        all_qres = subcontractors + supplies + computer_supplies

        # Calculate totals by state
        state_totals = self._calculate_state_totals(employees, all_qres)

        # Calculate grand totals
        total_wage_qre = sum(Decimal(str(e["qualified_wages"])) for e in employees)
        total_supply_qre = sum(Decimal(str(s["qualified_amount"])) for s in supplies)
        total_computer_qre = sum(Decimal(str(c["qualified_amount"])) for c in computer_supplies)
        total_subcontractor_qre = sum(Decimal(str(c["qualified_amount"])) for c in subcontractors)
        total_qre = total_wage_qre + total_supply_qre + total_computer_qre + total_subcontractor_qre

        study_data = {
            "id": str(uuid4()),
            "entity_name": "Aura Technologies, Inc.",
            "ein": "84-5678901",
            "tax_year": 2024,
            "fiscal_year_end": date(2024, 12, 31).isoformat(),
            "entity_type": "C_CORP",
            "status": "cpa_approval",
            "states": ["CA", "PA"],
            "gross_receipts": {
                2024: Decimal("285000000"),
                2023: Decimal("215000000"),
                2022: Decimal("165000000"),
                2021: Decimal("125000000"),
                2020: Decimal("95000000")
            },
            "prior_year_qre": {
                2023: Decimal("28500000"),
                2022: Decimal("22000000"),
                2021: Decimal("17500000")
            },
            "credit_method": "ASC",
            "is_startup": False,

            # Calculated totals
            "total_qre": total_qre,
            "qre_wages": total_wage_qre,
            "qre_supplies": total_supply_qre,
            "qre_computer_supplies": total_computer_qre,
            "qre_subcontractor": total_subcontractor_qre,
            "qre_contract": total_subcontractor_qre,  # Alias for compatibility
            "state_totals": state_totals,

            # CPA Review
            "cpa_name": "Jonathan Toroni, CPA",
            "cpa_license": "CPA-PA-123456",
            "cpa_firm": "Toroni & Company CPAs",
            "cpa_approval_date": None,
            "cpa_signature": None
        }

        return {
            "study_data": study_data,
            "projects": projects,
            "employees": employees,
            "subcontractors": subcontractors,
            "supplies": supplies,
            "computer_supplies": computer_supplies,
            "qres": all_qres
        }

    def _calculate_state_totals(
        self,
        employees: List[Dict],
        qres: List[Dict]
    ) -> Dict[str, Dict[str, Decimal]]:
        """Calculate totals by state (CA and PA)."""
        states = ["CA", "PA"]
        totals = {}

        for state in states:
            state_employees = [e for e in employees if e["state"] == state]
            state_qres = [q for q in qres if q["state"] == state]

            wage_qre = sum(Decimal(str(e["qualified_wages"])) for e in state_employees)
            supply_qre = sum(
                Decimal(str(q["qualified_amount"]))
                for q in state_qres if q["category"] == "supplies"
            )
            computer_qre = sum(
                Decimal(str(q["qualified_amount"]))
                for q in state_qres if q["category"] == "computer_supplies"
            )
            subcontractor_qre = sum(
                Decimal(str(q["qualified_amount"]))
                for q in state_qres if q["category"] == "subcontractor"
            )

            totals[state] = {
                "employee_count": len(state_employees),
                "wage_qre": wage_qre,
                "supply_qre": supply_qre,
                "computer_qre": computer_qre,
                "subcontractor_qre": subcontractor_qre,
                "total_qre": wage_qre + supply_qre + computer_qre + subcontractor_qre
            }

        return totals


class EnterpriseCalculator:
    """Calculates federal and state R&D credits for enterprise study."""

    def __init__(self):
        self.federal_rules = FederalRules()

    def calculate_all_credits(self, study_data: Dict) -> Dict[str, Any]:
        """Calculate federal and CA/PA state credits."""

        total_qre = float(study_data["total_qre"])
        prior_qre = [
            float(study_data["prior_year_qre"].get(year, 0))
            for year in [2023, 2022, 2021]
        ]

        # Federal calculation
        avg_prior_qre = sum(prior_qre) / 3 if prior_qre else 0
        gross_receipts = [
            float(study_data["gross_receipts"].get(year, 0))
            for year in [2024, 2023, 2022, 2021, 2020]
        ]

        # Federal Regular Credit
        if avg_prior_qre > 0 and gross_receipts[0] > 0:
            base_ratio = avg_prior_qre / (sum(gross_receipts[1:]) / 4) if sum(gross_receipts[1:]) > 0 else 0.03
            fixed_base_pct = max(0.03, min(base_ratio, 0.16))
        else:
            fixed_base_pct = 0.03

        avg_gross_receipts = sum(gross_receipts[1:]) / 4 if gross_receipts[1:] else 0
        base_amount = avg_gross_receipts * fixed_base_pct
        min_base = total_qre * 0.50
        final_base = max(base_amount, min_base)

        excess_qre_regular = max(total_qre - final_base, 0)
        tentative_regular = excess_qre_regular * 0.20
        section_280c_regular = tentative_regular * 0.21
        final_regular = tentative_regular - section_280c_regular

        # Federal ASC
        asc_base = avg_prior_qre * 0.50
        excess_qre_asc = max(total_qre - asc_base, 0)
        tentative_asc = excess_qre_asc * 0.14
        section_280c_asc = tentative_asc * 0.21
        final_asc = tentative_asc - section_280c_asc

        selected_method = "asc" if final_asc >= final_regular else "regular"
        federal_credit = final_asc if selected_method == "asc" else final_regular

        # State calculations for CA and PA
        state_results = {}
        total_state_credits = Decimal("0")

        for state, state_totals in study_data.get("state_totals", {}).items():
            state_qre = float(state_totals["total_qre"])

            if state == "CA":
                # California R&D Credit: 24% of excess QRE (incremental)
                state_prior_avg = avg_prior_qre * (state_qre / total_qre) if total_qre > 0 else 0
                state_base = state_prior_avg * 0.50
                state_excess = max(state_qre - state_base, 0)
                state_credit = state_excess * 0.24

                state_results["CA"] = {
                    "state_name": "California",
                    "state_code": "CA",
                    "credit_type": "incremental",
                    "credit_rate": 0.24,
                    "state_qre": state_qre,
                    "state_base_amount": state_base,
                    "excess_qre": state_excess,
                    "calculated_credit": state_credit,
                    "credit_cap": "N/A",
                    "final_credit": state_credit,
                    "carryforward_years": "Unlimited",
                    "is_refundable": False,
                    "statute_citation": "Cal. Rev. & Tax Code Section 23609",
                    "form_number": "FTB 3523"
                }

            elif state == "PA":
                # Pennsylvania R&D Credit: 10% of increase in R&D spending
                state_prior_avg = avg_prior_qre * (state_qre / total_qre) if total_qre > 0 else 0
                state_increase = max(state_qre - state_prior_avg, 0)
                state_credit = state_increase * 0.10
                # PA has annual cap of $55M total program, individual cap typically $1.5M-$2M
                state_credit = min(state_credit, 2000000)

                state_results["PA"] = {
                    "state_name": "Pennsylvania",
                    "state_code": "PA",
                    "credit_type": "incremental",
                    "credit_rate": 0.10,
                    "state_qre": state_qre,
                    "state_base_amount": state_prior_avg,
                    "excess_qre": state_increase,
                    "calculated_credit": state_increase * 0.10,
                    "credit_cap": "$2,000,000 per taxpayer",
                    "final_credit": state_credit,
                    "carryforward_years": 15,
                    "is_refundable": False,
                    "statute_citation": "72 P.S. Section 8702-A",
                    "form_number": "PA REV-545",
                    "notes": "Credit is assignable/sellable at 85% of face value"
                }

            total_state_credits += Decimal(str(state_credit))

        return {
            "total_qre": total_qre,
            "qre_wages": float(study_data["qre_wages"]),
            "qre_supplies": float(study_data["qre_supplies"]),
            "qre_computer_supplies": float(study_data.get("qre_computer_supplies", 0)),
            "qre_subcontractor": float(study_data.get("qre_subcontractor", 0)),
            "qre_contract": float(study_data.get("qre_contract", 0)),

            "federal_regular": {
                "total_qre": total_qre,
                "fixed_base_percentage": fixed_base_pct,
                "avg_gross_receipts": avg_gross_receipts,
                "calculated_base": base_amount,
                "min_base": min_base,
                "base_amount": final_base,
                "excess_qre": excess_qre_regular,
                "tentative_credit": tentative_regular,
                "section_280c_reduction": section_280c_regular,
                "final_credit": final_regular
            },

            "federal_asc": {
                "total_qre": total_qre,
                "prior_year_1": prior_qre[0] if prior_qre else 0,
                "prior_year_2": prior_qre[1] if len(prior_qre) > 1 else 0,
                "prior_year_3": prior_qre[2] if len(prior_qre) > 2 else 0,
                "avg_prior_qre": avg_prior_qre,
                "base_amount": asc_base,
                "excess_qre": excess_qre_asc,
                "tentative_credit": tentative_asc,
                "section_280c_reduction": section_280c_asc,
                "final_credit": final_asc
            },

            "selected_method": selected_method,
            "regular_credit": final_regular,
            "asc_credit": final_asc,
            "federal_credit": federal_credit,

            "state_results": state_results,
            "total_state_credits": float(total_state_credits),

            "total_credits": federal_credit + float(total_state_credits)
        }


class CPASignOffManager:
    """Manages the CPA sign-off workflow."""

    def __init__(self):
        self.required_reviews = [
            "project_qualification",
            "employee_allocations",
            "qre_schedules",
            "calculation_review",
            "documentation_review"
        ]

    def initiate_review(self, study_id: str) -> Dict[str, Any]:
        return {
            "study_id": study_id,
            "status": "in_review",
            "initiated_at": datetime.now().isoformat(),
            "reviews_pending": self.required_reviews.copy(),
            "reviews_completed": [],
            "reviewer": None
        }

    def complete_review_step(self, workflow: Dict, step: str, reviewer: str, notes: str = "") -> Dict:
        if step in workflow["reviews_pending"]:
            workflow["reviews_pending"].remove(step)
            workflow["reviews_completed"].append({
                "step": step,
                "reviewer": reviewer,
                "completed_at": datetime.now().isoformat(),
                "notes": notes
            })
            workflow["reviewer"] = reviewer

        if not workflow["reviews_pending"]:
            workflow["status"] = "ready_for_signoff"

        return workflow

    def sign_off(self, workflow: Dict, cpa_name: str, cpa_license: str, cpa_firm: str) -> Dict:
        if workflow["status"] != "ready_for_signoff":
            raise ValueError("Complete all review steps first.")

        import hashlib
        content = f"{cpa_name}|{cpa_license}|{datetime.now().isoformat()}"
        sig_hash = hashlib.sha256(content.encode()).hexdigest()[:32]

        return {
            **workflow,
            "status": "signed",
            "signed_at": datetime.now().isoformat(),
            "cpa_name": cpa_name,
            "cpa_license": cpa_license,
            "cpa_firm": cpa_firm,
            "signature_hash": sig_hash
        }


def run_enterprise_e2e_test():
    """Run the enterprise E2E test."""

    print("=" * 100)
    print("ENTERPRISE R&D TAX CREDIT STUDY - COMPREHENSIVE E2E TEST")
    print("=" * 100)
    print()

    # Step 1: Generate data
    print("STEP 1: Generating Enterprise-Scale Test Data...")
    print("-" * 80)

    study_gen = EnterpriseStudyGenerator(seed=42)
    all_data = study_gen.generate_complete_study()

    study_data = all_data["study_data"]
    projects = all_data["projects"]
    employees = all_data["employees"]
    subcontractors = all_data["subcontractors"]
    supplies = all_data["supplies"]
    computer_supplies = all_data["computer_supplies"]
    qres = all_data["qres"]

    print(f"  Entity: {study_data['entity_name']}")
    print(f"  Tax Year: {study_data['tax_year']}")
    print(f"  States: {', '.join(study_data['states'])}")
    print()
    print(f"  Generated {len(projects)} R&D Projects with detailed 4-Part Test answers")
    print(f"  Generated {len(employees)} employees across CA and PA")
    print(f"  Generated {len(subcontractors)} subcontractor expenses")
    print(f"  Generated {len(supplies)} supply expenses")
    print(f"  Generated {len(computer_supplies)} computer supply expenses")
    print()

    # Show project details
    print("  Projects:")
    for p in projects:
        print(f"    - {p['name']}")
        print(f"      Budget: ${float(p['total_budget']):,.0f} | Score: {p['overall_score']}/100")
    print()

    # Show state distribution
    print("  Employee Distribution:")
    for state in ["CA", "PA"]:
        state_count = len([e for e in employees if e["state"] == state])
        state_wages = sum(float(e["qualified_wages"]) for e in employees if e["state"] == state)
        print(f"    {state}: {state_count} employees, ${state_wages:,.0f} qualified wages")
    print()

    # Show expense breakdown
    print("  Expense Categories:")
    print(f"    Wages:              ${float(study_data['qre_wages']):>15,.2f}")
    print(f"    Supplies:           ${float(study_data['qre_supplies']):>15,.2f}")
    print(f"    Computer Supplies:  ${float(study_data['qre_computer_supplies']):>15,.2f}")
    print(f"    Subcontractors:     ${float(study_data['qre_subcontractor']):>15,.2f}")
    print(f"    ----------------------------------------")
    print(f"    TOTAL QRE:          ${float(study_data['total_qre']):>15,.2f}")
    print()

    # Step 2: Calculate credits
    print("STEP 2: Calculating Federal and State R&D Credits...")
    print("-" * 80)

    calculator = EnterpriseCalculator()
    calc_result = calculator.calculate_all_credits(study_data)

    print(f"  FEDERAL CREDIT CALCULATION:")
    print(f"    Method Selected: {calc_result['selected_method'].upper()}")
    print(f"    Regular Credit:  ${calc_result['regular_credit']:>12,.2f}")
    print(f"    ASC Credit:      ${calc_result['asc_credit']:>12,.2f}")
    print(f"    Final Federal:   ${calc_result['federal_credit']:>12,.2f}")
    print()

    print(f"  STATE CREDIT CALCULATIONS:")
    for state, result in calc_result["state_results"].items():
        print(f"    {state} - {result['state_name']}:")
        print(f"      State QRE:      ${result['state_qre']:>12,.2f}")
        print(f"      Credit Rate:    {result['credit_rate']*100:.0f}%")
        print(f"      State Credit:   ${result['final_credit']:>12,.2f}")
        print(f"      Form:           {result['form_number']}")
    print()

    print(f"  TOTAL STATE CREDITS:  ${calc_result['total_state_credits']:>12,.2f}")
    print(f"  ============================================")
    print(f"  GRAND TOTAL CREDITS:  ${calc_result['total_credits']:>12,.2f}")
    print()

    # Step 3: Generate PDF
    print("STEP 3: Generating PDF Study Report...")
    print("-" * 80)

    pdf_generator = PDFStudyGenerator(config={
        "include_watermark": False,
        "branding": {
            "company_name": "Aura AI",
            "tagline": "Intelligent Tax Credit Automation",
            "primary_color": "#1F4E79",
            "secondary_color": "#6366F1"
        }
    })

    narratives = {
        "executive_summary": """
This comprehensive R&D Tax Credit Study documents the qualified research activities undertaken
by Aura Technologies, Inc. during tax year 2024. The company engaged in three major R&D
initiatives: (1) the Aura AI Document Processing Platform, (2) the Aura Predict Anomaly
Detection System, and (3) the Aura Comply Regulatory Engine. These projects represent
significant technological advancement through novel approaches to AI, machine learning,
and natural language processing.
        """.strip(),
        "methodology": """
This study was prepared using a combination of contemporaneous documentation review,
employee interviews, project analysis, and financial record examination. The methodology
follows IRS guidance and Treasury Regulations for IRC Section 41 compliance, as well as
state-specific requirements for California and Pennsylvania R&D tax credits.
        """.strip()
    }

    pdf_bytes = pdf_generator.generate_study_report(
        study_data=study_data,
        projects=projects,
        employees=employees[:100],
        qre_summary={
            "wages": float(study_data["qre_wages"]),
            "supplies": float(study_data["qre_supplies"]) + float(study_data["qre_computer_supplies"]),
            "contract_research": float(study_data["qre_subcontractor"]),
            "total": float(study_data["total_qre"])
        },
        calculation_result=calc_result,
        narratives=narratives,
        evidence_items=[],
        is_final=True
    )

    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, 'enterprise_rd_study_2024.pdf')
    with open(pdf_path, 'wb') as f:
        f.write(pdf_bytes)
    print(f"  PDF saved: {pdf_path}")
    print(f"  Size: {len(pdf_bytes):,} bytes")
    print()

    # Step 4: Generate Excel
    print("STEP 4: Generating Excel Workbook...")
    print("-" * 80)

    excel_generator = ExcelWorkbookGenerator()
    excel_bytes = excel_generator.generate_workbook(
        study_data=study_data,
        projects=projects,
        employees=employees,
        qres=qres,
        calculation_result=calc_result
    )

    excel_path = os.path.join(output_dir, 'enterprise_rd_study_2024.xlsx')
    with open(excel_path, 'wb') as f:
        f.write(excel_bytes)
    print(f"  Excel saved: {excel_path}")
    print(f"  Size: {len(excel_bytes):,} bytes")
    print()

    # Step 5: CPA Sign-off
    print("STEP 5: Completing CPA Sign-off Workflow...")
    print("-" * 80)

    signoff_manager = CPASignOffManager()
    workflow = signoff_manager.initiate_review(study_data["id"])

    for step in signoff_manager.required_reviews:
        workflow = signoff_manager.complete_review_step(
            workflow, step, "Jonathan Toroni, CPA", f"Reviewed and approved {step}"
        )
        print(f"    Completed: {step}")

    workflow = signoff_manager.sign_off(
        workflow,
        cpa_name="Jonathan Toroni, CPA",
        cpa_license="CPA-PA-123456",
        cpa_firm="Toroni & Company CPAs"
    )

    print(f"  Sign-off completed by: {workflow['cpa_name']}")
    print(f"  Signature: {workflow['signature_hash']}")
    print()

    # Summary
    print("=" * 100)
    print("ENTERPRISE E2E TEST COMPLETE - SUMMARY")
    print("=" * 100)
    print()
    print("DATA GENERATED:")
    print(f"  - 3 R&D Projects with comprehensive 4-Part Test documentation")
    print(f"  - {len(employees)} employees across 2 states (CA, PA)")
    print(f"  - {len(subcontractors)} subcontractor expenses")
    print(f"  - {len(supplies)} supply expenses")
    print(f"  - {len(computer_supplies)} computer supply expenses")
    print()
    print("CREDITS CALCULATED:")
    print(f"  - Federal Credit ({calc_result['selected_method'].upper()}): ${calc_result['federal_credit']:,.2f}")
    print(f"  - California State Credit: ${calc_result['state_results']['CA']['final_credit']:,.2f}")
    print(f"  - Pennsylvania State Credit: ${calc_result['state_results']['PA']['final_credit']:,.2f}")
    print(f"  - TOTAL CREDITS: ${calc_result['total_credits']:,.2f}")
    print()
    print("OUTPUTS:")
    print(f"  - PDF Study: {pdf_path}")
    print(f"  - Excel Workbook: {excel_path}")
    print()
    print("CPA SIGN-OFF: COMPLETED")
    print(f"  - Signed by: {workflow['cpa_name']}")
    print(f"  - Firm: {workflow['cpa_firm']}")
    print()
    print("=" * 100)
    print("ALL TESTS PASSED SUCCESSFULLY")
    print("=" * 100)

    return {
        "study_data": study_data,
        "projects": projects,
        "employees": employees,
        "calculation_result": calc_result,
        "workflow": workflow,
        "pdf_path": pdf_path,
        "excel_path": excel_path
    }


if __name__ == "__main__":
    result = run_enterprise_e2e_test()
