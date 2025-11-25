"""
AI Interview Bot for R&D Tax Credit Studies

Conducts structured interviews to gather R&D qualification evidence.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class InterviewType(str, Enum):
    """Types of interviews."""
    EMPLOYEE = "employee"
    PROJECT_LEAD = "project_lead"
    MANAGEMENT = "management"
    TECHNICAL = "technical"


class QuestionCategory(str, Enum):
    """Categories of interview questions."""
    PROJECT_OVERVIEW = "project_overview"
    TECHNICAL_CHALLENGES = "technical_challenges"
    UNCERTAINTY = "uncertainty"
    EXPERIMENTATION = "experimentation"
    TIME_ALLOCATION = "time_allocation"
    ROLE_RESPONSIBILITIES = "role_responsibilities"


@dataclass
class InterviewQuestion:
    """Structured interview question."""
    question_id: str
    question: str
    category: QuestionCategory
    priority: int  # 1-5, 1 is highest
    follow_up_prompts: List[str] = field(default_factory=list)
    expected_evidence_type: str = ""


@dataclass
class InterviewResponse:
    """Response to an interview question."""
    question_id: str
    response: str
    timestamp: datetime
    extracted_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5


@dataclass
class InterviewSession:
    """Complete interview session."""
    session_id: UUID
    study_id: UUID
    interview_type: InterviewType
    interviewee_name: str
    interviewee_title: str

    # Transcript
    questions_asked: List[InterviewQuestion]
    responses: List[InterviewResponse]

    # Extracted information
    projects_identified: List[Dict[str, Any]]
    activities_identified: List[Dict[str, Any]]
    time_allocations: List[Dict[str, Any]]
    uncertainties_identified: List[Dict[str, Any]]
    experiments_identified: List[Dict[str, Any]]

    # Summary
    summary: str
    confidence_score: float
    follow_up_needed: bool
    follow_up_topics: List[str]

    # Metadata
    started_at: datetime
    completed_at: Optional[datetime]


class InterviewBot:
    """
    AI-powered interview bot for R&D studies.

    Conducts structured interviews to gather:
    - Project and activity information
    - Technical challenges and uncertainties
    - Experimentation processes
    - Time allocation data
    - Role and responsibility details
    """

    def __init__(self, openai_client=None, config: Optional[Dict] = None):
        self.openai_client = openai_client
        self.config = config or {}
        self.model = self.config.get("model", "gpt-4-turbo-preview")

    def get_question_bank(
        self,
        interview_type: InterviewType
    ) -> List[InterviewQuestion]:
        """Get standard questions for interview type."""
        questions = []

        # Common questions for all interview types
        common_questions = [
            InterviewQuestion(
                question_id="common_1",
                question="Can you describe your role and primary responsibilities?",
                category=QuestionCategory.ROLE_RESPONSIBILITIES,
                priority=1,
                follow_up_prompts=[
                    "How long have you been in this role?",
                    "Who do you report to?"
                ]
            ),
            InterviewQuestion(
                question_id="common_2",
                question="What percentage of your time do you spend on research and development activities?",
                category=QuestionCategory.TIME_ALLOCATION,
                priority=1,
                follow_up_prompts=[
                    "How did you arrive at that estimate?",
                    "Does this vary by project or time of year?"
                ],
                expected_evidence_type="time_tracking"
            ),
        ]

        # Technical/Project Lead specific questions
        technical_questions = [
            InterviewQuestion(
                question_id="tech_1",
                question="Can you describe the main projects you've worked on this year?",
                category=QuestionCategory.PROJECT_OVERVIEW,
                priority=1,
                follow_up_prompts=[
                    "What was the goal of each project?",
                    "What was the expected outcome?"
                ],
                expected_evidence_type="project_documentation"
            ),
            InterviewQuestion(
                question_id="tech_2",
                question="What technical challenges or uncertainties did you encounter?",
                category=QuestionCategory.UNCERTAINTY,
                priority=1,
                follow_up_prompts=[
                    "Was the solution known at the start?",
                    "What made this technically challenging?"
                ],
                expected_evidence_type="technical_documentation"
            ),
            InterviewQuestion(
                question_id="tech_3",
                question="How did you approach solving these technical challenges?",
                category=QuestionCategory.EXPERIMENTATION,
                priority=1,
                follow_up_prompts=[
                    "Did you try multiple approaches?",
                    "How did you evaluate different solutions?"
                ],
                expected_evidence_type="test_results"
            ),
            InterviewQuestion(
                question_id="tech_4",
                question="Did you conduct any testing, prototyping, or modeling?",
                category=QuestionCategory.EXPERIMENTATION,
                priority=2,
                follow_up_prompts=[
                    "Can you describe the testing process?",
                    "Were there any failed approaches?"
                ],
                expected_evidence_type="test_documentation"
            ),
            InterviewQuestion(
                question_id="tech_5",
                question="What new or improved capabilities resulted from this work?",
                category=QuestionCategory.PROJECT_OVERVIEW,
                priority=2,
                follow_up_prompts=[
                    "How is this different from what existed before?",
                    "What improvements were achieved?"
                ]
            ),
            InterviewQuestion(
                question_id="tech_6",
                question="What scientific or engineering principles did you apply?",
                category=QuestionCategory.TECHNICAL_CHALLENGES,
                priority=2,
                follow_up_prompts=[
                    "What domain expertise was required?",
                    "What calculations or analysis were performed?"
                ]
            ),
        ]

        # Management specific questions
        management_questions = [
            InterviewQuestion(
                question_id="mgmt_1",
                question="What R&D initiatives did the company undertake this year?",
                category=QuestionCategory.PROJECT_OVERVIEW,
                priority=1,
                follow_up_prompts=[
                    "What were the business drivers?",
                    "What was the expected ROI?"
                ]
            ),
            InterviewQuestion(
                question_id="mgmt_2",
                question="How do you identify and prioritize R&D projects?",
                category=QuestionCategory.PROJECT_OVERVIEW,
                priority=2
            ),
            InterviewQuestion(
                question_id="mgmt_3",
                question="Who are the key technical staff involved in R&D?",
                category=QuestionCategory.ROLE_RESPONSIBILITIES,
                priority=1,
                follow_up_prompts=[
                    "What are their primary responsibilities?",
                    "What percentage of their time is spent on R&D?"
                ]
            ),
            InterviewQuestion(
                question_id="mgmt_4",
                question="Do you use any contractors for research activities?",
                category=QuestionCategory.PROJECT_OVERVIEW,
                priority=2,
                follow_up_prompts=[
                    "What type of work do contractors perform?",
                    "Where is the work performed?"
                ],
                expected_evidence_type="contracts"
            ),
        ]

        # Employee specific questions
        employee_questions = [
            InterviewQuestion(
                question_id="emp_1",
                question="Walk me through a typical day or week in your role.",
                category=QuestionCategory.ROLE_RESPONSIBILITIES,
                priority=1
            ),
            InterviewQuestion(
                question_id="emp_2",
                question="What projects have you contributed to?",
                category=QuestionCategory.PROJECT_OVERVIEW,
                priority=1,
                follow_up_prompts=[
                    "What was your specific contribution?",
                    "How much time did you spend on each?"
                ]
            ),
            InterviewQuestion(
                question_id="emp_3",
                question="Do you document your time by project or activity?",
                category=QuestionCategory.TIME_ALLOCATION,
                priority=2,
                expected_evidence_type="time_tracking"
            ),
        ]

        # Build question list based on interview type
        questions.extend(common_questions)

        if interview_type in [InterviewType.TECHNICAL, InterviewType.PROJECT_LEAD]:
            questions.extend(technical_questions)
        elif interview_type == InterviewType.MANAGEMENT:
            questions.extend(management_questions)
        elif interview_type == InterviewType.EMPLOYEE:
            questions.extend(employee_questions)

        # Sort by priority
        questions.sort(key=lambda q: q.priority)

        return questions

    async def start_session(
        self,
        study_id: UUID,
        interview_type: InterviewType,
        interviewee_name: str,
        interviewee_title: str
    ) -> InterviewSession:
        """Start a new interview session."""
        session = InterviewSession(
            session_id=UUID(int=0),  # Will be generated
            study_id=study_id,
            interview_type=interview_type,
            interviewee_name=interviewee_name,
            interviewee_title=interviewee_title,
            questions_asked=[],
            responses=[],
            projects_identified=[],
            activities_identified=[],
            time_allocations=[],
            uncertainties_identified=[],
            experiments_identified=[],
            summary="",
            confidence_score=0.0,
            follow_up_needed=False,
            follow_up_topics=[],
            started_at=datetime.utcnow(),
            completed_at=None
        )

        return session

    async def get_next_question(
        self,
        session: InterviewSession,
        previous_response: Optional[str] = None
    ) -> Optional[InterviewQuestion]:
        """
        Get the next question based on conversation context.

        Uses AI to determine:
        - If follow-up questions are needed
        - Which standard question to ask next
        - Custom questions based on responses
        """
        question_bank = self.get_question_bank(session.interview_type)
        asked_ids = {q.question_id for q in session.questions_asked}

        # Check if we should ask a follow-up
        if previous_response and session.questions_asked:
            last_question = session.questions_asked[-1]

            # Use AI to determine if follow-up is needed
            follow_up = await self._generate_follow_up(
                last_question, previous_response
            )
            if follow_up:
                return follow_up

        # Get next unanswered question
        for question in question_bank:
            if question.question_id not in asked_ids:
                return question

        return None

    async def process_response(
        self,
        session: InterviewSession,
        question: InterviewQuestion,
        response_text: str
    ) -> InterviewResponse:
        """
        Process an interview response.

        Extracts:
        - Projects mentioned
        - Activities described
        - Time estimates
        - Uncertainties mentioned
        - Experimentation activities
        """
        # Extract information using AI
        extracted = await self._extract_from_response(
            question, response_text, session.interview_type
        )

        response = InterviewResponse(
            question_id=question.question_id,
            response=response_text,
            timestamp=datetime.utcnow(),
            extracted_data=extracted,
            confidence=extracted.get("confidence", 0.5)
        )

        # Update session with extracted data
        session.questions_asked.append(question)
        session.responses.append(response)

        if extracted.get("projects"):
            session.projects_identified.extend(extracted["projects"])
        if extracted.get("activities"):
            session.activities_identified.extend(extracted["activities"])
        if extracted.get("time_allocations"):
            session.time_allocations.extend(extracted["time_allocations"])
        if extracted.get("uncertainties"):
            session.uncertainties_identified.extend(extracted["uncertainties"])
        if extracted.get("experiments"):
            session.experiments_identified.extend(extracted["experiments"])

        return response

    async def complete_session(
        self,
        session: InterviewSession
    ) -> InterviewSession:
        """Complete an interview session and generate summary."""
        session.completed_at = datetime.utcnow()

        # Generate summary
        session.summary = await self._generate_summary(session)

        # Calculate confidence score
        session.confidence_score = self._calculate_session_confidence(session)

        # Determine if follow-up is needed
        session.follow_up_needed, session.follow_up_topics = self._assess_follow_up_needs(session)

        return session

    async def _generate_follow_up(
        self,
        last_question: InterviewQuestion,
        response: str
    ) -> Optional[InterviewQuestion]:
        """Generate a contextual follow-up question."""
        if not self.openai_client:
            return None

        # Check if response needs clarification
        if len(response) < 50:
            return InterviewQuestion(
                question_id=f"followup_{last_question.question_id}",
                question="Can you elaborate on that a bit more?",
                category=last_question.category,
                priority=1
            )

        # Use AI to generate contextual follow-up
        prompt = f"""Based on this interview exchange, determine if a follow-up question is needed.

