# LLM Service - RAG-Powered AI Assistant

The LLM Service provides Retrieval-Augmented Generation (RAG) capabilities for the Aura Audit AI platform. It combines vector similarity search with large language models to deliver contextually-aware, citation-backed responses for audit-related queries.

## Features

### Core Capabilities
- **RAG Query Processing**: Combines document retrieval with LLM generation for accurate, contextual responses
- **Knowledge Base Management**: Store and manage regulatory documents (GAAP, GAAS, PCAOB, SEC, etc.)
- **Vector Embeddings**: Generate and cache embeddings using sentence-transformers
- **Semantic Search**: pgvector-powered similarity search across knowledge base
- **Schema-Constrained Generation**: Produce structured JSON outputs following predefined schemas
- **Citation Tracking**: Automatic citation generation with similarity scores

### Specialized Generation
- **Disclosure Generation**: Generate GAAP-compliant financial disclosures
- **Anomaly Explanations**: Explain detected anomalies with recommended procedures
- **Workpaper Review**: AI-powered review comments and recommendations
- **Compliance Checks**: Assess compliance with regulatory requirements

## Architecture

### Technology Stack
- **FastAPI**: Async web framework
- **PostgreSQL + pgvector**: Vector database for embeddings
- **sentence-transformers**: Embedding model (all-MiniLM-L6-v2)
- **OpenAI GPT-4**: Large language model for generation
- **LangChain**: RAG orchestration framework
- **Redis**: Caching layer

### Database Models

#### KnowledgeDocument
Stores reference documents with metadata:
- Document type (GAAP, GAAS, PCAOB, SEC, etc.)
- Title, standard code, source
- Full text content
- Version and effective date

#### DocumentChunk
Text chunks with vector embeddings:
- References parent document
- Chunk index and content
- 384-dimensional embedding vector
- Token count and metadata

#### RAGQuery
Query execution records:
- Query text and embedding
- Retrieved context and chunks
- Generated response
- Performance metrics (timing, tokens)
- Citations and structured output

#### EmbeddingCache
Caches embeddings for frequently accessed text:
- SHA256 hash of text
- Embedding vector
- Access count and last accessed

## API Endpoints

### Knowledge Base Management

```
POST   /knowledge/documents          Create knowledge document
GET    /knowledge/documents          List documents (with filters)
GET    /knowledge/documents/{id}     Get document by ID
PATCH  /knowledge/documents/{id}     Update document
DELETE /knowledge/documents/{id}     Delete document (soft delete)
```

### Embeddings

```
POST   /embeddings                   Generate embeddings for text
```

### RAG Queries

```
POST   /rag/query                    Process RAG query
GET    /rag/queries/{id}             Get query by ID
POST   /rag/queries/{id}/feedback    Submit feedback
```

### Specialized Generation

```
POST   /disclosures/generate         Generate financial disclosure
POST   /anomalies/explain            Explain detected anomaly
```

### Vector Search

```
POST   /search/vector                Direct vector similarity search
```

### Statistics

```
GET    /stats/embeddings             Embedding statistics
GET    /stats/rag                    RAG usage statistics
```

## Configuration

