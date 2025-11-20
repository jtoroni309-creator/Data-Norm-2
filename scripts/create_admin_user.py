"""
Script to create admin user for Aura Audit AI platform

This script creates an admin user with full access to the system.
Run this script once to set up the initial admin account.

Usage:
    python scripts/create_admin_user.py
"""

import asyncio
import sys
from pathlib import Path

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

# Database URL - update this to match your actual database
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/aura_audit_ai"


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


async def create_admin_user():
    """Create admin user in the database"""

    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)

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
            admin_email = "admin@auraai.com"
            admin_password = "AdminAura2024!"  # Strong default password
            admin_full_name = "System Administrator"

            # Hash password
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

            session.add(admin_user)
            await session.commit()

            print("\n" + "="*60)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("="*60)
            print(f"\n📧 Email:    {admin_email}")
            print(f"🔑 Password: {admin_password}")
            print(f"👤 Name:     {admin_full_name}")
            print(f"🏢 Org:      {org.name}")
            print(f"🆔 User ID:  {admin_user.id}")
            print(f"🔐 Role:     {admin_user.role.value}")
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
    print("\n🚀 Creating admin user for Aura Audit AI...\n")
    asyncio.run(create_admin_user())
