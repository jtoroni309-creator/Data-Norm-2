"""
Script to create admin user for Aura Audit AI platform

This script creates an admin user with full access to the system.
Supports both local authentication and Azure Active Directory (AAD) integration.

Usage:
    # Local authentication
    python scripts/create_admin_user.py

    # Azure AAD authentication
    python scripts/create_admin_user.py --azure-ad --aad-tenant-id <tenant-id>

Environment Variables:
    DATABASE_URL - PostgreSQL connection string
    AZURE_TENANT_ID - Azure AD tenant ID
    AZURE_CLIENT_ID - Azure AD application client ID (optional)
    AZURE_CLIENT_SECRET - Azure AD application client secret (optional)
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

# Add services to path
sys.path.append(str(Path(__file__).parent.parent / "services" / "identity"))

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import uuid

# Import from identity service
from app.models import User, Organization, Base
from app.schemas import RoleEnum

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database URL - from environment or default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/aura_audit_ai"
)

# Azure AD configuration
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def get_azure_ad_user_info(email: str, tenant_id: str) -> Optional[dict]:
    """
    Get user information from Azure Active Directory

    Args:
        email: User email address
        tenant_id: Azure AD tenant ID

    Returns:
        dict with user info or None if not found
    """
    try:
        from azure.identity import DefaultAzureCredential, ClientSecretCredential
        from azure.core.credentials import AccessToken
        import requests

        # Authenticate to Azure AD
        if AZURE_CLIENT_ID and AZURE_CLIENT_SECRET:
            # Service principal authentication
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=AZURE_CLIENT_ID,
                client_secret=AZURE_CLIENT_SECRET
            )
        else:
            # Default credential (managed identity, Azure CLI, etc.)
            credential = DefaultAzureCredential()

        # Get access token for Microsoft Graph
        token = credential.get_token("https://graph.microsoft.com/.default")

        # Query Microsoft Graph API for user
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-Type": "application/json"
        }

        # Search for user by email
        url = f"https://graph.microsoft.com/v1.0/users/{email}"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            user_data = response.json()
            return {
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "full_name": user_data.get("displayName"),
                "aad_object_id": user_data.get("id"),
                "department": user_data.get("department"),
                "job_title": user_data.get("jobTitle")
            }
        else:
            print(f"⚠️  User not found in Azure AD: {email}")
            print(f"    Status: {response.status_code}")
            return None

    except ImportError:
        print("❌ Azure SDK not installed. Install with: pip install azure-identity requests")
        return None
    except Exception as e:
        print(f"❌ Error querying Azure AD: {e}")
        return None


async def create_admin_user(
    use_azure_ad: bool = False,
    tenant_id: Optional[str] = None,
    admin_email: Optional[str] = None,
    admin_password: Optional[str] = None,
    admin_name: Optional[str] = None
):
    """
    Create admin user in the database

    Args:
        use_azure_ad: Whether to use Azure AD for authentication
        tenant_id: Azure AD tenant ID (required if use_azure_ad=True)
        admin_email: Admin email (optional, defaults to admin@auraai.com)
        admin_password: Admin password (optional, auto-generated if not provided)
        admin_name: Admin full name (optional)
    """

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=False)

    # Create async session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Check if admin already exists
            result = await session.execute(
                select(User).where(User.email == "admin@auraai.com")
            )
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print("❌ Admin user already exists!")
                print(f"   Email: admin@auraai.com")
                print(f"   User ID: {existing_admin.id}")
                return

            # Create organization if needed
            result = await session.execute(
                select(Organization).where(Organization.name == "Toroni & Company")
            )
            org = result.scalar_one_or_none()

            if not org:
                org = Organization(
                    id=uuid.uuid4(),
                    name="Toroni & Company",
                    is_active=True
                )
                session.add(org)
                await session.flush()
                print(f"✅ Created organization: {org.name}")

            # Admin credentials
            if not admin_email:
                admin_email = "admin@auraai.com"
            if not admin_password:
                admin_password = "AdminAura2024!"  # Strong default password
            if not admin_name:
                admin_full_name = "System Administrator"
            else:
                admin_full_name = admin_name

            # Azure AD integration
            aad_object_id = None
            auth_provider = "local"

            if use_azure_ad and tenant_id:
                print(f"\n🔍 Querying Azure Active Directory for {admin_email}...")
                aad_info = get_azure_ad_user_info(admin_email, tenant_id)

                if aad_info:
                    aad_object_id = aad_info["aad_object_id"]
                    admin_full_name = aad_info["full_name"] or admin_full_name
                    auth_provider = "azure_ad"
                    print(f"✅ Found in Azure AD: {aad_info['full_name']}")
                    if aad_info.get("job_title"):
                        print(f"   Title: {aad_info['job_title']}")
                    if aad_info.get("department"):
                        print(f"   Department: {aad_info['department']}")
                else:
                    print(f"⚠️  Proceeding with local authentication")
                    use_azure_ad = False

            # Hash password (not used for Azure AD, but required for schema)
            hashed_password = hash_password(admin_password)

            # Create admin user
            admin_user = User(
                id=uuid.uuid4(),
                email=admin_email,
                full_name=admin_full_name,
                hashed_password=hashed_password,
                organization_id=org.id,
                role=RoleEnum.PARTNER,  # Highest role
                is_active=True
            )

            # Add Azure AD attributes if available
            if hasattr(admin_user, 'aad_object_id') and aad_object_id:
                admin_user.aad_object_id = aad_object_id
            if hasattr(admin_user, 'auth_provider') and auth_provider:
                admin_user.auth_provider = auth_provider

            session.add(admin_user)
            await session.commit()

            print("\n" + "="*60)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("="*60)
            print(f"\n📧 Email:          {admin_email}")
            if not use_azure_ad:
                print(f"🔑 Password:       {admin_password}")
            print(f"👤 Name:           {admin_full_name}")
            print(f"🏢 Organization:   {org.name}")
            print(f"🆔 User ID:        {admin_user.id}")
            print(f"🔐 Role:           {admin_user.role.value}")
            print(f"🔒 Auth Provider:  {auth_provider}")
            if aad_object_id:
                print(f"☁️  Azure AD ID:    {aad_object_id}")

            if use_azure_ad:
                print("\n✅ Azure AD authentication enabled")
                print("   User will authenticate via Microsoft Identity Platform")
            else:
                print("\n⚠️  IMPORTANT: Change this password after first login!")
            print("="*60 + "\n")

            # Also create CPA firm admin
            result = await session.execute(
                select(User).where(User.email == "cpa.admin@auraai.com")
            )
            existing_cpa = result.scalar_one_or_none()

            if not existing_cpa:
                cpa_password = "CpaAdmin2024!"
                cpa_user = User(
                    id=uuid.uuid4(),
                    email="cpa.admin@auraai.com",
                    full_name="CPA Portal Administrator",
                    hashed_password=hash_password(cpa_password),
                    organization_id=org.id,
                    role=RoleEnum.PARTNER,
                    is_active=True
                )
                session.add(cpa_user)
                await session.commit()

                print("✅ CPA PORTAL ADMIN CREATED!")
                print("="*60)
                print(f"\n📧 Email:    cpa.admin@auraai.com")
                print(f"🔑 Password: {cpa_password}")
                print(f"👤 Name:     CPA Portal Administrator")
                print(f"🆔 User ID:  {cpa_user.id}")
                print("\n⚠️  IMPORTANT: Change this password after first login!")
                print("="*60 + "\n")

        except Exception as e:
            print(f"\n❌ Error creating admin user: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create admin user for Aura Audit AI platform"
    )
    parser.add_argument(
        "--azure-ad",
        action="store_true",
        help="Use Azure Active Directory for authentication"
    )
    parser.add_argument(
        "--aad-tenant-id",
        type=str,
        help="Azure AD tenant ID (can also use AZURE_TENANT_ID env var)"
    )
    parser.add_argument(
        "--email",
        type=str,
        help="Admin user email address (default: admin@auraai.com)"
    )
    parser.add_argument(
        "--password",
        type=str,
        help="Admin user password (default: auto-generated)"
    )
    parser.add_argument(
        "--name",
        type=str,
        help="Admin user full name (default: System Administrator)"
    )

    args = parser.parse_args()

    # Determine Azure AD settings
    use_azure_ad = args.azure_ad
    tenant_id = args.aad_tenant_id or AZURE_TENANT_ID

    if use_azure_ad and not tenant_id:
        print("❌ Error: --aad-tenant-id required when using --azure-ad")
        print("   Or set AZURE_TENANT_ID environment variable")
        sys.exit(1)

    print("\n🚀 Creating admin user for Aura Audit AI...\n")

    if use_azure_ad:
        print(f"🔐 Authentication: Azure Active Directory")
        print(f"☁️  Tenant ID: {tenant_id}")
    else:
        print(f"🔐 Authentication: Local (database)")

    print()

    asyncio.run(create_admin_user(
        use_azure_ad=use_azure_ad,
        tenant_id=tenant_id,
        admin_email=args.email,
        admin_password=args.password,
        admin_name=args.name
    ))
