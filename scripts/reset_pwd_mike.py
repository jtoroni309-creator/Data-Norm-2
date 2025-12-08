import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
import bcrypt

async def reset_password():
    db_url = os.environ.get('DATABASE_URL')
    engine = create_async_engine(db_url)

    # Hash the password using bcrypt
    password = b'Cred1234'
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt).decode('utf-8')

    async with engine.begin() as conn:
        # Use proper parameterized query
        await conn.execute(
            text("UPDATE atlas.users SET hashed_password = :pwd WHERE email = :email"),
            {"pwd": hashed, "email": "mikehaas40@gmail.com"}
        )

        print(f'Password reset for mikehaas40@gmail.com')
        print(f'New password: Cred1234')

asyncio.run(reset_password())
