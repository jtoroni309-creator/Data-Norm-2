"""
Aura Audit AI - Identity & Authentication Service

Production-grade authentication with:
- JWT token management
- OIDC integration (Azure AD, Okta)
- Role-based access control (RBAC)
- Password hashing (bcrypt)
- Session management
- Audit logging
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import FastAPI, HTTPException, Depends, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from passlib.context import CryptContext
from jose import JWTError, jwt

from app.config import settings
from app.database import get_db, init_db
from app.models import User, Organization, LoginAuditLog, UserInvitation, UserPermission, Client, PasswordResetToken
from app.schemas import (
    UserCreate,
    UserResponse,
    TokenResponse,
    LoginRequest,
    HealthResponse,
    RoleEnum,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    UserInvitationCreate,
    UserInvitationResponse,
    UserInvitationAccept,
    UserInvitationValidateResponse,
    UserPermissionUpdate,
    UserPermissionResponse,
    UserUpdate,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    PasswordResetRequest,
    PasswordResetResponse,
    PasswordResetConfirm,
    RDStudyClientInvitationCreate,
    RDStudyClientInvitationResponse,
    RDStudyClientInvitationValidate
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

app = FastAPI(
    title="Aura Audit AI - Identity Service",
    description="Authentication, authorization, and user management",
    version="1.0.0",
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Utility Functions
# ========================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Payload to encode (user_id, email, roles)
        expires_delta: Token expiration time (default: 8 hours)

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token

    Usage:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": str(user.id)}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

    # Fetch user from database
    result = await db.execute(
        select(User).where(
            and_(
                User.id == UUID(user_id),
                User.is_active == True
            )
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    return user


def require_role(allowed_roles: List[RoleEnum]):
    """
    Dependency factory for role-based access control

    Usage:
        @app.post("/engagements")
        async def create_engagement(
            user: User = Depends(require_role([RoleEnum.PARTNER, RoleEnum.MANAGER]))
        ):
            ...
    """
    async def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}"
            )
        return user

    return role_checker


async def log_login_attempt(
    db: AsyncSession,
    email: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Log authentication attempt for audit trail"""
    try:
        log_entry = LoginAuditLog(
            email=email,
            success=success,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message,
            attempted_at=datetime.utcnow()
        )
        db.add(log_entry)
        await db.commit()
    except Exception as e:
        # Don't fail login if audit logging fails
        logger.warning(f"Failed to log login attempt for {email}: {str(e)}")
        await db.rollback()


# ========================================
# Health & Status
# ========================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="identity",
        version="1.0.0"
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Aura Audit AI - Identity Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# ========================================
# Authentication Endpoints
# ========================================

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user

    - Validates email uniqueness
    - Hashes password
    - Creates user record
    - Returns user info (no password)
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user (note: role is handled separately via user_permissions table)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        organization_id=user_data.organization_id,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")

    # Build response manually since the model doesn't have role
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=user_data.role,
        organization_id=new_user.organization_id,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        last_login_at=new_user.last_login_at
    )


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token (JSON)

    - Validates credentials
    - Logs login attempt
    - Returns access token
    """
    email = credentials.email
    password = credentials.password

    # Fetch user by email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    # Validate credentials
    if not user or not verify_password(password, user.hashed_password):
        await log_login_attempt(
            db=db,
            email=email,
            success=False,
            error_message="Invalid credentials"
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        await log_login_attempt(
            db=db,
            email=email,
            success=False,
            error_message="Account inactive"
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "cpa_firm_id": str(user.cpa_firm_id) if user.cpa_firm_id else None,
            "client_id": str(user.client_id) if user.client_id else None
        }
    )

    # Log successful login
    await log_login_attempt(
        db=db,
        email=user.email,
        success=True
    )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600,
        user=UserResponse.model_validate(user)
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse.model_validate(current_user)


@app.post("/auth/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset

    - Validates email exists
    - Creates password reset token
    - In production, would send email with reset link
    """
    import secrets

    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {request.email}")
        return PasswordResetResponse(
            message="If the email exists, a password reset link will be sent"
        )

    # Invalidate any existing tokens for this user
    await db.execute(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at == None
            )
        )
    )

    # Generate secure token
    token = secrets.token_urlsafe(32)

    # Create reset token (expires in 1 hour)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )

    db.add(reset_token)
    await db.commit()

    # TODO: In production, send email with reset link
    # For now, log the token (in production this would be removed)
    logger.info(f"Password reset token created for {user.email}: {token}")

    return PasswordResetResponse(
        message="If the email exists, a password reset link will be sent"
    )


