"""
AI Chat Service for Audits

Natural language querying of audit data - "ChatGPT for Audits"

Features:
- Ask questions about engagement data in natural language
- Retrieval-Augmented Generation (RAG) from work papers
- SQL generation for complex queries
- Citation of sources (work paper references)
- Conversation history and context
- Multi-turn conversations

Examples:
- "What was the biggest risk identified in the revenue cycle?"
- "Show me all journal entries over materiality in December"
- "Summarize the going concern assessment"
- "Compare this year's gross margin to last year"
- "What procedures did we perform for ASC 606?"

Impact: 10x faster data exploration, better audit insights
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
import json

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
import openai
from loguru import logger

from .database import get_db
from .config import settings
from .rag_engine import AuditRAGEngine


app = FastAPI(
    title="AI Chat Service",
    description="Natural language querying for audit engagements",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MessageRole(str, Enum):
    """Chat message roles"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Single chat message"""
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    citations: Optional[List[Dict[str, str]]] = None


class ChatRequest(BaseModel):
    """Request to chat with audit AI"""
    engagement_id: str
    message: str
    conversation_id: Optional[str] = None  # For continuing conversation
    include_context: bool = True  # Include engagement data in context


class ChatResponse(BaseModel):
    """Response from audit AI"""
    conversation_id: str
    message: str
    citations: List[Dict[str, str]]
    suggested_followups: List[str]
    data: Optional[Dict] = None  # Structured data if query returned results
    sql_generated: Optional[str] = None  # SQL query if generated


