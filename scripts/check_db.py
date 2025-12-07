from sqlalchemy import create_engine, text
import os

db_url = os.environ.get('DATABASE_URL')
engine = create_engine(db_url)

with engine.connect() as conn:
    # Check clients
    result = conn.execute(text('SELECT COUNT(*) FROM clients'))
    print(f'Total clients in DB: {result.scalar()}')

    # Check engagements
    result = conn.execute(text('SELECT COUNT(*) FROM engagements'))
    print(f'Total engagements in DB: {result.scalar()}')

    # List some clients
    result = conn.execute(text('SELECT id, name, status, organization_id FROM clients LIMIT 5'))
    print('Sample clients:')
    for row in result:
        print(f'  {row}')

    # List some engagements
    result = conn.execute(text('SELECT id, name, status, organization_id FROM engagements LIMIT 5'))
    print('Sample engagements:')
    for row in result:
        print(f'  {row}')