@app.post("/auth/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password with token

    - Validates token
    - Updates password
    - Invalidates token
    """
    # Find token
    result = await db.execute(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == request.token,
                PasswordResetToken.used_at == None,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        )
    )
    token_record = result.scalar_one_or_none()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Find user
    result = await db.execute(
        select(User).where(User.id == token_record.user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    # Update password
    user.password_hash = hash_password(request.new_password)
    user.last_password_change = datetime.utcnow()
    user.require_password_change = False

    # Mark token as used
    token_record.used_at = datetime.utcnow()

    await db.commit()

    logger.info(f"Password reset successful for user: {user.email}")

    return PasswordResetResponse(
        message="Password has been reset successfully"
    )


@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh access token (extends session)"""

    access_token = create_access_token(
        data={
            "sub": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role.value,
            "organization_id": str(current_user.organization_id) if current_user.organization_id else None
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600
    )


# ========================================
# User Management (Admin)
# ========================================

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_role([RoleEnum.PARTNER, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    List users in organization

    Requires: Partner or Manager role
    """
    result = await db.execute(
        select(User)
        .where(User.organization_id == current_user.organization_id)
        .offset(skip)
        .limit(limit)
    )
    users = result.scalars().all()

    return [UserResponse.model_validate(user) for user in users]


@app.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_role([RoleEnum.PARTNER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a user account

    Requires: Partner role
    """
    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == current_user.organization_id
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    await db.commit()

    logger.info(f"User deactivated: {user.email} by {current_user.email}")

    return {"message": "User deactivated successfully"}


@app.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(require_role([RoleEnum.PARTNER, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's information

    Requires: Partner or Manager role
    """
    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == current_user.organization_id
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    await db.commit()
    await db.refresh(user)

    logger.info(f"User updated: {user.email} by {current_user.email}")

    return UserResponse.model_validate(user)


# ========================================
# Organization/Firm Management
# ========================================

@app.get("/admin/organizations", response_model=List[OrganizationResponse])
async def list_all_organizations(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all CPA firms (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    query = select(Organization)

    # Apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Organization.firm_name.ilike(search_pattern),
                Organization.legal_name.ilike(search_pattern),
                Organization.primary_contact_email.ilike(search_pattern)
            )
        )

    query = query.offset(skip).limit(limit).order_by(Organization.created_at.desc())

    result = await db.execute(query)
    organizations = result.scalars().all()

    return [OrganizationResponse.model_validate(org) for org in organizations]


@app.post("/admin/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new CPA firm (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    from sqlalchemy import text
    from uuid import uuid4

    # Check if firm with same name or email already exists
    result = await db.execute(
        select(Organization).where(
            or_(
                Organization.firm_name == org_data.firm_name,
                Organization.primary_contact_email == org_data.primary_contact_email
            )
        )
    )
    existing_org = result.scalar_one_or_none()

    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization with this name or email already exists"
        )

    # Use raw SQL to handle PostgreSQL enum types properly
    new_id = uuid4()
    tier = org_data.subscription_tier or "professional"
    status_val = org_data.subscription_status or "active"
    max_users = org_data.max_users or 10

    # For asyncpg, we need to use CAST function instead of :: syntax
    insert_query = text("""
        INSERT INTO atlas.cpa_firms (
            id, firm_name, legal_name, ein, primary_contact_name,
            primary_contact_email, primary_contact_phone,
            subscription_tier, subscription_status, max_users, is_active
        ) VALUES (
            :id, :firm_name, :legal_name, :ein, :primary_contact_name,
            :primary_contact_email, :primary_contact_phone,
            CAST(:subscription_tier AS atlas.firm_subscription_tier),
            CAST(:subscription_status AS atlas.firm_status),
            :max_users, :is_active
        )
        RETURNING id, firm_name, legal_name, ein, primary_contact_name, primary_contact_email,
                  primary_contact_phone, logo_url, primary_color, secondary_color,
                  require_two_factor_auth, session_timeout_minutes,
                  subscription_tier, subscription_status, max_users,
                  is_active, created_at, updated_at
    """)

    result = await db.execute(insert_query, {
        "id": new_id,
        "firm_name": org_data.firm_name,
        "legal_name": org_data.legal_name,
        "ein": org_data.ein,
        "primary_contact_name": org_data.primary_contact_name,
        "primary_contact_email": org_data.primary_contact_email,
        "primary_contact_phone": org_data.primary_contact_phone,
        "subscription_tier": tier,
        "subscription_status": status_val,
        "max_users": max_users,
        "is_active": True
    })
    await db.commit()

    row = result.fetchone()
    logger.info(f"New organization created: {org_data.firm_name} (ID: {new_id})")

    # Return the response
    return OrganizationResponse(
        id=row.id,
        firm_name=row.firm_name,
        legal_name=row.legal_name,
        ein=row.ein,
        primary_contact_name=row.primary_contact_name,
        primary_contact_email=row.primary_contact_email,
        primary_contact_phone=row.primary_contact_phone,
        logo_url=row.logo_url,
        primary_color=row.primary_color,
        secondary_color=row.secondary_color,
        require_two_factor_auth=row.require_two_factor_auth or False,
        session_timeout_minutes=row.session_timeout_minutes,
        subscription_tier=row.subscription_tier,
        subscription_status=row.subscription_status,
        max_users=row.max_users,
        enabled_services=None,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at
    )


@app.delete("/admin/organizations/{org_id}")
async def delete_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a CPA firm (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Check if organization has users
    user_result = await db.execute(
        select(User).where(User.cpa_firm_id == org_id).limit(1)
    )
    has_users = user_result.scalar_one_or_none() is not None

    if has_users:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete organization with existing users. Please remove or reassign users first."
        )

    await db.delete(organization)
    await db.commit()

    logger.info(f"Organization deleted: {organization.firm_name} (ID: {org_id})")

    return {"message": "Organization deleted successfully", "id": str(org_id)}


@app.patch("/admin/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization_admin(
    org_id: UUID,
    org_update: OrganizationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update organization settings (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Update fields if provided
    update_data = org_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    organization.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(organization)

    logger.info(f"Organization updated: {organization.firm_name} by admin")

    return OrganizationResponse.model_validate(organization)


@app.patch("/admin/organizations/{org_id}/services", response_model=OrganizationResponse)
async def update_organization_services(
    org_id: UUID,
    services: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Update enabled services for a CPA firm (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    Note: enabled_services column doesn't exist in DB yet, so this endpoint does nothing
    """
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # TODO: Add enabled_services column to database schema
    # organization.enabled_services = services
    organization.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(organization)

    logger.info(f"Organization services update requested (no-op): {organization.firm_name} (ID: {org_id})")

    return OrganizationResponse.model_validate(organization)


@app.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get organization details

    Users can only access their own organization
    """
    if current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )

    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return OrganizationResponse.model_validate(organization)


@app.get("/organizations/me/details", response_model=OrganizationResponse)
async def get_my_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's organization details"""
    if not current_user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not associated with an organization"
        )

    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return OrganizationResponse.model_validate(organization)


@app.patch("/organizations/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    org_update: OrganizationUpdate,
    current_user: User = Depends(require_role([RoleEnum.PARTNER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Update organization settings

    Requires: Partner role
    """
    if current_user.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )

    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    # Update fields if provided
    update_data = org_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(organization, field, value)

    await db.commit()
    await db.refresh(organization)

    logger.info(f"Organization updated: {organization.firm_name} by {current_user.email}")

    return OrganizationResponse.model_validate(organization)


# ========================================
# Admin User Management
# ========================================

@app.get("/admin/organizations/{org_id}/users")
async def get_organization_users(
    org_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all users for a specific organization (Admin endpoint)
    """
    from sqlalchemy.orm import selectinload

    result = await db.execute(
        select(User)
        .options(selectinload(User.organization))
        .where(User.cpa_firm_id == org_id)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()

    return [
        {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": "firm_user",
            "is_active": user.is_active,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]


@app.get("/admin/users")
async def list_all_users(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    organization_id: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    List all users across all organizations (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    from sqlalchemy.orm import selectinload

    query = select(User).options(selectinload(User.organization))

    # Apply filters
    filters = []
    if search:
        search_pattern = f"%{search}%"
        filters.append(
            or_(
                User.email.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern)
            )
        )
    if organization_id:
        filters.append(User.cpa_firm_id == UUID(organization_id))
    if is_active is not None:
        filters.append(User.is_active == is_active)

    if filters:
        query = query.where(and_(*filters))

    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    # Build response with organization name
    return [
        {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": getattr(user, 'role', None) or "firm_user",
            "organization_id": str(user.cpa_firm_id) if user.cpa_firm_id else None,
            "organization_name": user.organization.firm_name if user.organization else None,
            "is_active": user.is_active,
            "email_verified": user.is_email_verified,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]


@app.get("/admin/users/{user_id}", response_model=UserResponse)
async def get_user_admin(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user details (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.model_validate(user)


@app.post("/admin/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user (note: role is handled separately via user_permissions table, not stored on User)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        organization_id=user_data.organization_id,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"New user created by admin: {new_user.email} (ID: {new_user.id})")

    # Build response manually since the model doesn't have role
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=user_data.role,  # Pass through the requested role
        organization_id=new_user.organization_id,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        last_login_at=new_user.last_login_at
    )


@app.patch("/admin/users/{user_id}", response_model=UserResponse)
async def update_user_admin(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields if provided
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    await db.commit()
    await db.refresh(user)

    logger.info(f"User updated by admin: {user.email}")

    return UserResponse.model_validate(user)


@app.delete("/admin/users/{user_id}")
async def deactivate_user_admin(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Deactivate a user (Admin endpoint - no auth required for now)

    Note: In production, this should require admin/super-admin role
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    await db.commit()

    logger.info(f"User deactivated by admin: {user.email}")

    return {"message": "User deactivated successfully", "id": str(user_id)}


@app.post("/admin/users/{user_id}/reset-password")
async def admin_reset_user_password(
    user_id: UUID,
    password_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset a user's password (Admin endpoint)

    Note: In production, this should require admin/super-admin role
    """
    new_password = password_data.get("new_password")
    if not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="new_password is required"
        )

    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters"
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Hash and update password
    user.password_hash = hash_password(new_password)
    user.last_password_change = datetime.utcnow()
    user.require_password_change = password_data.get("require_change", False)

    await db.commit()

    logger.info(f"Password reset by admin for user: {user.email}")

    return {"message": "Password reset successfully", "user_id": str(user_id)}


# ========================================
# User Invitations
# ========================================

@app.post("/invitations", response_model=UserInvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    invitation_data: UserInvitationCreate,
    current_user: User = Depends(require_role([RoleEnum.PARTNER, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Invite a new user to the organization

    Requires: Partner or Manager role
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == invitation_data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Check if invitation already exists
    result = await db.execute(
        select(UserInvitation).where(
            and_(
                UserInvitation.email == invitation_data.email,
                UserInvitation.organization_id == current_user.organization_id,
                UserInvitation.is_expired == False
            )
        )
    )
    existing_invitation = result.scalar_one_or_none()

    if existing_invitation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Active invitation already exists for this email"
        )

    # Generate invitation token
    import secrets
    token = secrets.token_urlsafe(32)

    # Create invitation (expires in 7 days)
    invitation = UserInvitation(
        email=invitation_data.email,
        organization_id=current_user.organization_id,
        role=invitation_data.role,
        invited_by_user_id=current_user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7),
        is_expired=False
    )

    db.add(invitation)
    await db.commit()
    await db.refresh(invitation)

    logger.info(f"Invitation created for {invitation.email} by {current_user.email}")

    # Send invitation email
    try:
        from .email_service import get_email_service

        # Get organization name
        org_result = await db.execute(
            select(Organization).where(Organization.id == current_user.organization_id)
        )
        organization = org_result.scalar_one()

        email_service = get_email_service()
        email_sent = await email_service.send_invitation_email(
            to_email=invitation.email,
            to_name=invitation.email.split('@')[0],  # Use email prefix as fallback name
            invitation_token=token,
            invited_by=current_user.full_name or current_user.email,
            organization_name=organization.name,
            role=invitation.role.value
        )

        if email_sent:
            logger.info(f"Invitation email sent successfully to {invitation.email}")
        else:
            logger.warning(f"Failed to send invitation email to {invitation.email}")

    except Exception as e:
        # Log error but don't fail the invitation creation
        logger.error(f"Error sending invitation email to {invitation.email}: {e}")

    return UserInvitationResponse.model_validate(invitation)


@app.get("/invitations", response_model=List[UserInvitationResponse])
async def list_invitations(
    current_user: User = Depends(require_role([RoleEnum.PARTNER, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    List all invitations for the organization

    Requires: Partner or Manager role
    """
    result = await db.execute(
        select(UserInvitation)
        .where(UserInvitation.organization_id == current_user.organization_id)
        .order_by(UserInvitation.created_at.desc())
    )
    invitations = result.scalars().all()

    return [UserInvitationResponse.model_validate(inv) for inv in invitations]


@app.get("/invitations/validate", response_model=UserInvitationValidateResponse)
async def validate_invitation(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate an invitation token and return invitation details.

    This endpoint is used by the AcceptInvitation page to display
    invitation details before the user creates their account.

    Returns 404 if token is invalid, 410 if expired.
    """
    result = await db.execute(
        select(UserInvitation).where(UserInvitation.token == token)
    )
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    # Check if already accepted
    if invitation.accepted_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation has already been used"
        )

    # Check if expired
    if invitation.is_expired or invitation.expires_at < datetime.utcnow():
        if not invitation.is_expired:
            invitation.is_expired = True
            await db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Invitation has expired"
        )

    # Get organization name
    org_result = await db.execute(
        select(Organization).where(Organization.id == invitation.organization_id)
    )
    organization = org_result.scalar_one_or_none()
    org_name = organization.firm_name if organization else "Unknown Organization"

    # Get inviter name
    inviter_result = await db.execute(
        select(User).where(User.id == invitation.invited_by_user_id)
    )
    inviter = inviter_result.scalar_one_or_none()
    inviter_name = inviter.full_name if inviter else "A team member"

    return UserInvitationValidateResponse(
        email=invitation.email,
        organization_name=org_name,
        role=invitation.role,
        invited_by=inviter_name,
        expires_at=invitation.expires_at
    )


@app.post("/invitations/{invitation_id}/resend", response_model=UserInvitationResponse)
async def resend_invitation(
    invitation_id: UUID,
    current_user: User = Depends(require_role([RoleEnum.PARTNER, RoleEnum.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Resend an invitation email and extend the expiration date.

    Requires: Partner or Manager role
    """
    result = await db.execute(
        select(UserInvitation).where(
            and_(
                UserInvitation.id == invitation_id,
                UserInvitation.organization_id == current_user.organization_id
            )
        )
    )
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )

    if invitation.accepted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has already been accepted"
        )

    # Extend expiration and reset expired flag
    invitation.expires_at = datetime.utcnow() + timedelta(days=7)
    invitation.is_expired = False

    await db.commit()
    await db.refresh(invitation)

    # Get organization name for email
    org_result = await db.execute(
        select(Organization).where(Organization.id == invitation.organization_id)
    )
    organization = org_result.scalar_one_or_none()
    org_name = organization.firm_name if organization else "Your Organization"

    # Send invitation email
    try:
        from app.email_service import get_email_service
        email_service = get_email_service()
        await email_service.send_invitation_email(
            to_email=invitation.email,
            to_name=invitation.email.split('@')[0],
            invitation_token=invitation.token,
            invited_by=current_user.full_name,
            organization_name=org_name,
            role=invitation.role.value
        )
        logger.info(f"Invitation email resent to {invitation.email}")
    except Exception as e:
        logger.error(f"Error resending invitation email to {invitation.email}: {e}")

    return UserInvitationResponse.model_validate(invitation)


@app.post("/invitations/accept", response_model=TokenResponse)
async def accept_invitation(
    acceptance_data: UserInvitationAccept,
    db: AsyncSession = Depends(get_db)
):
    """Accept invitation and create user account"""
    result = await db.execute(
        select(UserInvitation).where(
            and_(
                UserInvitation.token == acceptance_data.token,
                UserInvitation.is_expired == False
            )
        )
    )
    invitation = result.scalar_one_or_none()

    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired invitation"
        )

    # Check if expired
    if invitation.expires_at < datetime.utcnow():
        invitation.is_expired = True
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )

    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == invitation.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )

    # Create user
    hashed_password = hash_password(acceptance_data.password)
    new_user = User(
        email=invitation.email,
        full_name=acceptance_data.full_name,
        hashed_password=hashed_password,
        organization_id=invitation.organization_id,
        role=invitation.role,
        is_active=True
    )

    db.add(new_user)

    # Mark invitation as accepted
    invitation.accepted_at = datetime.utcnow()
    invitation.is_expired = True

    await db.commit()
    await db.refresh(new_user)

    # Create default permissions based on role
    default_permissions = UserPermission(
        user_id=new_user.id,
        can_upload_documents=True,
        can_create_engagements=(invitation.role in [RoleEnum.PARTNER, RoleEnum.MANAGER]),
        can_edit_engagements=(invitation.role in [RoleEnum.PARTNER, RoleEnum.MANAGER, RoleEnum.SENIOR]),
        can_view_all_engagements=(invitation.role in [RoleEnum.PARTNER, RoleEnum.MANAGER]),
        can_invite_users=(invitation.role in [RoleEnum.PARTNER, RoleEnum.MANAGER]),
        can_manage_users=(invitation.role == RoleEnum.PARTNER),
        can_edit_firm_settings=(invitation.role == RoleEnum.PARTNER)
    )
    db.add(default_permissions)
    await db.commit()

    logger.info(f"User created from invitation: {new_user.email}")

    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(new_user.id),
            "email": new_user.email,
            "role": new_user.role.value,
            "organization_id": str(new_user.organization_id)
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRY_HOURS * 3600
    )


# ========================================
# User Permissions
# ========================================

@app.get("/users/{user_id}/permissions", response_model=UserPermissionResponse)
async def get_user_permissions(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user permissions

    Users can view their own permissions; Admins can view any user's permissions
    """
    # Check authorization
    if current_user.id != user_id and current_user.role not in [RoleEnum.PARTNER, RoleEnum.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    result = await db.execute(
        select(UserPermission).where(UserPermission.user_id == user_id)
    )
    permissions = result.scalar_one_or_none()

    if not permissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permissions not found"
        )

    return UserPermissionResponse.model_validate(permissions)


@app.patch("/users/{user_id}/permissions", response_model=UserPermissionResponse)
async def update_user_permissions(
    user_id: UUID,
    permission_update: UserPermissionUpdate,
    current_user: User = Depends(require_role([RoleEnum.PARTNER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user permissions

    Requires: Partner role
    """
    # Verify user belongs to same organization
    result = await db.execute(
        select(User).where(
            and_(
                User.id == user_id,
                User.organization_id == current_user.organization_id
            )
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get or create permissions
    result = await db.execute(
        select(UserPermission).where(UserPermission.user_id == user_id)
    )
    permissions = result.scalar_one_or_none()

    if not permissions:
        permissions = UserPermission(user_id=user_id)
        db.add(permissions)

    # Update permissions
    update_data = permission_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(permissions, field, value)

    await db.commit()
    await db.refresh(permissions)

    logger.info(f"Permissions updated for user {user.email} by {current_user.email}")

    return UserPermissionResponse.model_validate(permissions)


# ========================================
# Client (Audit Client) Management
# ========================================

@app.get("/clients", response_model=dict)
@app.get("/clients/", response_model=dict, include_in_schema=False)
async def list_clients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List clients for the current user's CPA firm
    """
    if not current_user.cpa_firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a CPA firm"
        )

    result = await db.execute(
        select(Client)
        .where(Client.cpa_firm_id == current_user.cpa_firm_id)
        .where(Client.is_active == True)
        .order_by(Client.client_name)
    )
    clients = result.scalars().all()

    client_list = []
    for client in clients:
        client_list.append({
            "id": str(client.id),
            "organization_id": str(client.cpa_firm_id),
            "name": client.client_name,
            "ein": client.ein,
            "industry": client.industry_code,
            "address": client.address_line1,
            "phone": client.primary_contact_phone,
            "email": client.primary_contact_email,
            "primary_contact_name": client.primary_contact_name,
            "primary_contact_email": client.primary_contact_email,
            "primary_contact_phone": client.primary_contact_phone,
            "status": client.client_status or "active",
            "fiscal_year_end": client.fiscal_year_end,
            "notes": None,
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "updated_at": client.updated_at.isoformat() if client.updated_at else None
        })

    return {"clients": client_list}


@app.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
@app.post("/clients/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new audit client
    """
    from sqlalchemy import text
    from uuid import uuid4 as gen_uuid

    if not current_user.cpa_firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a CPA firm"
        )

    # Check if client with same name exists in this firm
    result = await db.execute(
        select(Client).where(
            and_(
                Client.cpa_firm_id == current_user.cpa_firm_id,
                Client.client_name == client_data.name
            )
        )
    )
    existing_client = result.scalar_one_or_none()

    if existing_client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client with this name already exists"
        )

    # Use raw SQL to handle PostgreSQL enum types
    new_id = gen_uuid()
    status_val = client_data.status if client_data.status else "active"

    insert_query = text("""
        INSERT INTO atlas.clients (
            id, cpa_firm_id, client_name, ein,
            primary_contact_name, primary_contact_email, primary_contact_phone,
            address_line1, fiscal_year_end, industry_code,
            client_status, is_active, created_by
        ) VALUES (
            :id, :cpa_firm_id, :client_name, :ein,
            :primary_contact_name, :primary_contact_email, :primary_contact_phone,
            :address_line1, :fiscal_year_end, :industry_code,
            CAST(:client_status AS atlas.client_status), :is_active, :created_by
        )
        RETURNING id, cpa_firm_id, client_name, ein,
                  primary_contact_name, primary_contact_email, primary_contact_phone,
                  address_line1, fiscal_year_end, industry_code,
                  client_status, is_active, created_at, updated_at
    """)

    result = await db.execute(insert_query, {
        "id": new_id,
        "cpa_firm_id": current_user.cpa_firm_id,
        "client_name": client_data.name,
        "ein": client_data.ein,
        "primary_contact_name": client_data.primary_contact_name,
        "primary_contact_email": client_data.primary_contact_email or client_data.email,
        "primary_contact_phone": client_data.primary_contact_phone or client_data.phone,
        "address_line1": client_data.address,
        "fiscal_year_end": client_data.fiscal_year_end,
        "industry_code": client_data.industry,
        "client_status": status_val,
        "is_active": True,
        "created_by": current_user.id
    })
    await db.commit()

    row = result.fetchone()
    logger.info(f"New client created: {client_data.name} by {current_user.email}")

    return ClientResponse(
        id=row.id,
        organization_id=row.cpa_firm_id,
        name=row.client_name,
        ein=row.ein,
        industry=row.industry_code,
        address=row.address_line1,
        phone=row.primary_contact_phone,
        email=row.primary_contact_email,
        primary_contact_name=row.primary_contact_name,
        primary_contact_email=row.primary_contact_email,
        primary_contact_phone=row.primary_contact_phone,
        status=str(row.client_status) if row.client_status else "active",
        fiscal_year_end=row.fiscal_year_end,
        notes=None,
        created_at=row.created_at,
        updated_at=row.updated_at
    )


@app.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get client by ID
    """
    result = await db.execute(
        select(Client).where(
            and_(
                Client.id == client_id,
                Client.cpa_firm_id == current_user.cpa_firm_id
            )
        )
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    return ClientResponse(
        id=client.id,
        organization_id=client.cpa_firm_id,
        name=client.client_name,
        ein=client.ein,
        industry=client.industry_code,
        address=client.address_line1,
        phone=client.primary_contact_phone,
        email=client.primary_contact_email,
        primary_contact_name=client.primary_contact_name,
        primary_contact_email=client.primary_contact_email,
        primary_contact_phone=client.primary_contact_phone,
        status=client.client_status or "active",
        fiscal_year_end=client.fiscal_year_end,
        notes=None,
        created_at=client.created_at,
        updated_at=client.updated_at
    )


@app.patch("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: UUID,
    client_update: ClientUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update client information
    """
    result = await db.execute(
        select(Client).where(
            and_(
                Client.id == client_id,
                Client.cpa_firm_id == current_user.cpa_firm_id
            )
        )
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Update fields if provided
    if client_update.name is not None:
        client.client_name = client_update.name
    if client_update.ein is not None:
        client.ein = client_update.ein
    if client_update.industry is not None:
        client.industry_code = client_update.industry
    if client_update.address is not None:
        client.address_line1 = client_update.address
    if client_update.primary_contact_name is not None:
        client.primary_contact_name = client_update.primary_contact_name
    if client_update.primary_contact_email is not None:
        client.primary_contact_email = client_update.primary_contact_email
    if client_update.primary_contact_phone is not None:
        client.primary_contact_phone = client_update.primary_contact_phone
    if client_update.email is not None:
        client.primary_contact_email = client_update.email
    if client_update.phone is not None:
        client.primary_contact_phone = client_update.phone
    if client_update.status is not None:
        client.client_status = client_update.status
    if client_update.fiscal_year_end is not None:
        client.fiscal_year_end = client_update.fiscal_year_end

    await db.commit()
    await db.refresh(client)

    logger.info(f"Client updated: {client.client_name} by {current_user.email}")

    return ClientResponse(
        id=client.id,
        organization_id=client.cpa_firm_id,
        name=client.client_name,
        ein=client.ein,
        industry=client.industry_code,
        address=client.address_line1,
        phone=client.primary_contact_phone,
        email=client.primary_contact_email,
        primary_contact_name=client.primary_contact_name,
        primary_contact_email=client.primary_contact_email,
        primary_contact_phone=client.primary_contact_phone,
        status=client.client_status or "active",
        fiscal_year_end=client.fiscal_year_end,
        notes=None,
        created_at=client.created_at,
        updated_at=client.updated_at
    )


@app.delete("/clients/{client_id}")
async def delete_client(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete (soft-delete) a client
    """
    result = await db.execute(
        select(Client).where(
            and_(
                Client.id == client_id,
                Client.cpa_firm_id == current_user.cpa_firm_id
            )
        )
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # Soft delete
    client.is_active = False
    await db.commit()

    logger.info(f"Client deleted: {client.client_name} by {current_user.email}")

    return {"message": "Client deleted successfully", "id": str(client_id)}


@app.get("/clients/{client_id}/engagements")
async def get_client_engagements(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get engagements for a client
    """
    # Verify client belongs to user's firm
    result = await db.execute(
        select(Client).where(
            and_(
                Client.id == client_id,
                Client.cpa_firm_id == current_user.cpa_firm_id
            )
        )
    )
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )

    # TODO: Query engagements from engagement service
    # For now, return empty list
    return {"engagements": []}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# ========================================
# Azure AD Authentication
# ========================================

@app.get("/auth/azure/login")
async def azure_ad_login():
    """Initiate Azure AD login flow"""
    if not settings.AZURE_AD_ENABLED:
        raise HTTPException(status_code=404, detail="Azure AD authentication not enabled")
    
    # Build authorization URL
    auth_url = (
        f"{settings.AZURE_AD_AUTHORITY}/oauth2/v2.0/authorize?"
        f"client_id={settings.AZURE_AD_CLIENT_ID}&"
        f"response_type=code&"
        f"redirect_uri={settings.AZURE_AD_REDIRECT_URI}&"
        f"response_mode=query&"
        f"scope={'+'.join(settings.AZURE_AD_SCOPES)}&"
        f"state=admin_portal"
    )
    
    return {"authorization_url": auth_url}


@app.get("/auth/azure/callback")
async def azure_ad_callback(
    code: str,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Handle Azure AD callback and create/login user"""
    if not settings.AZURE_AD_ENABLED:
        raise HTTPException(status_code=404, detail="Azure AD authentication not enabled")
    
    try:
        import msal
        
        # Create MSAL confidential client
        app = msal.ConfidentialClientApplication(
            settings.AZURE_AD_CLIENT_ID,
            authority=settings.AZURE_AD_AUTHORITY,
            client_credential=settings.AZURE_AD_CLIENT_SECRET,
        )
        
        # Acquire token by authorization code
        result = app.acquire_token_by_authorization_code(
            code,
            scopes=settings.AZURE_AD_SCOPES,
            redirect_uri=settings.AZURE_AD_REDIRECT_URI
        )
        
        if "error" in result:
            logger.error(f"Azure AD error: {result.get('error_description')}")
            raise HTTPException(
                status_code=400,
                detail=f"Azure AD authentication failed: {result.get('error_description')}"
            )
        
        # Extract user info from ID token
        id_token_claims = result.get("id_token_claims", {})
        email = id_token_claims.get("preferred_username") or id_token_claims.get("email")
        name = id_token_claims.get("name", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="No email found in Azure AD response")
        
        # Check if user exists
        user_result = await db.execute(
            select(User).where(User.email == email)
        )
        user = user_result.scalar_one_or_none()
        
        # Create user if doesn't exist
        if not user:
            name_parts = name.split(" ", 1)
            first_name = name_parts[0] if name_parts else email.split("@")[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ""
            
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
                is_email_verified=True,  # Azure AD verified
                password_hash=None  # No password for Azure AD users
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new Azure AD user: {email}")
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "cpa_firm_id": str(user.cpa_firm_id) if user.cpa_firm_id else None,
                "auth_method": "azure_ad"
            }
        )
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        logger.info(f"Azure AD user logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRY_HOURS * 3600,
            user=UserResponse.model_validate(user)
        )
        
    except Exception as e:
        logger.error(f"Azure AD callback error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.post("/auth/azure/logout")
async def azure_ad_logout():
    """Azure AD logout"""
    logout_url = (
        f"{settings.AZURE_AD_AUTHORITY}/oauth2/v2.0/logout?"
        f"post_logout_redirect_uri=https://admin.auraai.toroniandcompany.com"
    )

    return {"logout_url": logout_url}


# ========================================
# R&D Study Client Invitations
# ========================================

@app.post("/rd-study/client-invitations", response_model=RDStudyClientInvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_rd_study_client_invitation(
    invitation_data: RDStudyClientInvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Invite a client to provide data for an R&D Tax Credit Study.

    The client will receive an email with a secure link to access
    the data collection portal. Clients can only upload data and
    describe projects - they cannot see calculations or final reports.

    Requires: Authenticated CPA firm user
    """
    import secrets
    from sqlalchemy import text
    from uuid import uuid4

    if not current_user.cpa_firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a CPA firm"
        )

    # Get firm details
    org_result = await db.execute(
        select(Organization).where(Organization.id == current_user.cpa_firm_id)
    )
    organization = org_result.scalar_one_or_none()

    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CPA firm not found"
        )

    # Generate secure token
    token = secrets.token_urlsafe(48)

    # Create invitation record using raw SQL
    new_id = uuid4()
    expires_at = datetime.utcnow() + timedelta(days=30)  # 30 days for R&D invitations

    insert_query = text("""
        INSERT INTO atlas.rd_study_client_invitations (
            id, client_email, client_name, study_id, study_name, tax_year,
            firm_id, invited_by_user_id, token, deadline, status, expires_at
        ) VALUES (
            :id, :client_email, :client_name, :study_id, :study_name, :tax_year,
            :firm_id, :invited_by_user_id, :token, :deadline, 'pending', :expires_at
        )
        ON CONFLICT (client_email, study_id) DO UPDATE SET
            token = :token,
            expires_at = :expires_at,
            status = 'pending',
            updated_at = NOW()
        RETURNING id, client_email, client_name, study_id, study_name, tax_year,
                  firm_id, invited_by_user_id, token, deadline, status, expires_at, created_at
    """)

    try:
        result = await db.execute(insert_query, {
            "id": new_id,
            "client_email": invitation_data.client_email,
            "client_name": invitation_data.client_name,
            "study_id": invitation_data.study_id,
            "study_name": invitation_data.study_name,
            "tax_year": invitation_data.tax_year,
            "firm_id": current_user.cpa_firm_id,
            "invited_by_user_id": current_user.id,
            "token": token,
            "deadline": invitation_data.deadline,
            "expires_at": expires_at
        })
        await db.commit()
        row = result.fetchone()
    except Exception as e:
        # Table might not exist yet, create it
        logger.warning(f"R&D invitation table may not exist: {e}")
        await db.rollback()

        # Create table if needed
        create_table = text("""
            CREATE TABLE IF NOT EXISTS atlas.rd_study_client_invitations (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_email VARCHAR(255) NOT NULL,
                client_name VARCHAR(255) NOT NULL,
                study_id UUID NOT NULL,
                study_name VARCHAR(255) NOT NULL,
                tax_year INTEGER NOT NULL,
                firm_id UUID NOT NULL REFERENCES atlas.cpa_firms(id),
                invited_by_user_id UUID NOT NULL REFERENCES atlas.users(id),
                token VARCHAR(255) NOT NULL UNIQUE,
                deadline VARCHAR(50),
                status VARCHAR(20) DEFAULT 'pending',
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                accepted_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(client_email, study_id)
            )
        """)
        await db.execute(create_table)
        await db.commit()

        # Try insert again
        result = await db.execute(insert_query, {
            "id": new_id,
            "client_email": invitation_data.client_email,
            "client_name": invitation_data.client_name,
            "study_id": invitation_data.study_id,
            "study_name": invitation_data.study_name,
            "tax_year": invitation_data.tax_year,
            "firm_id": current_user.cpa_firm_id,
            "invited_by_user_id": current_user.id,
            "token": token,
            "deadline": invitation_data.deadline,
            "expires_at": expires_at
        })
        await db.commit()
        row = result.fetchone()

    logger.info(f"R&D study client invitation created for {invitation_data.client_email} by {current_user.email}")

    # Send invitation email
    try:
        from app.email_service import get_email_service
        email_service = get_email_service()
        email_sent = await email_service.send_rd_study_invitation_email(
            to_email=invitation_data.client_email,
            to_name=invitation_data.client_name,
            invitation_token=token,
            firm_name=organization.firm_name,
            study_name=invitation_data.study_name,
            tax_year=invitation_data.tax_year,
            invited_by=current_user.full_name or current_user.email,
            deadline=invitation_data.deadline
        )

        if email_sent:
            logger.info(f"R&D study invitation email sent successfully to {invitation_data.client_email}")
        else:
            logger.warning(f"Failed to send R&D study invitation email to {invitation_data.client_email}")

    except Exception as e:
        logger.error(f"Error sending R&D study invitation email: {e}")

    return RDStudyClientInvitationResponse(
        id=row.id,
        client_email=row.client_email,
        client_name=row.client_name,
        study_id=row.study_id,
        study_name=row.study_name,
        tax_year=row.tax_year,
        firm_id=row.firm_id,
        firm_name=organization.firm_name,
        invited_by_user_id=row.invited_by_user_id,
        invited_by_name=current_user.full_name or current_user.email,
        token=row.token,
        deadline=row.deadline,
        status=row.status,
        expires_at=row.expires_at,
        accepted_at=None,
        created_at=row.created_at
    )


@app.get("/rd-study/client-invitations/validate", response_model=RDStudyClientInvitationValidate)
async def validate_rd_study_client_invitation(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate an R&D study client invitation token.

    This endpoint is called when a client clicks the invitation link
    to verify the token is valid before showing the data collection form.
    """
    from sqlalchemy import text

    query = text("""
        SELECT i.*, f.firm_name, u.full_name as inviter_name
        FROM atlas.rd_study_client_invitations i
        JOIN atlas.cpa_firms f ON i.firm_id = f.id
        JOIN atlas.users u ON i.invited_by_user_id = u.id
        WHERE i.token = :token
    """)

    try:
        result = await db.execute(query, {"token": token})
        row = result.fetchone()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation token"
        )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invitation token"
        )

    # Check if already accepted
    if row.accepted_at:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has already been used"
        )

    # Check if expired
    if row.expires_at < datetime.utcnow() or row.status == 'expired':
        # Update status to expired
        update_query = text("""
            UPDATE atlas.rd_study_client_invitations
            SET status = 'expired', updated_at = NOW()
            WHERE token = :token
        """)
        await db.execute(update_query, {"token": token})
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This invitation has expired"
        )

    return RDStudyClientInvitationValidate(
        client_email=row.client_email,
        client_name=row.client_name,
        study_name=row.study_name,
        tax_year=row.tax_year,
        firm_name=row.firm_name,
        invited_by=row.inviter_name or "Your CPA",
        deadline=row.deadline,
        expires_at=row.expires_at
    )


@app.get("/rd-study/client-invitations", response_model=List[RDStudyClientInvitationResponse])
async def list_rd_study_client_invitations(
    study_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List R&D study client invitations for the CPA firm.

    Optionally filter by study_id.
    """
    from sqlalchemy import text

    if not current_user.cpa_firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a CPA firm"
        )

    if study_id:
        query = text("""
            SELECT i.*, f.firm_name, u.full_name as inviter_name
            FROM atlas.rd_study_client_invitations i
            JOIN atlas.cpa_firms f ON i.firm_id = f.id
            JOIN atlas.users u ON i.invited_by_user_id = u.id
            WHERE i.firm_id = :firm_id AND i.study_id = :study_id
            ORDER BY i.created_at DESC
        """)
        params = {"firm_id": current_user.cpa_firm_id, "study_id": study_id}
    else:
        query = text("""
            SELECT i.*, f.firm_name, u.full_name as inviter_name
            FROM atlas.rd_study_client_invitations i
            JOIN atlas.cpa_firms f ON i.firm_id = f.id
            JOIN atlas.users u ON i.invited_by_user_id = u.id
            WHERE i.firm_id = :firm_id
            ORDER BY i.created_at DESC
        """)
        params = {"firm_id": current_user.cpa_firm_id}

    try:
        result = await db.execute(query, params)
        rows = result.fetchall()
    except Exception:
        return []

    return [
        RDStudyClientInvitationResponse(
            id=row.id,
            client_email=row.client_email,
            client_name=row.client_name,
            study_id=row.study_id,
            study_name=row.study_name,
            tax_year=row.tax_year,
            firm_id=row.firm_id,
            firm_name=row.firm_name,
            invited_by_user_id=row.invited_by_user_id,
            invited_by_name=row.inviter_name or "",
            token=row.token,
            deadline=row.deadline,
            status=row.status,
            expires_at=row.expires_at,
            accepted_at=row.accepted_at,
            created_at=row.created_at
        )
        for row in rows
    ]


@app.post("/rd-study/client-invitations/{invitation_id}/resend")
async def resend_rd_study_client_invitation(
    invitation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resend an R&D study client invitation email.
    """
    from sqlalchemy import text
    import secrets

    if not current_user.cpa_firm_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with a CPA firm"
        )

    # Get invitation
    query = text("""
        SELECT i.*, f.firm_name
        FROM atlas.rd_study_client_invitations i
        JOIN atlas.cpa_firms f ON i.firm_id = f.id
        WHERE i.id = :id AND i.firm_id = :firm_id
    """)

    try:
        result = await db.execute(query, {"id": invitation_id, "firm_id": current_user.cpa_firm_id})
        row = result.fetchone()
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found")

    if row.accepted_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation already accepted")

    # Generate new token and extend expiration
    new_token = secrets.token_urlsafe(48)
    new_expires = datetime.utcnow() + timedelta(days=30)

    update_query = text("""
        UPDATE atlas.rd_study_client_invitations
        SET token = :token, expires_at = :expires_at, status = 'pending', updated_at = NOW()
        WHERE id = :id
    """)
    await db.execute(update_query, {"id": invitation_id, "token": new_token, "expires_at": new_expires})
    await db.commit()

    # Send email
    try:
        from app.email_service import get_email_service
        email_service = get_email_service()
        await email_service.send_rd_study_invitation_email(
            to_email=row.client_email,
            to_name=row.client_name,
            invitation_token=new_token,
            firm_name=row.firm_name,
            study_name=row.study_name,
            tax_year=row.tax_year,
            invited_by=current_user.full_name or current_user.email,
            deadline=row.deadline
        )
        logger.info(f"R&D study invitation resent to {row.client_email}")
    except Exception as e:
        logger.error(f"Error resending invitation: {e}")

    return {"message": "Invitation resent successfully", "new_expires_at": new_expires.isoformat()}
