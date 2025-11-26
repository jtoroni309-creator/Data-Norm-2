import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
import os
from passlib.context import CryptContext

async def check_and_create_user():
    db_url = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://atlasadmin:j:%[uxtnylFnDK9Cd5{+B0P86vv%HN5l@aura-audit-ai-prod-psql.postgres.database.azure.com:5432/atlas?ssl=require')
    engine = create_async_engine(db_url)
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    async with engine.connect() as conn:
        # Check if user exists
        result = await conn.execute(text("""
            SELECT u.id, u.email, u.first_name, u.last_name, u.password_hash, u.is_active, f.firm_name
            FROM atlas.users u
            LEFT JOIN atlas.cpa_firms f ON u.cpa_firm_id = f.id
            WHERE u.email = :email
        """), {'email': 'jtoroni@toroniandcompany.com'})
        user = result.fetchone()

        if user:
            print(f'User exists: {user[1]}')
            print(f'Name: {user[2]} {user[3]}')
            print(f'Active: {user[5]}')
            print(f'Firm: {user[6]}')
            print(f'Hash starts with: {user[4][:20]}...')

            # Test password verification
            is_valid = pwd_context.verify('AuraAdmin2024!', user[4])
            print(f'Password valid: {is_valid}')

            if not is_valid:
                # Update password
                new_hash = pwd_context.hash('AuraAdmin2024!')
                await conn.execute(text("""
                    UPDATE atlas.users
                    SET password_hash = :hash
                    WHERE email = :email
                """), {'hash': new_hash, 'email': 'jtoroni@toroniandcompany.com'})
                await conn.commit()
                print(f'Password updated!')
        else:
            print('User does not exist - creating...')

            # Check if firm exists
            firm_result = await conn.execute(text("""
                SELECT id FROM atlas.cpa_firms
                WHERE firm_name = :firm_name
            """), {'firm_name': 'Toroni and Company'})
            firm = firm_result.fetchone()

            if not firm:
                # Create firm
                firm_result = await conn.execute(text("""
                    INSERT INTO atlas.cpa_firms (id, firm_name, legal_name, primary_contact_email, primary_contact_name, subscription_tier, subscription_status, is_active, created_at, updated_at)
                    VALUES (gen_random_uuid(), :firm_name, :legal_name, :email, :name, :tier, :status, true, NOW(), NOW())
                    RETURNING id
                """), {
                    'firm_name': 'Toroni and Company',
                    'legal_name': 'Toroni and Company LLC',
                    'email': 'admin@toroniandcompany.com',
                    'name': 'Jonathan Toroni',
                    'tier': 'enterprise',
                    'status': 'active'
                })
                firm = firm_result.fetchone()
                print(f'Created firm with ID: {firm[0]}')

            # Create user
            new_hash = pwd_context.hash('AuraAdmin2024!')
            await conn.execute(text("""
                INSERT INTO atlas.users (id, cpa_firm_id, email, first_name, last_name, password_hash, is_active, is_email_verified, created_at, updated_at)
                VALUES (gen_random_uuid(), :firm_id, :email, :first_name, :last_name, :password_hash, true, true, NOW(), NOW())
            """), {
                'firm_id': str(firm[0]),
                'email': 'jtoroni@toroniandcompany.com',
                'first_name': 'Jonathan',
                'last_name': 'Toroni',
                'password_hash': new_hash
            })
            await conn.commit()
            print('User created!')

asyncio.run(check_and_create_user())
