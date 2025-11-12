# Production Readiness Implementation Plan
## Aura Audit AI Platform

**Created:** 2025-11-12
**Target Launch:** 6-8 weeks from start
**Priority:** Critical Security Fixes → Feature Completion → Testing → Deployment

---

## PHASE 1: CRITICAL SECURITY FIXES (Week 1-2)
**Duration:** 10-15 days
**Priority:** P0 - Blocking
**Owner:** DevOps + Backend Team

### 1.1 Remove Hardcoded Credentials ⚠️ CRITICAL
**Estimated Time:** 4-6 hours
**Files to Modify:**
- `docker-compose.yml`
- `.env.example`
- All service Dockerfiles

**Implementation Steps:**

1. **Create Environment Variable Structure**
   ```bash
   # Create .env file from template
   cp .env.production.template .env.production

   # Generate secrets
   openssl rand -hex 32 > /tmp/jwt_secret.txt
   openssl rand -hex 32 > /tmp/encryption_key.txt
   openssl rand -hex 32 > /tmp/master_key.txt
   openssl rand -base64 32 > /tmp/fernet_key.txt
   ```

2. **Update docker-compose.yml**
   - Replace all hardcoded values with `${VARIABLE:-default}`
   - Services to update:
     - ✅ `db`: POSTGRES_PASSWORD
     - ✅ `minio`: MINIO_ROOT_PASSWORD
     - ✅ `api-identity`: JWT_SECRET
     - ✅ `api-security`: MASTER_KEY
     - ✅ `api-data-anonymization`: ENCRYPTION_KEY
     - ✅ `airflow-*`: AIRFLOW__CORE__FERNET_KEY, AIRFLOW__WEBSERVER__SECRET_KEY

3. **Create .env.local for Development**
   ```bash
   # Copy example and populate
   cp .env.example .env.local
   ```

4. **Update .gitignore**
   ```
   .env
   .env.local
   .env.production
   .env.*.local
   ```

5. **Documentation**
   - Update QUICK_START.txt with .env setup
   - Add secrets generation guide
   - Document Azure Key Vault integration

**Testing:**
- [ ] Start all services with .env file
- [ ] Verify no hardcoded credentials remain
- [ ] Test authentication flows
- [ ] Verify service-to-service communication

**Success Criteria:**
- ✅ No hardcoded credentials in any tracked file
- ✅ All services start successfully with environment variables
- ✅ Secrets documented in secure location

---

### 1.2 Implement Secure Cookie-Based Authentication ⚠️ CRITICAL
**Estimated Time:** 6-8 hours
**Files to Modify:**
- `frontend/src/lib/api.ts`
- `services/identity/app/main.py`
- `services/gateway/app/main.py`

**Implementation Steps:**

1. **Backend: Update Identity Service**

   Create new file: `services/identity/app/cookie_auth.py`
   ```python
   from fastapi import Response, Cookie
   from datetime import datetime, timedelta

   def set_auth_cookie(response: Response, token: str, expires_in: int = 3600):
       """Set httpOnly, Secure cookie with JWT"""
       expires = datetime.utcnow() + timedelta(seconds=expires_in)
       response.set_cookie(
           key="auth_token",
           value=token,
           httponly=True,
           secure=True,  # HTTPS only
           samesite="strict",
           max_age=expires_in,
           expires=expires,
           domain=os.getenv("COOKIE_DOMAIN", None)
       )
   ```

   Update `services/identity/app/main.py`:
   ```python
   @app.post("/auth/login")
   async def login(response: Response, credentials: LoginRequest):
       # ... existing authentication logic ...
       token = create_jwt(user)
       set_auth_cookie(response, token)
       return {"message": "Login successful", "user": user_data}
   ```

