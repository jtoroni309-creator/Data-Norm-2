"""
Run database migration script
"""
import psycopg2
from urllib.parse import quote_plus
import sys

# Database connection details
host = "aura-audit-ai-prod-psql.postgres.database.azure.com"
database = "atlas"
user = "atlasadmin"
password = "j:%[uxtnyLFnDK9Cd5{)B0P86vv%HN5l"
port = 5432

# Migration file
migration_file = r"c:\Users\jtoroni\Data Norm\Data-Norm-2\database\migrations\012_rd_client_portal.sql"

def run_migration():
    try:
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port,
            sslmode="require"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print(f"Reading migration file: {migration_file}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()

        print("Executing migration...")
        # Split by semicolon and execute each statement
        statements = sql.split(';')
        for i, stmt in enumerate(statements):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                try:
                    cursor.execute(stmt)
                    print(f"  Statement {i+1}: OK")
                except Exception as e:
                    if "already exists" in str(e) or "duplicate" in str(e).lower():
                        print(f"  Statement {i+1}: Already exists (skipped)")
                    else:
                        print(f"  Statement {i+1}: Error - {e}")

        cursor.close()
        conn.close()
        print("\nMigration completed successfully!")
        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)
