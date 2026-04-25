import os
from datetime import datetime, timedelta

COUNTER_TABLE = 'batch_counter'
MARKET_FRESHNESS_TABLE = 'market_data_freshness'

MARKETS = [
    ('tokyo', 'Tokyo'),
    ('london', 'London'),
    ('new_york', 'New York'),
]

# Uses the same Postgres service and credentials as Airflow metadata DB.
DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'postgres'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'dbname': os.getenv('POSTGRES_DB', 'airflow'),
    'user': os.getenv('POSTGRES_USER', 'airflow'),
    'password': os.getenv('POSTGRES_PASSWORD', 'airflow'),
}

DEFAULT_ARGS = {
    'owner': 'ikram',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
