import logging
import time

from airflow.operators.python import get_current_context
from airflow.stats import Stats
from batch_pipeline_settings import MARKETS
from db_utils import (
    get_counter_value,
    update_counter_value,
    update_market_freshness,
    verify_database,
)

logger = logging.getLogger(__name__)

def emit_market_freshness_metrics(timestamp_epoch):
    for market_key, _ in MARKETS:
        Stats.gauge(f"market_last_success_unix_{market_key}", timestamp_epoch)


def read_data():
    current_value = get_counter_value()
    logger.info(f"📖 READ from database: value = {current_value}")
    return current_value


def increment_data():
    context = get_current_context()
    current_value = context['ti'].xcom_pull(task_ids='read_data')
    new_value = int(current_value) + 1
    logger.info(f"⚙️ PROCESS: {current_value} → {new_value}")
    return new_value


def write_data():
    context = get_current_context()
    new_value = context['ti'].xcom_pull(task_ids='increment_data')

    # Update counter
    update_counter_value(new_value)
    logger.info(f"💾 WRITE to database: value = {new_value}")

    # Update market freshness (batch operation)
    update_market_freshness(MARKETS)
    
    # Emit metrics for monitoring
    emit_market_freshness_metrics(int(time.time()))
    logger.info("📈 Emitted market freshness metrics")

    return new_value


def check_health():
    verify_database()
    logger.info("✅ Health check passed")
    return "healthy"


def initialize_database():
    from db_utils import initialize_tables
    
    initialize_tables()
    logger.info("📊 Database initialization complete")
