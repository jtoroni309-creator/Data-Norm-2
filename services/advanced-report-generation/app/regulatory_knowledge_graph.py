"""
Regulatory Knowledge Graph

A comprehensive graph of audit standards and their relationships:
- PCAOB Auditing Standards (AS)
- AICPA Standards (AU-C)
- SEC Regulations
- GAAP/IFRS
- Cross-references and supersessions

Used to:
- Find all applicable standards for a report section
- Check for conflicts between standards
- Ensure completeness of citations
- Navigate standard relationships
"""

import networkx as nx
from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import pickle
from pathlib import Path
from loguru import logger

from .config import settings


@dataclass
class RegulatoryStandard:
    """A regulatory standard or requirement"""
    standard_id: str  # "AS_3101", "AU-C_700", "ASC_606"
    title: str
    authority: str  # "PCAOB", "AICPA", "FASB", "SEC"
    effective_date: datetime
    superseded: bool = False
    superseded_by: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None


@dataclass
class StandardRequirement:
    """A specific requirement within a standard"""
    requirement_id: str  # "AS_3101_P08"
    standard_id: str
    paragraph: str  # "08", "15a", etc.
    text: str
    applies_to: List[str]  # ["public_companies", "issuers", "all"]


class RegulatoryKnowledgeGraph:
    """
    Knowledge graph of regulatory standards

    Graph structure:
    - Nodes: Standards, requirements, concepts
    - Edges: Relationships (references, supersedes, requires, etc.)

    Benefits:
    - Automatic citation completeness checking
    - Conflict detection
    - Standard navigation
    - Requirement extraction
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        """Build the complete regulatory knowledge graph"""

        # Try to load from cache
        cache_path = Path(settings.KNOWLEDGE_GRAPH_CACHE_PATH)
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    self.graph = pickle.load(f)
                logger.info("Loaded knowledge graph from cache")
                return
            except Exception as e:
                logger.warning(f"Failed to load cache: {e}")

        logger.info("Building regulatory knowledge graph...")

        # Add PCAOB Auditing Standards
        self._add_pcaob_standards()

        # Add AICPA SAS/AU-C Standards
        self._add_aicpa_standards()

        # Add SEC Regulations
        self._add_sec_regulations()

        # Add GAAP/ASC Topics
        self._add_asc_topics()

        # Add relationships
        self._add_relationships()

        # Cache the graph
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump(self.graph, f)

        logger.info(f"Knowledge graph built: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

    def _add_pcaob_standards(self):
        """Add PCAOB Auditing Standards"""

        pcaob_standards = [
            {
                "id": "AS_1001",
                "title": "Responsibilities and Functions of the Independent Auditor",
                "effective_date": "2004-05-14",
                "applies_to": ["public_companies", "issuers"],
                "summary": "Establishes the responsibilities of the independent auditor"
            },
            {
                "id": "AS_1005",
                "title": "Independence",
                "effective_date": "2004-05-14",
                "applies_to": ["public_companies", "issuers"],
                "summary": "Requirements for auditor independence"
            },
            {
                "id": "AS_1015",
                "title": "Due Professional Care",
                "effective_date": "2004-05-14",
                "applies_to": ["all"],
                "summary": "Professional skepticism and due care requirements"
            },
            {
                "id": "AS_2101",
                "title": "Audit Planning",
                "effective_date": "2010-10-21",
                "applies_to": ["all"],
                "summary": "Requirements for planning the audit"
            },
            {
                "id": "AS_2110",
                "title": "Identifying and Assessing Risks of Material Misstatement",
                "effective_date": "2010-12-15",
                "applies_to": ["all"],
                "summary": "Risk assessment procedures and identifying risks"
            },
            {
                "id": "AS_2201",
                "title": "An Audit of Internal Control Over Financial Reporting",
                "effective_date": "2007-07-25",
                "applies_to": ["public_companies", "large_accelerated_filers"],
                "summary": "Requirements for integrated audits (SOX 404)"
            },
            {
                "id": "AS_2301",
                "title": "The Auditor's Responses to the Risks of Material Misstatement",
                "effective_date": "2010-12-15",
                "applies_to": ["all"],
                "summary": "Designing and performing audit procedures"
            },
            {
                "id": "AS_2401",
                "title": "Consideration of Fraud in a Financial Statement Audit",
                "effective_date": "2002-12-15",
                "applies_to": ["all"],
                "summary": "Requirements for considering fraud risks"
            },
            {
                "id": "AS_2415",
                "title": "Consideration of an Entity's Ability to Continue as a Going Concern",
                "effective_date": "2010-10-21",
                "applies_to": ["all"],
                "summary": "Going concern assessment requirements"
            },
            {
                "id": "AS_2501",
                "title": "Auditing Accounting Estimates",
                "effective_date": "2018-12-15",
                "applies_to": ["all"],
                "summary": "Requirements for auditing accounting estimates"
            },
            {
                "id": "AS_2502",
                "title": "Auditing Fair Value Measurements and Disclosures",
                "effective_date": "2018-12-15",
                "applies_to": ["all"],
                "summary": "Fair value measurement audit procedures"
            },
            {
                "id": "AS_2810",
                "title": "Evaluating Audit Results",
                "effective_date": "2010-10-21",
                "applies_to": ["all"],
                "summary": "Evaluating misstatements and forming conclusion"
            },
            {
                "id": "AS_3101",
                "title": "The Auditor's Report on an Audit of Financial Statements",
                "effective_date": "2017-06-30",
                "applies_to": ["all"],
                "summary": "Requirements for the audit report"
            },
            {
                "id": "AS_3105",
                "title": "Departures from Unqualified Opinions",
                "effective_date": "2004-05-14",
                "applies_to": ["all"],
                "summary": "Qualified, adverse, and disclaimer opinions"
            },
        ]

        for std in pcaob_standards:
            self.graph.add_node(
                std["id"],
                type="standard",
                title=std["title"],
                authority="PCAOB",
                effective_date=datetime.fromisoformat(std["effective_date"]),
                applies_to=std["applies_to"],
                summary=std["summary"],
                superseded=False,
                url=f"https://pcaobus.org/oversight/standards/auditing-standards/{std['id'].replace('_', '-').lower()}"
            )

    def _add_aicpa_standards(self):
        """Add AICPA SAS/AU-C Standards"""

        aicpa_standards = [
            {
                "id": "AU-C_200",
                "title": "Overall Objectives of the Independent Auditor",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers", "private_companies"],
                "summary": "Overall objectives and conduct of audit"
            },
            {
                "id": "AU-C_210",
                "title": "Terms of Engagement",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Engagement letter requirements"
            },
            {
                "id": "AU-C_300",
                "title": "Planning an Audit",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Planning procedures for audit"
            },
            {
                "id": "AU-C_315",
                "title": "Understanding the Entity and Its Environment",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Risk assessment and understanding entity"
            },
            {
                "id": "AU-C_330",
                "title": "Performing Audit Procedures in Response to Assessed Risks",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Substantive procedures and tests of controls"
            },
            {
                "id": "AU-C_500",
                "title": "Audit Evidence",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Sufficient appropriate audit evidence"
            },
            {
                "id": "AU-C_700",
                "title": "Forming an Opinion and Reporting on Financial Statements",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Audit report requirements for non-issuers"
            },
            {
                "id": "AU-C_705",
                "title": "Modifications to the Opinion in the Independent Auditor's Report",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Qualified, adverse, and disclaimer opinions"
            },
            {
                "id": "AU-C_706",
                "title": "Emphasis-of-Matter Paragraphs and Other-Matter Paragraphs",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Additional communication in auditor's report"
            },
            {
                "id": "AU-C_720",
                "title": "Other Information in Documents Containing Audited Financial Statements",
                "effective_date": "2012-12-15",
                "applies_to": ["non_issuers"],
                "summary": "Auditor's responsibility for other information"
            },
        ]

        for std in aicpa_standards:
            self.graph.add_node(
                std["id"],
                type="standard",
                title=std["title"],
                authority="AICPA",
                effective_date=datetime.fromisoformat(std["effective_date"]),
                applies_to=std["applies_to"],
                summary=std["summary"],
                superseded=False,
                url=f"https://www.aicpa.org/research/standards/auditattest/clarifiedsas.html"
            )

    def _add_sec_regulations(self):
        """Add SEC regulations relevant to audit reports"""

        sec_regs = [
            {
                "id": "SEC_17CFR210",
                "title": "Regulation S-X: Form and Content of Financial Statements",
                "effective_date": "1982-01-01",
                "applies_to": ["public_companies", "issuers"],
                "summary": "SEC requirements for financial statement presentation"
            },
            {
                "id": "SEC_17CFR240",
                "title": "Regulation S-K: Standard Instructions for Filing Forms",
                "effective_date": "1982-01-01",
                "applies_to": ["public_companies", "issuers"],
                "summary": "Disclosure requirements for SEC filings"
            },
            {
                "id": "SEC_SOX302",
                "title": "SOX Section 302: Corporate Responsibility for Financial Reports",
                "effective_date": "2002-07-30",
                "applies_to": ["public_companies", "issuers"],
                "summary": "Management certification requirements"
            },
            {
                "id": "SEC_SOX404",
                "title": "SOX Section 404: Management Assessment of Internal Controls",
                "effective_date": "2002-07-30",
                "applies_to": ["public_companies", "accelerated_filers"],
                "summary": "Internal control over financial reporting requirements"
            },
        ]

        for reg in sec_regs:
            self.graph.add_node(
                reg["id"],
                type="regulation",
                title=reg["title"],
                authority="SEC",
                effective_date=datetime.fromisoformat(reg["effective_date"]),
                applies_to=reg["applies_to"],
                summary=reg["summary"],
                superseded=False,
                url="https://www.sec.gov/rules-regulations"
            )

    def _add_asc_topics(self):
        """Add key ASC topics referenced in audit reports"""

        asc_topics = [
            {
                "id": "ASC_205",
                "title": "Presentation of Financial Statements",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_210",
                "title": "Balance Sheet",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_220",
                "title": "Income Statement",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_230",
                "title": "Statement of Cash Flows",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_250",
                "title": "Accounting Changes and Error Corrections",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_260",
                "title": "Earnings Per Share",
                "applies_to": ["public_companies"]
            },
            {
                "id": "ASC_606",
                "title": "Revenue from Contracts with Customers",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_715",
                "title": "Compensation - Retirement Benefits",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_718",
                "title": "Compensation - Stock Compensation",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_820",
                "title": "Fair Value Measurement",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_842",
                "title": "Leases",
                "applies_to": ["all"]
            },
            {
                "id": "ASC_326",
                "title": "Financial Instruments - Credit Losses (CECL)",
                "applies_to": ["all"]
            },
        ]

        for topic in asc_topics:
            self.graph.add_node(
                topic["id"],
                type="accounting_standard",
                title=topic["title"],
                authority="FASB",
                applies_to=topic["applies_to"],
                superseded=False,
                url=f"https://asc.fasb.org/{topic['id'].replace('_', '-')}"
            )

    def _add_relationships(self):
        """Add relationships between standards"""

        # PCAOB <-> AICPA correspondences
        correspondences = [
            ("AS_3101", "AU-C_700", "corresponds_to"),  # Audit report
            ("AS_3105", "AU-C_705", "corresponds_to"),  # Modified opinions
            ("AS_2101", "AU-C_300", "corresponds_to"),  # Planning
            ("AS_2110", "AU-C_315", "corresponds_to"),  # Risk assessment
            ("AS_2301", "AU-C_330", "corresponds_to"),  # Responses to risks
            ("AS_2401", "AU-C_240", "corresponds_to"),  # Fraud (note: AU-C 240 not added, but relationship shown)
        ]

        for std1, std2, relationship in correspondences:
            if self.graph.has_node(std1) and self.graph.has_node(std2):
                self.graph.add_edge(std1, std2, relationship=relationship)
                self.graph.add_edge(std2, std1, relationship=relationship)  # Bidirectional

        # Standards that reference SEC regulations
        sec_references = [
            ("AS_3101", "SEC_17CFR210", "must_comply_with"),
            ("AS_2201", "SEC_SOX404", "implements"),
            ("AU-C_700", "SEC_17CFR210", "may_reference"),
        ]

        for std, reg, relationship in sec_references:
            if self.graph.has_node(std) and self.graph.has_node(reg):
                self.graph.add_edge(std, reg, relationship=relationship)

        # Accounting standards referenced in audit standards
        accounting_refs = [
            ("AS_2501", "ASC_820", "addresses"),  # Estimates -> Fair value
            ("AS_2502", "ASC_820", "addresses"),  # Fair value -> ASC 820
            ("AS_2415", "ASC_205", "addresses"),  # Going concern -> Presentation
        ]

        for std, asc, relationship in accounting_refs:
            if self.graph.has_node(std) and self.graph.has_node(asc):
                self.graph.add_edge(std, asc, relationship=relationship)

    def get_applicable_standards(
        self,
        report_section: str,
        entity_type: str,
        framework: str = "GAAP"
    ) -> List[Dict]:
        """
        Get all applicable standards for a report section

        Args:
            report_section: "opinion", "basis", "responsibilities", etc.
            entity_type: "public_company", "private_company", "non_profit"
            framework: "GAAP", "IFRS"

        Returns:
            List of applicable standards with metadata
        """

        applicable = []

        # Mapping of sections to standards
        section_mapping = {
            "opinion": ["AS_3101", "AU-C_700", "AS_3105", "AU-C_705"],
            "basis": ["AS_3101", "AU-C_700"],
            "responsibilities": ["AS_3101", "AU-C_700", "AS_1001", "AU-C_200"],
            "internal_control": ["AS_2201", "SEC_SOX404"],
            "going_concern": ["AS_2415", "AU-C_570", "ASC_205"],
            "emphasis_of_matter": ["AU-C_706"],
        }

        # Get standards for this section
        standard_ids = section_mapping.get(report_section, [])

        for std_id in standard_ids:
            if not self.graph.has_node(std_id):
                continue

            node_data = self.graph.nodes[std_id]

            # Check if applies to this entity type
            applies_to = node_data.get("applies_to", [])

            if "all" in applies_to:
                applicable.append({
                    "standard_id": std_id,
                    "title": node_data.get("title"),
                    "authority": node_data.get("authority"),
                    "applies": True,
                    "mandatory": True
                })
            elif entity_type in ["public_company", "issuer"] and any(
                x in applies_to for x in ["public_companies", "issuers"]
            ):
                applicable.append({
                    "standard_id": std_id,
                    "title": node_data.get("title"),
                    "authority": node_data.get("authority"),
                    "applies": True,
                    "mandatory": True
                })
            elif entity_type in ["private_company", "non_issuer"] and any(
                x in applies_to for x in ["non_issuers", "private_companies"]
            ):
                applicable.append({
                    "standard_id": std_id,
                    "title": node_data.get("title"),
                    "authority": node_data.get("authority"),
                    "applies": True,
                    "mandatory": True
                })

        return applicable

    def check_conflicts(self, standard1: str, standard2: str) -> Tuple[bool, Optional[str]]:
        """
        Check if two standards conflict

        Returns:
            (has_conflict, reason)
        """

        if not self.graph.has_node(standard1) or not self.graph.has_node(standard2):
            return False, None

        node1 = self.graph.nodes[standard1]
        node2 = self.graph.nodes[standard2]

        # Check if one is superseded
        if node1.get("superseded"):
            return True, f"{standard1} is superseded by {node1.get('superseded_by')}"

        if node2.get("superseded"):
            return True, f"{standard2} is superseded by {node2.get('superseded_by')}"

        # Check if they apply to mutually exclusive entity types
        applies1 = set(node1.get("applies_to", []))
        applies2 = set(node2.get("applies_to", []))

        if "all" not in applies1 and "all" not in applies2:
            # Check for conflicts between PCAOB (issuers) and AICPA (non-issuers)
            if any(x in applies1 for x in ["public_companies", "issuers"]) and \
               any(x in applies2 for x in ["non_issuers", "private_companies"]):
                return True, f"{standard1} applies to issuers, {standard2} applies to non-issuers"

        return False, None

    def get_related_standards(self, standard_id: str, max_depth: int = 2) -> List[str]:
        """
        Get all related standards within max_depth hops

        Useful for finding all relevant citations
        """

        if not self.graph.has_node(standard_id):
            return []

        # BFS from standard_id
        related = set()
        visited = {standard_id}
        queue = [(standard_id, 0)]

        while queue:
            current, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # Get neighbors
            for neighbor in self.graph.neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    related.add(neighbor)
                    queue.append((neighbor, depth + 1))

            # Also check predecessors (reverse edges)
            for predecessor in self.graph.predecessors(current):
                if predecessor not in visited:
                    visited.add(predecessor)
                    related.add(predecessor)
                    queue.append((predecessor, depth + 1))

        return list(related)

    def validate_citation(self, citation: str) -> Dict:
        """
        Validate a citation

        Returns:
            {
                "valid": bool,
                "exists": bool,
                "current": bool,  # Not superseded
                "superseded_by": Optional[str],
                "standard_data": Dict
            }
        """

        # Parse citation (e.g., "AS 3101", "AU-C 700", "ASC 606")
        citation_clean = citation.replace(" ", "_").replace("-", "-")

        if not self.graph.has_node(citation_clean):
            return {
                "valid": False,
                "exists": False,
                "current": False,
                "superseded_by": None,
                "standard_data": {}
            }

        node_data = self.graph.nodes[citation_clean]

        is_current = not node_data.get("superseded", False)

        return {
            "valid": True,
            "exists": True,
            "current": is_current,
            "superseded_by": node_data.get("superseded_by"),
            "standard_data": dict(node_data)
        }

    def export_to_json(self, output_path: str):
        """Export graph to JSON for external use"""

        data = {
            "nodes": [],
            "edges": []
        }

        for node_id, node_data in self.graph.nodes(data=True):
            node_export = {"id": node_id, **node_data}
            # Convert datetime to string
            if "effective_date" in node_export:
                node_export["effective_date"] = node_export["effective_date"].isoformat()
            data["nodes"].append(node_export)

        for source, target, edge_data in self.graph.edges(data=True):
            data["edges"].append({
                "source": source,
                "target": target,
                **edge_data
            })

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported knowledge graph to {output_path}")


# Global knowledge graph instance
knowledge_graph = RegulatoryKnowledgeGraph()
