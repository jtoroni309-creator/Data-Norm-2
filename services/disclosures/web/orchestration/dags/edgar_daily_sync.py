from datetime import datetime
from airflow import DAG

default_args = {
    'owner': 'atlas',
    'start_date': datetime(2025, 1, 1),
}

dag = DAG(
    'edgar_daily_sync',
    default_args=default_args,
    schedule_interval='0 2 * * *',
    tags=['ingestion'],
)
