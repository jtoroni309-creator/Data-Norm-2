#!/usr/bin/env python3
"""
Create a test user in the Aura Audit AI database
This is a temporary workaround while the identity service is being fixed
"""
import asyncio
import sys
from uuid import uuid4
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection string
DATABASE_URL = "postgresql://atlasadmin:j:%[uxtnyLFnDK9Cd5{)B0P86vv%HN5l@aura-audit-ai-prod-psql.postgres.database.azure.com:5432/atlas?sslmode=require"

# Password hashing context (bcrypt with 12 rounds, matching identity service)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def create_test_user():
    """Create a test user and organization"""
    # Create synchronous engine for admin tasks
    engine = create_engine(DATABASE_URL.replace("asyncpg", "psycopg2"))
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # First, check if organization exists, if not create one
        org_id = str(uuid4())
        org_name = "Test Firm"

        result = session.execute(
            text("SELECT id FROM atlas.organizations WHERE name = :name"),
            {"name": org_name}
        )
        existing_org = result.fetchone()

        if existing_org:
            org_id = str(existing_org[0])
            print(f"✓ Using existing organization: {org_name} ({org_id})")
        else:
            session.execute(
                text("""
                    INSERT INTO atlas.organizations (
                        id, name, organization_type, created_at, updated_at
                    ) VALUES (
                        :id, :name, 'CPA_FIRM', NOW(), NOW()
                    )
                """),
                {
                    "id": org_id,
                    "name": org_name
                }
            )
            session.commit()
            print(f"✓ Created organization: {org_name} ({org_id})")

        # Create test users with different roles
        test_users = [
            {
                "email": "admin@testfirm.com",
                "full_name": "Admin User",
                "password": "Admin123!",
                "role": "PARTNER"
            },
            {
                "email": "manager@testfirm.com",
                "full_name": "Manager User",
                "password": "Manager123!",
                "role": "MANAGER"
            },
            {
                "email": "staff@testfirm.com",
                "full_name": "Staff User",
                "password": "Staff123!",
                "role": "STAFF"
            }
        ]

        created_users = []

        for user_data in test_users:
            # Check if user already exists
            result = session.execute(
                text("SELECT id, email FROM atlas.users WHERE email = :email"),
                {"email": user_data["email"]}
            )
            existing_user = result.fetchone()

            if existing_user:
                print(f"⚠ User already exists: {user_data['email']}")
                continue

            # Create new user
            user_id = str(uuid4())
            hashed_pw = hash_password(user_data["password"])

            session.execute(
                text("""
                    INSERT INTO atlas.users (
                        id, email, full_name, hashed_password, organization_id,
                        role, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :email, :full_name, :hashed_password, :organization_id,
                        :role, true, NOW(), NOW()
                    )
                """),
                {
                    "id": user_id,
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "hashed_password": hashed_pw,
                    "organization_id": org_id,
                    "role": user_data["role"]
                }
            )
            session.commit()

            created_users.append(user_data)
            print(f"✓ Created user: {user_data['email']} ({user_data['role']})")

        print("\n" + "="*60)
        print("Test users created successfully!")
        print("="*60)

        if created_users:
            print("\nYou can now log in with these credentials:\n")
            for user in created_users:
                print(f"Email:    {user['email']}")
                print(f"Password: {user['password']}")
                print(f"Role:     {user['role']}")
                print()
        else:
            print("\nAll test users already exist. You can log in with:")
            for user in test_users:
                print(f"Email:    {user['email']}")
                print(f"Password: {user['password']}")
                print()

        print("Access the portal at:")
        print("  - https://portal.auraai.toroniandcompany.com/login")
        print("  - https://cpa.auraai.toroniandcompany.com/login")
        print("\n" + "="*60)

    except Exception as e:
        session.rollback()
        print(f"✗ Error creating test users: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    create_test_user()
