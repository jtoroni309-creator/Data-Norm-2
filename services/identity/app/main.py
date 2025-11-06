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
from sqlalchemy import select, and_
from passlib.context import CryptContext
from jose import JWTError, jwt

from .config import settings
from .database import get_db, init_db
from .models import User, Organization, LoginAuditLog, UserInvitation, UserPermission
from .schemas import (
    UserCreate,
    UserResponse,
    TokenResponse,
    LoginRequest,
    HealthResponse,
    RoleEnum,
    OrganizationResponse,
    OrganizationUpdate,
    UserInvitationCreate,
    UserInvitationResponse,
    UserInvitationAccept,
    UserPermissionUpdate,
    UserPermissionResponse,
    UserUpdate
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
    version="1.0.0"
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

    # Create user
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        organization_id=user_data.organization_id,
        role=user_data.role,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")

    return UserResponse.model_validate(new_user)


@app.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return JWT token

    - Validates credentials
    - Logs login attempt
    - Returns access token
    """
    # Fetch user by email
    result = await db.execute(
        select(User).where(User.email == form_data.username)
    )
    user = result.scalar_one_or_none()

    # Validate credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
        await log_login_attempt(
            db=db,
            email=form_data.username,
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
            email=form_data.username,
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
            "role": user.role.value,
            "organization_id": str(user.organization_id) if user.organization_id else None
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
        expires_in=settings.JWT_EXPIRY_HOURS * 3600
    )


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse.model_validate(current_user)


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

    logger.info(f"Organization updated: {organization.name} by {current_user.email}")

    return OrganizationResponse.model_validate(organization)


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