class AuditChatEngine:
    """
    Conversational AI for audit engagements

    Capabilities:
    - Answer questions about engagement data
    - Generate SQL queries from natural language
    - Retrieve relevant work papers
    - Provide audit procedure guidance
    - Explain financial metrics
    """

    def __init__(self):
        # OpenAI setup
        openai.api_type = "azure"
        openai.api_base = settings.AZURE_OPENAI_ENDPOINT
        openai.api_key = settings.AZURE_OPENAI_API_KEY
        openai.api_version = settings.AZURE_OPENAI_API_VERSION

        # RAG engine for work paper retrieval
        self.rag_engine = AuditRAGEngine()

        # Conversation history (in-memory cache, would use Redis in production)
        self.conversations: Dict[str, List[ChatMessage]] = {}

    async def chat(
        self,
        engagement_id: str,
        message: str,
        conversation_id: Optional[str] = None,
        db: AsyncSession = None,
    ) -> ChatResponse:
        """
        Process chat message and generate response

        Args:
            engagement_id: Engagement ID for context
            message: User's question
            conversation_id: Conversation ID (for multi-turn)
            db: Database session
        """

        # Get or create conversation
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
        else:
            conversation_id = f"conv_{engagement_id}_{datetime.utcnow().timestamp()}"
            conversation = []
            self.conversations[conversation_id] = conversation

        # Add user message to history
        user_msg = ChatMessage(role=MessageRole.USER, content=message)
        conversation.append(user_msg)

        # Retrieve relevant context
        context = await self._retrieve_context(engagement_id, message, db)

        # Build prompt
        system_prompt = self._build_system_prompt(engagement_id, context)

        # Build message history
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history (last 5 turns)
        for msg in conversation[-10:]:  # Last 10 messages (5 turns)
            messages.append({
                "role": msg.role.value,
                "content": msg.content,
            })

        # Call GPT-4
        try:
            response = await openai.ChatCompletion.acreate(
                engine=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                temperature=0.3,  # Low temperature for accuracy
                max_tokens=1500,
            )

            assistant_message = response.choices[0].message.content

            # Parse response for citations
            citations = self._extract_citations(assistant_message)

            # Check if SQL was generated
            sql_query = self._extract_sql(assistant_message)

            # Execute SQL if present
            data = None
            if sql_query and db:
                data = await self._execute_sql(sql_query, db)

            # Generate suggested follow-ups
            followups = self._generate_followups(message, assistant_message, context)

            # Add assistant message to history
            assistant_msg = ChatMessage(
                role=MessageRole.ASSISTANT,
                content=assistant_message,
                citations=citations,
            )
            conversation.append(assistant_msg)

            return ChatResponse(
                conversation_id=conversation_id,
                message=assistant_message,
                citations=citations,
                suggested_followups=followups,
                data=data,
                sql_generated=sql_query,
            )

        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise HTTPException(500, f"Chat failed: {str(e)}")

    async def _retrieve_context(
        self,
        engagement_id: str,
        message: str,
        db: AsyncSession
    ) -> Dict[str, any]:
        """
        Retrieve relevant context for the question

        Sources:
        - Engagement metadata
        - Financial statements
        - Trial balance
        - Work papers
        - Risk assessments
        - Prior conversations
        """

        context = {}

        # Get engagement metadata
        result = await db.execute(
            text("SELECT * FROM engagements WHERE id = :id"),
            {"id": engagement_id}
        )
        engagement = result.fetchone()

        if engagement:
            context["engagement"] = {
                "client_name": engagement.client_name,
                "fiscal_year_end": engagement.fiscal_year_end.isoformat(),
                "engagement_type": engagement.engagement_type,
                "status": engagement.status,
            }

        # Get financial summary
        result = await db.execute(
            text("""
                SELECT
                    SUM(CASE WHEN debit > 0 THEN debit ELSE 0 END) as total_debits,
                    SUM(CASE WHEN credit > 0 THEN credit ELSE 0 END) as total_credits,
                    COUNT(*) as line_count
                FROM trial_balance_lines
                WHERE trial_balance_id IN (
                    SELECT id FROM trial_balances WHERE engagement_id = :id
                )
            """),
            {"id": engagement_id}
        )
        financials = result.fetchone()

        if financials:
            context["financials"] = {
                "total_debits": float(financials.total_debits or 0),
                "total_credits": float(financials.total_credits or 0),
                "line_count": financials.line_count,
            }

        # Retrieve relevant work papers using RAG
        workpapers = await self.rag_engine.search(
            query=message,
            engagement_id=engagement_id,
            top_k=3
        )

        context["workpapers"] = workpapers

        return context

    def _build_system_prompt(
        self,
        engagement_id: str,
        context: Dict
    ) -> str:
        """Build system prompt with context"""

        prompt = f"""You are an expert audit AI assistant with access to:

**Engagement**: {context.get('engagement', {}).get('client_name', 'Unknown')}
**Fiscal Year End**: {context.get('engagement', {}).get('fiscal_year_end', 'Unknown')}

**Available Data**:
- Financial statements and trial balance
- Journal entries
- Work papers and documentation
- Risk assessments
- Audit procedures performed

**Capabilities**:
1. Answer questions about the audit engagement
2. Explain financial metrics and trends
3. Retrieve specific transactions or accounts
4. Summarize audit procedures and findings
5. Generate SQL queries for complex data requests

**Instructions**:
- Always cite your sources (use format: [Work Paper A-1])
- If you generate SQL, enclose it in ```sql ... ``` blocks
- Be concise but thorough
- If you're uncertain, say so
- Focus on audit-relevant insights

**Context**:
"""

        # Add financial context
        if "financials" in context:
            financials = context["financials"]
            prompt += f"""
Trial Balance Summary:
- Total Debits: ${financials['total_debits']:,.2f}
- Total Credits: ${financials['total_credits']:,.2f}
- Line Items: {financials['line_count']}
"""

        # Add work paper context
        if "workpapers" in context and context["workpapers"]:
            prompt += "\n**Relevant Work Papers**:\n"
            for wp in context["workpapers"][:3]:
                prompt += f"- {wp.get('reference', 'Unknown')}: {wp.get('title', 'Unknown')}\n"
                prompt += f"  {wp.get('summary', '')[:200]}...\n"

        return prompt

    def _extract_citations(self, message: str) -> List[Dict[str, str]]:
        """Extract citations from assistant message"""

        import re

        citations = []

        # Find citations in format [Work Paper A-1], [AS 2110], etc.
        pattern = r'\[(Work Paper |WP |AS |ASC |AU-C )?([^\]]+)\]'
        matches = re.finditer(pattern, message)

        for match in matches:
            citation_type = match.group(1) or "Reference"
            citation_value = match.group(2)

            citations.append({
                "type": citation_type.strip(),
                "value": citation_value,
                "text": match.group(0),
            })

        return citations

    def _extract_sql(self, message: str) -> Optional[str]:
        """Extract SQL query from assistant message"""

        import re

        # Find SQL in code blocks
        pattern = r'```sql\n(.*?)\n```'
        match = re.search(pattern, message, re.DOTALL)

        if match:
            return match.group(1).strip()

        return None

    async def _execute_sql(
        self,
        sql_query: str,
        db: AsyncSession
    ) -> Optional[Dict]:
        """
        Execute SQL query safely

        Security: Only allow SELECT queries
        """

        # Security check: only SELECT allowed
        if not sql_query.strip().upper().startswith("SELECT"):
            logger.warning(f"Blocked non-SELECT query: {sql_query}")
            return {"error": "Only SELECT queries are allowed"}

        try:
            result = await db.execute(text(sql_query))
            rows = result.fetchall()

            # Convert to dict
            data = []
            if rows:
                columns = result.keys()
                for row in rows[:100]:  # Limit to 100 rows
                    data.append(dict(zip(columns, row)))

            return {
                "row_count": len(data),
                "rows": data,
            }

        except Exception as e:
            logger.error(f"SQL execution error: {e}")
            return {"error": str(e)}

    def _generate_followups(
        self,
        user_message: str,
        assistant_message: str,
        context: Dict
    ) -> List[str]:
        """Generate suggested follow-up questions"""

        # Default follow-ups
        followups = []

        # Context-aware suggestions
        if "revenue" in user_message.lower():
            followups.extend([
                "What procedures did we perform for revenue testing?",
                "Were there any exceptions in revenue sampling?",
                "Show me the revenue cutoff testing results",
            ])
        elif "risk" in user_message.lower():
            followups.extend([
                "What were the key audit matters identified?",
                "Show me the fraud risk assessment",
                "What controls were tested?",
            ])
        elif "journal" in user_message.lower() or "entry" in user_message.lower():
            followups.extend([
                "Show me all manual journal entries",
                "Were any journal entries flagged as high-risk?",
                "What was the largest journal entry?",
            ])
        elif "materiality" in user_message.lower():
            followups.extend([
                "How was materiality calculated?",
                "Were any uncorrected misstatements recorded?",
                "What is the summary of unadjusted differences?",
            ])
        else:
            # Generic follow-ups
            followups.extend([
                "What were the significant risks identified?",
                "Show me the financial statement summary",
                "Were there any audit findings?",
            ])

        return followups[:3]  # Return top 3


# Global chat engine
chat_engine = AuditChatEngine()


@app.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Chat with audit AI

    Send a question and get an AI-generated response with citations
    """

    response = await chat_engine.chat(
        engagement_id=request.engagement_id,
        message=request.message,
        conversation_id=request.conversation_id,
        db=db,
    )

    return response


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history"""

    if conversation_id not in chat_engine.conversations:
        raise HTTPException(404, "Conversation not found")

    conversation = chat_engine.conversations[conversation_id]

    return {
        "conversation_id": conversation_id,
        "message_count": len(conversation),
        "messages": [
            {
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "citations": msg.citations,
            }
            for msg in conversation
        ]
    }


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation history"""

    if conversation_id in chat_engine.conversations:
        del chat_engine.conversations[conversation_id]
        return {"message": "Conversation deleted"}

    raise HTTPException(404, "Conversation not found")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Chat"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)
