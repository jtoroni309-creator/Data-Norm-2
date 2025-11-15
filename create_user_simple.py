#!/usr/bin/env python3
"""
Create test users - works with existing atlas.users table schema
"""
import os
import sys
from uuid import uuid4
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set", file=sys.stderr)
    sys.exit(1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    """Create test users"""
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check actual column structure
        print("Checking users table structure...")
        result = session.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'atlas' AND table_name = 'users'
            ORDER BY ordinal_position
        """))
        columns = [row[0] for row in result.fetchall()]
        print(f"Existing columns: {', '.join(columns)}")

        # Add hashed_password column if it doesn't exist
        if 'hashed_password' not in columns:
            print("Adding hashed_password column...")
            session.execute(text("ALTER TABLE atlas.users ADD COLUMN hashed_password TEXT"))
            session.commit()
            print("✓ Added hashed_password column")
        else:
            print("✓ hashed_password column exists")

        # Check if organization exists, create if not
        print("Checking for test organization...")
        result = session.execute(
            text("SELECT id FROM atlas.organizations WHERE name = :name"),
            {"name": "Test CPA Firm"}
        )
        org = result.fetchone()

        if org:
            org_id = str(org[0])
            print(f"✓ Using existing organization: {org_id}")
        else:
            org_id = str(uuid4())
            session.execute(
                text("""
                    INSERT INTO atlas.organizations (id, name, created_at, updated_at)
                    VALUES (:id, :name, NOW(), NOW())
                """),
                {"id": org_id, "name": "Test CPA Firm"}
            )
            session.commit()
            print(f"✓ Created organization: {org_id}")

        # Create test users
        test_users = [
            {"email": "partner@testfirm.com", "full_name": "Partner User", "password": "Partner123!", "role": "partner"},
            {"email": "manager@testfirm.com", "full_name": "Manager User", "password": "Manager123!", "role": "manager"},
            {"email": "staff@testfirm.com", "full_name": "Staff User", "password": "Staff123!", "role": "staff"}
        ]

        created = 0
        for user in test_users:
            # Check if exists
            result = session.execute(
                text("SELECT id FROM atlas.users WHERE email = :email"),
                {"email": user["email"]}
            )
            if result.fetchone():
                print(f"⚠ User exists: {user['email']}")
                continue

            # Create user - dynamically build query based on available columns
            user_id = str(uuid4())
            hashed_pw = pwd_context.hash(user["password"])

            # Build INSERT based on what columns exist
            if 'full_name' in columns:
                insert_sql = """
                    INSERT INTO atlas.users (
                        id, email, full_name, hashed_password, organization_id,
                        role, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :email, :full_name, :hashed_password, :organization_id,
                        CAST(:role AS atlas.user_role), true, NOW(), NOW()
                    )
                """
                params = {
                    "id": user_id,
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "hashed_password": hashed_pw,
                    "organization_id": org_id,
                    "role": user["role"]
                }
            else:
                # Fallback: use only email, hashed_password, organization_id, role
                insert_sql = """
                    INSERT INTO atlas.users (
                        id, email, hashed_password, organization_id,
                        role, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :email, :hashed_password, :organization_id,
                        CAST(:role AS atlas.user_role), true, NOW(), NOW()
                    )
                """
                params = {
                    "id": user_id,
                    "email": user["email"],
                    "hashed_password": hashed_pw,
                    "organization_id": org_id,
                    "role": user["role"]
                }

            session.execute(text(insert_sql), params)
            session.commit()
            created += 1
            print(f"✓ Created: {user['email']} ({user['role']})")

        print("\n" + "="*60)
        print(f"Success! Created {created} users")
        print("="*60)
        print("\nLogin Credentials:")
        print("-" * 60)
        for user in test_users:
            print(f"\nEmail:    {user['email']}")
            print(f"Password: {user['password']}")
            print(f"Role:     {user['role']}")

        print("\n" + "="*60)
        print("Portal URLs:")
        print("  https://portal.auraai.toroniandcompany.com/login")
        print("  https://cpa.auraai.toroniandcompany.com/login")
        print("="*60)

    except Exception as e:
        session.rollback()
        print(f"\n✗ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()

if __name__ == "__main__":
    create_test_users()