2. **Backend: Update Gateway to Extract from Cookie**

   Update `services/gateway/app/main.py`:
   ```python
   @app.middleware("http")
   async def auth_middleware(request: Request, call_next):
       # Check for token in cookie first, then header
       token = request.cookies.get("auth_token")
       if not token:
           auth_header = request.headers.get("authorization")
           if auth_header and auth_header.startswith("Bearer "):
               token = auth_header.split(" ")[1]

       if token:
           # Add to request state for downstream services
           request.state.token = token
   ```

3. **Frontend: Remove localStorage Usage**

   Update `frontend/src/lib/api.ts`:
   ```typescript
   // Remove localStorage.getItem('auth_token')
   // Cookies sent automatically with credentials: 'include'

   export const apiClient: AxiosInstance = axios.create({
     baseURL: API_URL,
     timeout: 30000,
     withCredentials: true, // Send cookies
     headers: {
       'Content-Type': 'application/json',
     },
   });

   // Remove token injection from request interceptor
   apiClient.interceptors.request.use(
     (config) => {
       // Cookies sent automatically
       return config;
     }
   );
   ```

4. **Implement CSRF Protection**

   Create `services/identity/app/csrf.py`:
   ```python
   import secrets
   from fastapi import HTTPException, Header, Cookie

   def generate_csrf_token() -> str:
       return secrets.token_urlsafe(32)

   def verify_csrf_token(
       csrf_token: str = Header(None, alias="X-CSRF-Token"),
       csrf_cookie: str = Cookie(None, alias="csrf_token")
   ):
       if not csrf_token or not csrf_cookie or csrf_token != csrf_cookie:
           raise HTTPException(401, "Invalid CSRF token")
   ```

**Testing:**
- [ ] Login works with cookies
- [ ] Logout clears cookies
- [ ] CSRF protection works
- [ ] Token not accessible from JavaScript
- [ ] XSS attack simulation fails

**Success Criteria:**
- ✅ Authentication tokens in httpOnly cookies
- ✅ CSRF protection implemented
- ✅ No localStorage usage for tokens
- ✅ XSS protection verified

---

### 1.3 Implement Redis-Backed Rate Limiting ⚠️ CRITICAL
**Estimated Time:** 4-6 hours
**Files to Modify:**
- `services/gateway/app/main.py`
- `services/gateway/requirements.txt`

**Implementation Steps:**

1. **Install Dependencies**
   ```bash
   # Add to services/gateway/requirements.txt
   redis==5.0.1
   slowapi==0.1.9
   ```