Question asked: {last_question.question}
Response: {response}

Standard follow-up prompts for this question:
{chr(10).join(last_question.follow_up_prompts) if last_question.follow_up_prompts else 'None'}

If a follow-up is needed, provide it. If the response is complete, respond with "NO_FOLLOWUP".

Focus on gathering information about:
- Specific technical challenges
- Uncertainty about capability, method, or design
- Experimentation processes used
- Time spent on qualified activities

Response format: Either a follow-up question or "NO_FOLLOWUP"."""

        try:
            ai_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )

            follow_up_text = ai_response.choices[0].message.content.strip()

            if follow_up_text and "NO_FOLLOWUP" not in follow_up_text:
                return InterviewQuestion(
                    question_id=f"ai_followup_{last_question.question_id}",
                    question=follow_up_text,
                    category=last_question.category,
                    priority=2
                )

        except Exception as e:
            logger.error(f"Follow-up generation failed: {e}")

        return None

    async def _extract_from_response(
        self,
        question: InterviewQuestion,
        response: str,
        interview_type: InterviewType
    ) -> Dict[str, Any]:
        """Extract structured data from interview response."""
        extracted = {
            "projects": [],
            "activities": [],
            "time_allocations": [],
            "uncertainties": [],
            "experiments": [],
            "confidence": 0.5
        }

        if not self.openai_client:
            return extracted

        prompt = f"""Extract R&D tax credit relevant information from this interview response.

