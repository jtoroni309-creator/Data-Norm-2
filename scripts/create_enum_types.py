#!/usr/bin/env python3
"""Create PostgreSQL ENUM types for engagement service"""
import asyncio
import asyncpg
import os
import urllib.parse

def parse_database_url():
    url = os.environ["DATABASE_URL"]
    url = url.replace("postgresql+asyncpg://", "")
    parts = url.split("@")
    creds = parts[0]
    hostpart = parts[1]
    user, password = creds.split(":", 1)
    password = urllib.parse.unquote(password)
    host_db = hostpart.split("?")[0]
    host_port, db = host_db.rsplit("/", 1)
    host, port = host_port.rsplit(":", 1)
    return host, int(port), user, password, db

async def create_types():
    host, port, user, password, db = parse_database_url()
    print(f"Connecting to {host}:{port}/{db} as {user}")

    conn = await asyncpg.connect(
        host=host, port=port, user=user,
        password=password, database=db, ssl="require"
    )

    # Check existing types
    existing = await conn.fetch("""
        SELECT typname FROM pg_type
        WHERE typname IN ('engagement_type', 'engagement_status', 'user_role', 'binder_node_type', 'workpaper_status')
    """)
    existing_names = [r['typname'] for r in existing]
    print(f"Existing types: {existing_names}")

    # Check table exists
    tables = await conn.fetch("""
        SELECT table_schema, table_name FROM information_schema.tables
        WHERE table_name = 'engagements'
    """)
    print(f"Engagements table: {[(r['table_schema'], r['table_name']) for r in tables]}")

    # Check type schemas
    type_schemas = await conn.fetch("""
        SELECT n.nspname as schema, t.typname as type FROM pg_type t
        JOIN pg_namespace n ON t.typnamespace = n.oid
        WHERE t.typname IN ('engagement_type', 'engagement_status')
    """)
    print(f"Type schemas: {[(r['schema'], r['type']) for r in type_schemas]}")

    # Check column types
    columns = await conn.fetch("""
        SELECT column_name, data_type, udt_name, udt_schema FROM information_schema.columns
        WHERE table_schema = 'atlas' AND table_name = 'engagements'
        ORDER BY ordinal_position
    """)
    print(f"Columns in engagements:")
    for col in columns:
        print(f"  {col['column_name']}: {col['data_type']} (udt: {col['udt_schema']}.{col['udt_name']})")

    # Create schema if not exists
    await conn.execute("CREATE SCHEMA IF NOT EXISTS atlas")

    # Create ENUM types if they don't exist
    if 'engagement_type' not in existing_names:
        print("Creating engagement_type...")
        await conn.execute("""
            CREATE TYPE engagement_type AS ENUM ('audit', 'review', 'compilation', 'agreed_upon_procedures')
        """)
        print("Created engagement_type")

    if 'engagement_status' not in existing_names:
        print("Creating engagement_status...")
        await conn.execute("""
            CREATE TYPE engagement_status AS ENUM ('draft', 'planning', 'fieldwork', 'review', 'finalized')
        """)
        print("Created engagement_status")

    if 'user_role' not in existing_names:
        print("Creating user_role...")
        await conn.execute("""
            CREATE TYPE user_role AS ENUM ('partner', 'manager', 'senior', 'staff', 'qc_reviewer', 'client_contact')
        """)
        print("Created user_role")

    if 'binder_node_type' not in existing_names:
        print("Creating binder_node_type...")
        await conn.execute("""
            CREATE TYPE binder_node_type AS ENUM ('folder', 'workpaper', 'evidence', 'note')
        """)
        print("Created binder_node_type")

    if 'workpaper_status' not in existing_names:
        print("Creating workpaper_status...")
        await conn.execute("""
            CREATE TYPE workpaper_status AS ENUM ('draft', 'prepared', 'reviewed', 'approved')
        """)
        print("Created workpaper_status")

    await conn.close()
    print("Done!")

if __name__ == "__main__":
    asyncio.run(create_types())
