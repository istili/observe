from datetime import datetime, timedelta

# Markets that pipeline processes
MARKETS = [
    ('tokyo', 'Tokyo'),
    ('london', 'London'),
    ('new_york', 'New York'),
]

# Default arguments for all DAG tasks
DEFAULT_ARGS = {
    'owner': 'ikram',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}
