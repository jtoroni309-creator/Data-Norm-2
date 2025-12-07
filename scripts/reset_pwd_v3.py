#!/usr/bin/env python3
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
import sys
sys.path.insert(0, '/app')
from app.main import hash_password

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")

async def reset_password():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Hash the new password using identity service's hash function
        new_password = "Antonio1977$$"
        hashed = hash_password(new_password)
        print(f"Generated hash: {hashed[:30]}...")

        # Update the user password
        result = await conn.execute(
            text("UPDATE atlas.users SET hashed_password = :pwd WHERE email = :email RETURNING id, email"),
            {"pwd": hashed, "email": "jtoroni@toroniandcompany.com"}
        )
        row = result.fetchone()
        if row:
            print(f"Password reset for user ID: {row[0]}, Email: {row[1]}")
        else:
            print("User not found!")

asyncio.run(reset_password())