Question: {question.question}
Category: {question.category.value}
Response: {response}

Extract and categorize any mentioned:
1. Projects (name, description, goal)
2. Activities (what was done, who did it)
3. Time allocations (percentage, hours, projects)
4. Technical uncertainties (what was unknown, challenges)
5. Experiments (testing, prototyping, iterations)

Return JSON with these keys:
- projects: [{{name, description, goal}}]
- activities: [{{description, personnel}}]
- time_allocations: [{{percentage, project, source}}]
- uncertainties: [{{description, type}}]
- experiments: [{{description, method}}]
- confidence: 0.0-1.0 (how confident in extractions)"""

        try:
            ai_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )

            import json
            result = json.loads(ai_response.choices[0].message.content)
            extracted.update(result)

        except Exception as e:
            logger.error(f"Response extraction failed: {e}")

        return extracted

    async def _generate_summary(self, session: InterviewSession) -> str:
        """Generate interview summary."""
        if not self.openai_client:
            return "Interview completed. Manual summary required."

        responses_text = "\n".join([
            f"Q: {q.question}\nA: {r.response}"
            for q, r in zip(session.questions_asked, session.responses)
        ])

        prompt = f"""Summarize this R&D tax credit interview.

Interview Type: {session.interview_type.value}
Interviewee: {session.interviewee_name} ({session.interviewee_title})

