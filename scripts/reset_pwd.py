#!/usr/bin/env python3
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
from passlib.context import CryptContext

DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgresql://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def reset_password():
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        # Hash the new password
        new_password = "Antonio1977$$"
        hashed = pwd_context.hash(new_password)

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
