#!/usr/bin/env python3
"""
Create test users - uses actual database schema
"""
import os
import sys
from uuid import uuid4
from passlib.context import CryptContext
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not set", file=sys.stderr)
    sys.exit(1)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create CPA firm if not exists
        print("Checking for test CPA firm...")
        result = session.execute(
            text("SELECT id FROM atlas.cpa_firms WHERE firm_name = :name"),
            {"name": "Test CPA Firm"}
        )
        firm = result.fetchone()

        if firm:
            firm_id = str(firm[0])
            print(f"✓ Using existing firm: {firm_id}")
        else:
            firm_id = str(uuid4())
            session.execute(
                text("""
                    INSERT INTO atlas.cpa_firms (
                        id, firm_name, primary_contact_email,
                        subscription_tier, is_active, created_at, updated_at
                    ) VALUES (
                        :id, :name, :email, 'trial', true, NOW(), NOW()
                    )
                """),
                {"id": firm_id, "name": "Test CPA Firm", "email": "admin@testfirm.com"}
            )
            session.commit()
            print(f"✓ Created CPA firm: {firm_id}")

        # Create test users
        test_users = [
            {"email": "partner@testfirm.com", "first_name": "Partner", "last_name": "User", "password": "Partner123!"},
            {"email": "manager@testfirm.com", "first_name": "Manager", "last_name": "User", "password": "Manager123!"},
            {"email": "staff@testfirm.com", "first_name": "Staff", "last_name": "User", "password": "Staff123!"}
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

            # Create user with actual schema
            user_id = str(uuid4())
            hashed_pw = pwd_context.hash(user["password"])

            session.execute(
                text("""
                    INSERT INTO atlas.users (
                        id, cpa_firm_id, email, first_name, last_name,
                        password_hash, is_active, is_email_verified,
                        created_at, updated_at
                    ) VALUES (
                        :id, :firm_id, :email, :first_name, :last_name,
                        :password_hash, true, true, NOW(), NOW()
                    )
                """),
                {
                    "id": user_id,
                    "firm_id": firm_id,
                    "email": user["email"],
                    "first_name": user["first_name"],
                    "last_name": user["last_name"],
                    "password_hash": hashed_pw
                }
            )
            session.commit()
            created += 1
            print(f"✓ Created: {user['email']}")

        print("\n" + "="*60)
        print(f"Success! Created {created} users")
        print("="*60)
        print("\nLogin Credentials:")
        print("-" * 60)
        for user in test_users:
            print(f"\nEmail:    {user['email']}")
            print(f"Password: {user['password']}")

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