Interview Transcript:
{responses_text[:6000]}

Provide a concise summary (200-300 words) covering:
1. Key projects discussed
2. Technical challenges and uncertainties identified
3. Experimentation activities mentioned
4. Time allocation information gathered
5. Additional information needed

Be factual and do not embellish the responses."""

        try:
            ai_response = await self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=500
            )

            return ai_response.choices[0].message.content

        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return "Summary generation failed."

    def _calculate_session_confidence(self, session: InterviewSession) -> float:
        """Calculate overall confidence score for the session."""
        if not session.responses:
            return 0.0

        # Base confidence from response quality
        avg_response_length = sum(len(r.response) for r in session.responses) / len(session.responses)
        length_score = min(avg_response_length / 200, 1.0)  # Target 200 chars avg

        # Confidence from extractions
        extraction_count = (
            len(session.projects_identified) +
            len(session.activities_identified) +
            len(session.uncertainties_identified) +
            len(session.experiments_identified)
        )
        extraction_score = min(extraction_count / 10, 1.0)  # Target 10 extractions

        # Confidence from response individual scores
        if session.responses:
            avg_extraction_confidence = sum(
                r.extracted_data.get("confidence", 0.5) for r in session.responses
            ) / len(session.responses)
        else:
            avg_extraction_confidence = 0.5

        # Weight the scores
        overall = (
            length_score * 0.2 +
            extraction_score * 0.3 +
            avg_extraction_confidence * 0.5
        )

        return min(max(overall, 0.1), 0.95)

    def _assess_follow_up_needs(
        self,
        session: InterviewSession
    ) -> tuple[bool, List[str]]:
        """Assess if follow-up interview is needed."""
        follow_up_topics = []

        # Check for missing information
        if not session.projects_identified:
            follow_up_topics.append("No specific projects identified")

        if not session.uncertainties_identified:
            follow_up_topics.append("Technical uncertainties not clearly documented")

        if not session.experiments_identified:
            follow_up_topics.append("Experimentation process not described")

        if not session.time_allocations:
            follow_up_topics.append("Time allocation percentages not provided")

        # Check confidence
        if session.confidence_score < 0.6:
            follow_up_topics.append("Overall low confidence in responses")

        follow_up_needed = len(follow_up_topics) > 0

        return follow_up_needed, follow_up_topics