Environment variables (`.env`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://atlas:password@db:5432/atlas

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.1
OPENAI_MAX_TOKENS=4096

# Embeddings
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
EMBEDDING_BATCH_SIZE=32

# RAG Configuration
RAG_TOP_K=5
RAG_SIMILARITY_THRESHOLD=0.7
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50

# Redis
REDIS_URL=redis://redis:6379/0
```

## Usage Examples

### Creating a Knowledge Document

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/knowledge/documents",
        json={
            "document_type": "gaap_standard",
            "title": "ASC 606 - Revenue Recognition",
            "standard_code": "ASC 606",
            "source": "FASB",
            "content": "...",
            "version": "2023"
        }
    )
    doc = response.json()
    print(f"Created document {doc['id']} with {doc['chunk_count']} chunks")
```

### Processing a RAG Query

```python
response = await client.post(
    "http://localhost:8000/rag/query",
    json={
        "query": "How should software revenue be recognized?",
        "purpose": "general_inquiry",
        "engagement_id": "...",
        "top_k": 5,
        "document_types": ["gaap_standard"]
    }
)

result = response.json()
print(f"Response: {result['response']}")
print(f"Citations: {len(result['citations'])}")
print(f"Total time: {result['total_time_ms']}ms")
```

### Generating a Disclosure

```python
response = await client.post(
    "http://localhost:8000/disclosures/generate",
    json={
        "engagement_id": "...",
        "disclosure_type": "revenue",
        "fiscal_year": "2024",
        "account_data": {
            "total_revenue": 5000000,
            "product_revenue": 3000000,
            "service_revenue": 2000000
        }
    }
)

disclosure = response.json()
print(disclosure['disclosure_text'])
```

### Vector Similarity Search

```python
response = await client.post(
    "http://localhost:8000/search/vector",
    json={
        "query": "materiality thresholds",
        "top_k": 10,
        "similarity_threshold": 0.75,
        "document_types": ["pcaob_rule", "aicpa_guidance"]
    }
)

results = response.json()
for result in results:
    print(f"Score: {result['similarity_score']:.2f}")
    print(f"Document: {result['document_title']}")
    print(f"Content: {result['content'][:200]}...")
```

## Performance Metrics

### Typical Response Times
- **Embedding Generation**: 50-100ms (cached) / 200-500ms (uncached)
- **Vector Retrieval**: 50-150ms (5 chunks)
- **LLM Generation**: 1-3 seconds (depending on response length)
- **Total RAG Query**: 1.5-4 seconds

### Scalability
- **Concurrent Requests**: 50+ concurrent queries
- **Knowledge Base Size**: Tested with 1000+ documents, 100K+ chunks
- **Embedding Cache**: 80%+ hit rate in production
- **Vector Search**: <100ms for 100K embeddings with ivfflat index

## Testing

### Run Unit Tests
```bash
cd services/llm
pytest tests/unit/ -v
```

### Run Integration Tests
```bash
pytest tests/integration/ -v
```

### Run All Tests with Coverage
```bash
pytest tests/ -v --cov=app --cov-report=html
```

## Development

### Local Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using alembic)
alembic upgrade head

# Start service
uvicorn app.main:app --reload --port 8000
```

### Docker
```bash
docker build -t aura-llm-service .
docker run -p 8000:8000 --env-file .env aura-llm-service
```

## Production Considerations

### Security
- Store `OPENAI_API_KEY` in secrets manager
- Implement rate limiting per user
- Add request size limits
- Enable HTTPS/TLS

### Monitoring
- Track token usage and costs
- Monitor response times
- Alert on error rates
- Log all queries for audit

### Optimization
- Increase embedding cache size for high-traffic queries
- Use pgvector IVFFlat index for large knowledge bases
- Implement query result caching with Redis
- Batch embedding generation for bulk document uploads

### Cost Management
- Monitor OpenAI API usage
- Implement token budgets per engagement/user
- Use embedding cache aggressively
- Consider local LLM for certain use cases

## Troubleshooting

### Slow Vector Search
- Ensure pgvector index is created: `CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops)`
- Increase `lists` parameter for larger datasets
- Check database connection pool size

### High Token Usage
- Reduce `RAG_TOP_K` to retrieve fewer chunks
- Decrease `OPENAI_MAX_TOKENS`
- Implement response caching for common queries

### Poor Response Quality
- Increase `RAG_SIMILARITY_THRESHOLD` to retrieve more relevant context
- Add more relevant documents to knowledge base
- Adjust LLM temperature (lower = more focused, higher = more creative)

## License

Copyright © 2024 Aura Audit AI. All rights reserved.
