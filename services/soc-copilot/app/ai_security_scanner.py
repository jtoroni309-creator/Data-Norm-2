"""
AI-Powered Security Scanner
Automated vulnerability detection and threat intelligence for penetration testing
"""
import logging
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID

import httpx
from openai import AsyncOpenAI

from .config import settings
from .pentest_models import VulnerabilitySeverity, ScanType

logger = logging.getLogger(__name__)


class AISecurityScanner:
    """
    AI-powered security scanner using GPT-4 for intelligent
    vulnerability detection, risk scoring, and remediation recommendations
    """

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.enabled = settings.ENABLE_AI_PLANNING and settings.OPENAI_API_KEY is not None

    async def analyze_scan_results(
        self,
        scan_type: ScanType,
        raw_results: Dict[str, Any],
        target_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Analyze raw scan results with AI to:
        - Identify and classify vulnerabilities
        - Calculate risk scores
        - Generate remediation recommendations
        - Map to SOC control objectives

        Args:
            scan_type: Type of scan performed
            raw_results: Raw scan output (JSON)
            target_info: Information about the target

        Returns:
            Enhanced scan results with AI analysis
        """
        if not self.enabled:
            logger.warning("AI scanner not enabled - returning raw results")
            return raw_results

        try:
            prompt = self._build_analysis_prompt(scan_type, raw_results, target_info)

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert security researcher and penetration tester. "
                            "Analyze vulnerability scan results and provide detailed, actionable "
                            "insights. Focus on risk prioritization, business impact, and "
                            "remediation guidance. Map findings to SOC control objectives where applicable."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            ai_analysis = response.choices[0].message.content
            confidence_score = self._calculate_confidence(response)

            logger.info(f"AI scan analysis completed for {scan_type.value} with confidence {confidence_score:.2f}")

            return {
                "ai_enhanced": True,
                "ai_model": settings.OPENAI_MODEL,
                "ai_confidence_score": confidence_score,
                "ai_analysis": ai_analysis,
                "raw_results": raw_results,
                "analyzed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"AI scan analysis failed: {e}")
            return {
                "ai_enhanced": False,
                "error": str(e),
                "raw_results": raw_results
            }

    async def detect_vulnerabilities(
        self,
        target_url: str,
        target_type: str,
        scan_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        AI-powered vulnerability detection

        Analyzes target and scan data to identify potential vulnerabilities,
        including zero-days and logic flaws that automated scanners might miss.

        Returns:
            List of detected vulnerabilities with risk scores
        """
        if not self.enabled:
            return []

        try:
            prompt = f"""
Analyze this target for security vulnerabilities:

Target: {target_url}
Type: {target_type}
Scan Data: {scan_data}

Identify all potential vulnerabilities including:
1. Known CVEs
2. Misconfigurations
3. Logic flaws
4. Security control gaps
5. Compliance issues (SOC 2 TSC)

For each vulnerability, provide:
- Title
- Severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- CVSS score (if applicable)
- CVE/CWE ID (if applicable)
- Description
- Proof of concept
- Business impact
- Remediation steps
- Estimated remediation time
- Related SOC control objectives (CC1-CC9, etc.)

Return as JSON array.
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a security vulnerability analyst. Provide detailed, accurate vulnerability assessments."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            vulnerabilities = response.choices[0].message.content
            logger.info(f"AI detected vulnerabilities for {target_url}")

            return self._parse_vulnerabilities(vulnerabilities)

        except Exception as e:
            logger.error(f"AI vulnerability detection failed: {e}")
            return []

    async def generate_exploit_suggestions(
        self,
        vulnerability: Dict[str, Any],
        target_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered exploit suggestions for vulnerability validation

        **IMPORTANT:** Only for authorized penetration testing with signed authorization.

        Args:
            vulnerability: Vulnerability details
            target_info: Target system information

        Returns:
            Exploit suggestions with safety guidelines
        """
        if not self.enabled:
            return {}

        try:
            prompt = f"""
For authorized penetration testing engagement:

Vulnerability: {vulnerability.get('title')}
Type: {vulnerability.get('vulnerability_type')}
Severity: {vulnerability.get('severity')}
Target: {target_info.get('hostname')}

Provide:
1. Safe exploitation methodology
2. Step-by-step verification process
3. Expected behavior vs. vulnerable behavior
4. Evidence collection methods
5. Safety precautions
6. Rollback procedures

Focus on verification, not actual exploitation. Emphasize safety and authorization.

Return as JSON.
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a penetration testing expert. Provide safe, authorized "
                            "vulnerability verification methods. Always emphasize proper authorization "
                            "and safety. Never provide destructive or illegal exploitation methods."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            suggestions = response.choices[0].message.content
            logger.info(f"AI generated exploit suggestions for {vulnerability.get('title')}")

            return {
                "exploit_suggestions": suggestions,
                "authorization_required": True,
                "safety_warning": "Only perform with written authorization. Document all actions.",
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"AI exploit suggestion generation failed: {e}")
            return {}

    async def analyze_attack_surface(
        self,
        domain: str,
        discovered_assets: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        AI-powered attack surface analysis

        Analyzes exposed assets and identifies high-risk attack vectors.

        Args:
            domain: Primary domain
            discovered_assets: List of discovered assets (subdomains, IPs, services)

        Returns:
            Attack surface analysis with risk heatmap
        """
        if not self.enabled:
            return {}

        try:
            prompt = f"""
Analyze attack surface for: {domain}

Discovered Assets:
{discovered_assets}

Provide comprehensive attack surface analysis:
1. Internet-exposed assets and services
2. High-risk entry points
3. Potential attack vectors
4. Misconfigurations and security gaps
5. Data exposure risks
6. Attack path scenarios
7. Risk heatmap (prioritized targets)
8. Immediate remediation priorities

Focus on business risk and exploitability.

Return as JSON.
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an attack surface management expert. Provide risk-prioritized analysis."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            analysis = response.choices[0].message.content
            logger.info(f"AI attack surface analysis completed for {domain}")

            return {
                "domain": domain,
                "analysis": analysis,
                "asset_count": len(discovered_assets),
                "analyzed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"AI attack surface analysis failed: {e}")
            return {}

    async def map_to_soc_controls(
        self,
        vulnerability: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Map vulnerability to SOC 2 Trust Services Criteria and control objectives

        Identifies which SOC controls would have prevented or detected this vulnerability.

        Args:
            vulnerability: Vulnerability details

        Returns:
            List of related control objectives with gap analysis
        """
        if not self.enabled:
            return []

        try:
            prompt = f"""
Map this vulnerability to SOC 2 Trust Services Criteria:

Vulnerability: {vulnerability.get('title')}
Type: {vulnerability.get('vulnerability_type')}
Description: {vulnerability.get('description')}

Identify:
1. Which TSC criteria are affected (CC1-CC9, A1, PI1, C1, P1)
2. Specific control objectives that failed
3. Control gap analysis
4. Control design recommendations
5. Implementation guidance

Return as JSON array of related controls.
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a SOC 2 auditing expert. Map security findings to TSC control objectives."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )

            control_mappings = response.choices[0].message.content
            logger.info(f"Mapped vulnerability to SOC controls: {vulnerability.get('title')}")

            return self._parse_control_mappings(control_mappings)

        except Exception as e:
            logger.error(f"SOC control mapping failed: {e}")
            return []

    async def generate_remediation_plan(
        self,
        vulnerabilities: List[Dict[str, Any]],
        environment_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered remediation roadmap

        Creates prioritized remediation plan based on risk, business impact,
        and available resources.

        Args:
            vulnerabilities: List of all vulnerabilities
            environment_info: Client environment details

        Returns:
            Comprehensive remediation roadmap
        """
        if not self.enabled:
            return {}

        try:
            # Summarize vulnerabilities
            vuln_summary = [
                {
                    "title": v.get("title"),
                    "severity": v.get("severity"),
                    "type": v.get("vulnerability_type")
                }
                for v in vulnerabilities
            ]

            prompt = f"""
Create remediation roadmap for these vulnerabilities:

Vulnerabilities: {vuln_summary}
Environment: {environment_info}

Provide:
1. Priority ranking (consider severity + exploitability + business impact)
2. Remediation phases (immediate, short-term, long-term)
3. Specific remediation steps for each vulnerability
4. Resource requirements (hours, skillset)
5. Implementation order (dependencies, quick wins)
6. Verification methods
7. Estimated timeline
8. Risk reduction metrics

Return as structured JSON.
"""

            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a security remediation expert. Create actionable, prioritized remediation plans."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            remediation_plan = response.choices[0].message.content
            logger.info(f"AI generated remediation plan for {len(vulnerabilities)} vulnerabilities")

            return {
                "remediation_plan": remediation_plan,
                "total_vulnerabilities": len(vulnerabilities),
                "generated_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"AI remediation plan generation failed: {e}")
            return {}

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _build_analysis_prompt(
        self,
        scan_type: ScanType,
        raw_results: Dict[str, Any],
        target_info: Dict[str, str]
    ) -> str:
        """Build AI analysis prompt based on scan type"""
        return f"""
Analyze these {scan_type.value} scan results:

Target: {target_info.get('hostname', 'Unknown')}
IP: {target_info.get('ip_address', 'Unknown')}
Type: {target_info.get('target_type', 'Unknown')}

Scan Results:
{raw_results}

Provide:
1. Summary of findings
2. Critical issues requiring immediate attention
3. Risk assessment
4. Recommended next steps
5. SOC control objective mappings

Return as structured JSON.
"""

    def _calculate_confidence(self, response) -> float:
        """Calculate AI confidence score based on response metadata"""
        # In production, implement sophisticated confidence scoring
        # based on response quality, token usage, model certainty, etc.
        return 0.85  # Placeholder

    def _parse_vulnerabilities(self, ai_response: str) -> List[Dict[str, Any]]:
        """Parse AI response into vulnerability structures"""
        # In production, implement robust JSON parsing and validation
        import json
        try:
            return json.loads(ai_response).get("vulnerabilities", [])
        except:
            return []

    def _parse_control_mappings(self, ai_response: str) -> List[Dict[str, str]]:
        """Parse AI response into control mapping structures"""
        import json
        try:
            return json.loads(ai_response).get("control_mappings", [])
        except:
            return []


# Global instance
ai_scanner = AISecurityScanner()