2. **Create Redis Rate Limiter**

   Create `services/gateway/app/rate_limiter.py`:
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   import redis.asyncio as redis

   # Connect to Redis
   redis_client = redis.from_url(
       os.getenv("REDIS_URL", "redis://localhost:6379"),
       encoding="utf-8",
       decode_responses=True
   )

   # Create limiter with Redis backend
   limiter = Limiter(
       key_func=get_remote_address,
       storage_uri=os.getenv("REDIS_URL", "redis://localhost:6379"),
       default_limits=["120/minute"]
   )
   ```

3. **Update Gateway to Use Redis Limiter**

   Update `services/gateway/app/main.py`:
   ```python
   from slowapi import _rate_limit_exceeded_handler
   from slowapi.errors import RateLimitExceeded
   from .rate_limiter import limiter

   app = FastAPI(...)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

   # Remove old in-memory rate limiter
   # Remove: rate_limit_storage: Dict[str, list] = defaultdict(list)

   @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
   @limiter.limit("120/minute")
   async def gateway(request: Request, path: str):
       # ... existing code ...
   ```

4. **Add Per-Endpoint Rate Limits**
   ```python
   # Different limits for different endpoints
   ENDPOINT_LIMITS = {
       "/auth/login": "5/minute",
       "/auth/register": "3/minute",
       "/llm/chat": "20/minute",
       "/reports/generate": "10/minute",
   }
   ```

5. **Test Rate Limiting**
   ```bash
   # Load test script
   for i in {1..150}; do
     curl -X GET http://localhost:8000/health
   done
   # Should see 429 errors after 120 requests
   ```

**Testing:**
- [ ] Rate limiting works across multiple gateway instances
- [ ] Limits persist after gateway restart
- [ ] Different endpoints have different limits
- [ ] Rate limit headers returned (X-RateLimit-*)

**Success Criteria:**
- ✅ Redis-backed rate limiting operational
- ✅ Works in distributed environment
- ✅ Survives service restarts
- ✅ Per-endpoint limits configurable

---

### 1.4 Enable SSL/TLS for Database Connections
**Estimated Time:** 2-3 hours
**Files to Modify:**
- `docker-compose.yml`
- `.env.production.template`
- All service database connection strings

**Implementation Steps:**

1. **Update All DATABASE_URL References**
   ```yaml
   # docker-compose.yml - Add ?sslmode=require
   DATABASE_URL=postgresql://atlas:${POSTGRES_PASSWORD}@db:5432/atlas?sslmode=require
   ```

2. **Update Production Template**
   ```bash
   # .env.production.template
   DATABASE_URL=postgresql://atlasadmin:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/atlas?sslmode=require
   ```

3. **Update SQLAlchemy Connection**

   Create `services/common/db.py` (shared utility):
   ```python
   from sqlalchemy.ext.asyncio import create_async_engine

   def get_database_engine(database_url: str):
       # Ensure SSL in production
       connect_args = {}
       if "sslmode=require" in database_url:
           connect_args["ssl"] = "require"

       return create_async_engine(
           database_url,
           echo=False,
           pool_size=20,
           max_overflow=10,
           connect_args=connect_args
       )
   ```

**Testing:**
- [ ] Local development still works (SSL optional)
- [ ] Production connections use SSL
- [ ] Connection pooling works with SSL

**Success Criteria:**
- ✅ All database connections use SSL in production
- ✅ Development still works with local PostgreSQL
- ✅ No connection errors

---

### 1.5 Update CORS Configuration
**Estimated Time:** 1-2 hours
**Files to Modify:**
- `services/gateway/app/main.py`
- `services/identity/app/main.py`
- `.env.production.template`

**Implementation Steps:**

1. **Update Gateway CORS**
   ```python
   # services/gateway/app/main.py
   import os

   # Get origins from environment
   allowed_origins = os.getenv(
       "CORS_ORIGINS",
       "http://localhost:3000,http://localhost:5173,http://localhost:3001"
   ).split(",")

   app.add_middleware(
       CORSMiddleware,
       allow_origins=allowed_origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
       expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"]
   )
   ```

2. **Add Production Domains**
   ```bash
   # .env.production
   CORS_ORIGINS=https://aura-audit-ai.com,https://app.aura-audit-ai.com,https://admin.aura-audit-ai.com,https://client.aura-audit-ai.com
   ```

**Success Criteria:**
- ✅ CORS configured from environment
- ✅ Production domains whitelisted
- ✅ Credentials (cookies) allowed

---

### 1.6 Create Secrets Generation Script
**Estimated Time:** 2-3 hours
**New File:** `scripts/generate-secrets.sh`

**Implementation Steps:**

1. **Create Script**
   ```bash
   #!/bin/bash
   # scripts/generate-secrets.sh

   echo "Generating secure secrets for Aura Audit AI..."

   # Generate secrets
   JWT_SECRET=$(openssl rand -hex 32)
   ENCRYPTION_KEY=$(openssl rand -hex 32)
   MASTER_KEY=$(openssl rand -hex 32)
   FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
   POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
   MINIO_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

   # Create .env file
   cat > .env.production << EOF
   # Generated on $(date)

   # Database
   POSTGRES_PASSWORD=$POSTGRES_PASSWORD
   DATABASE_URL=postgresql://atlas:$POSTGRES_PASSWORD@db:5432/atlas?sslmode=require

   # Authentication
   JWT_SECRET=$JWT_SECRET
   JWT_ALGORITHM=HS256

   # Encryption
   ENCRYPTION_KEY=$ENCRYPTION_KEY
   MASTER_KEY=$MASTER_KEY

   # Airflow
   AIRFLOW__CORE__FERNET_KEY=$FERNET_KEY

   # Storage
   MINIO_ROOT_PASSWORD=$MINIO_PASSWORD
   S3_SECRET_KEY=$MINIO_PASSWORD

   EOF

   echo "✅ Secrets generated and saved to .env.production"
   echo "⚠️  IMPORTANT: Store these secrets in Azure Key Vault!"
   echo "⚠️  DO NOT commit .env.production to git!"
   ```

2. **Make Executable**
   ```bash
   chmod +x scripts/generate-secrets.sh
   ```

3. **Add to Documentation**
   Update `AZURE_DEPLOYMENT.md` with secrets setup instructions

**Success Criteria:**
- ✅ Script generates strong secrets
- ✅ Secrets saved to .env file
- ✅ Documentation updated

---

## PHASE 2: FEATURE COMPLETION (Week 3-4)
**Duration:** 10-12 days
**Priority:** P0/P1 - Blocking Launch

### 2.1 Complete DocuSign JWT Authentication
**Estimated Time:** 8-10 hours
**Files to Modify:**
- `services/reporting/app/docusign_service.py`
- `services/reporting/requirements.txt`

**Implementation Steps:**

1. **Install DocuSign SDK**
   ```bash
   # Add to requirements.txt
   docusign-esign==3.24.0
   pyjwt==2.8.0
   cryptography==41.0.7
   ```

2. **Implement JWT Authentication**
   ```python
   import time
   import jwt
   from docusign_esign import ApiClient, EnvelopesApi
   from cryptography.hazmat.primitives import serialization

   class DocuSignService:
       def __init__(self):
           self.integration_key = os.getenv("DOCUSIGN_INTEGRATION_KEY")
           self.account_id = os.getenv("DOCUSIGN_ACCOUNT_ID")
           self.user_id = os.getenv("DOCUSIGN_USER_ID")
           self.base_url = os.getenv("DOCUSIGN_BASE_URL")
           self.private_key_path = os.getenv("DOCUSIGN_PRIVATE_KEY_PATH")

       def get_jwt_token(self) -> str:
           """Generate JWT for service account authentication"""
           with open(self.private_key_path, 'rb') as key_file:
               private_key = key_file.read()

           now = int(time.time())
           payload = {
               "iss": self.integration_key,
               "sub": self.user_id,
               "aud": "account-d.docusign.com",
               "iat": now,
               "exp": now + 3600,
               "scope": "signature impersonation"
           }

           token = jwt.encode(payload, private_key, algorithm='RS256')
           return token

       def get_access_token(self) -> str:
           """Exchange JWT for access token"""
           # Implementation
   ```

3. **Implement Envelope Creation**
   ```python
   async def create_envelope(
       self,
       report_id: str,
       signers: List[Dict],
       document_bytes: bytes
   ) -> str:
       """Create DocuSign envelope for report"""
       # Implementation
   ```

4. **Add Webhook Handler**
   ```python
   @app.post("/reporting/docusign/webhook")
   async def docusign_webhook(request: Request):
       """Handle DocuSign status updates"""
       # Verify signature, update report status
   ```

**Testing:**
- [ ] JWT generation works
- [ ] Envelope creation successful
- [ ] Signature flow completes
- [ ] Webhook updates received
- [ ] Completed documents stored

**Success Criteria:**
- ✅ Full DocuSign integration working
- ✅ Reports can be sent for signature
- ✅ Status updates received
- ✅ Signed documents archived

---

### 2.2 Decision: Tax Features - Keep or Remove
**Estimated Time:** 2 hours (decision) + 30 hours (if keeping)

**Option A: Remove from MVP**
- Delete services: tax-ocr-intake, tax-review, tax-forms, tax-engine
- Update gateway routing
- Update documentation
- **Time saved:** 30+ hours

**Option B: Complete for MVP**
- Implement 11 TODOs in tax-ocr-intake
- Implement 9 TODOs in tax-review
- Implement 5 TODOs in tax-engine
- Complete tax-forms service
- **Time required:** 30-40 hours

**Recommendation:** Remove from MVP, add in Phase 2 post-launch

---

### 2.3 Complete Analytics Features
**Estimated Time:** 6-8 hours

**Items:**
1. Implement Isolation Forest for JE testing
2. Add ML model training pipeline
3. Complete anomaly detection scoring

---

## PHASE 3: TESTING & QUALITY (Week 5-6)
**Duration:** 10-12 days
**Priority:** P1 - Quality Gate

### 3.1 Unit Test Coverage Sprint
**Target:** 80%+ coverage for critical services

**Priority Services:**
1. Identity (authentication) - Target: 90%
2. Gateway (routing) - Target: 85%
3. Engagement (core workflow) - Target: 85%
4. Reporting (critical output) - Target: 85%
5. Analytics (data integrity) - Target: 80%

### 3.2 Integration Testing
**Estimated Time:** 15-20 hours

1. API contract tests
2. Service-to-service communication
3. Database transaction tests
4. Cache invalidation tests

### 3.3 End-to-End Testing
**Estimated Time:** 20-25 hours

**Critical User Flows:**
1. User registration → email verification → login
2. Create engagement → assign team → upload data
3. Normalize accounts → run analytics → generate report
4. Send report for e-signature → track status → archive
5. QC review process

### 3.4 Load Testing
**Tools:** k6, Locust, or Apache JMeter

**Scenarios:**
- 50 concurrent users (typical)
- 100 concurrent users (peak)
- 500 concurrent users (stress test)

**Targets:**
- P95 response time: <2 seconds
- P99 response time: <5 seconds
- Error rate: <0.1%

---

## PHASE 4: INFRASTRUCTURE & MONITORING (Week 7-8)
**Duration:** 8-10 days

### 4.1 Implement Structured Logging
### 4.2 Add Prometheus Metrics
### 4.3 Configure Alerting Rules
### 4.4 Set Up Log Aggregation
### 4.5 Create Operational Runbooks

---

## PHASE 5: DEPLOYMENT (Week 9-12)
### 5.1 Staging Deployment
### 5.2 Production Deployment
### 5.3 Smoke Testing
### 5.4 Customer Pilot

---

## RISK REGISTER

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| DocuSign integration delays | Medium | High | Start early, have backup plan |
| Test coverage not achieved | Medium | High | Daily tracking, pair testing |
| Performance issues at scale | Low | High | Load test early, optimize hot paths |
| Database migration issues | Low | Critical | Test on staging, have rollback plan |
| Third-party API downtime | Medium | Medium | Implement circuit breakers |

---

## DAILY PROGRESS TRACKING

### Week 1
- [ ] Day 1: Remove hardcoded credentials
- [ ] Day 2: Implement cookie auth backend
- [ ] Day 3: Implement cookie auth frontend
- [ ] Day 4: Implement Redis rate limiting
- [ ] Day 5: SSL/TLS + CORS updates

### Week 2
- [ ] Day 1-2: DocuSign JWT implementation
- [ ] Day 3: DocuSign testing
- [ ] Day 4: Tax features decision
- [ ] Day 5: Analytics completion

---

## SUCCESS METRICS

### Security
- ✅ 0 hardcoded credentials
- ✅ 0 P0 security vulnerabilities
- ✅ All connections encrypted
- ✅ Auth tokens in secure cookies

### Quality
- ✅ 80%+ test coverage
- ✅ <0.1% error rate
- ✅ <2s P95 response time

### Features
- ✅ 100% core features complete
- ✅ All P0 TODOs resolved
- ✅ E2E flows working

---

## CONTACT & ESCALATION

**Technical Blockers:** Escalate after 4 hours
**Security Issues:** Escalate immediately
**Scope Changes:** Require approval

---

**Next Steps:** Execute Phase 1.1 - Remove Hardcoded Credentials
