import logging
import time

import psycopg2
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from batch_pipeline_settings import (
    COUNTER_TABLE,
    DB_CONFIG,
    MARKETS,
    MARKET_FRESHNESS_TABLE,
)

logger = logging.getLogger(__name__)


def emit_market_freshness_metrics(last_success_epoch):
    """Emit one gauge metric per market with latest success timestamp."""

    for market_key, _ in MARKETS:
        Stats.gauge(f"market_last_success_unix_{market_key}", last_success_epoch)


def _ensure_counter_table(cur):
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {COUNTER_TABLE} (
            id SMALLINT PRIMARY KEY,
            value BIGINT NOT NULL DEFAULT 0,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    cur.execute(
        f"""
        INSERT INTO {COUNTER_TABLE} (id, value)
        VALUES (1, 0)
        ON CONFLICT (id) DO NOTHING
        """
    )


def _upsert_market_freshness(cur):
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {MARKET_FRESHNESS_TABLE} (
            market_key TEXT PRIMARY KEY,
            market_name TEXT NOT NULL,
            last_success_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    for market_key, market_name in MARKETS:
        cur.execute(
            f"""
            INSERT INTO {MARKET_FRESHNESS_TABLE} (market_key, market_name, last_success_at)
            VALUES (%s, %s, NOW())
            ON CONFLICT (market_key)
            DO UPDATE SET
                market_name = EXCLUDED.market_name,
                last_success_at = EXCLUDED.last_success_at
            """,
            (market_key, market_name),
        )


def read_data():
    """READ step: load current counter value from Postgres."""

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                _ensure_counter_table(cur)
                cur.execute(f"SELECT value FROM {COUNTER_TABLE} WHERE id = 1")
                current_value = cur.fetchone()[0]

        logger.info(f"📖 READ from Postgres: value = {current_value}")
        return current_value
    finally:
        conn.close()


def increment_data():
    """INCREMENT step: apply deterministic counter increment."""

    context = get_current_context()
    current_value = context['ti'].xcom_pull(task_ids='read_data')
    new_value = int(current_value) + 1
    logger.info(f"⚙️ PROCESS: {current_value} -> {new_value}")
    return new_value


def write_data():
    """WRITE step: persist new value and emit market freshness metrics."""

    context = get_current_context()
    new_value = context['ti'].xcom_pull(task_ids='increment_data')

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                _ensure_counter_table(cur)
                cur.execute(
                    f"""
                    UPDATE {COUNTER_TABLE}
                    SET value = %s, updated_at = NOW()
                    WHERE id = 1
                    """,
                    (new_value,),
                )
                _upsert_market_freshness(cur)

        logger.info(f"💾 WRITE to Postgres: value = {new_value}")
        emit_market_freshness_metrics(int(time.time()))
        logger.info("📈 Emitted market freshness metrics for Tokyo, London, and New York")
        return new_value
    finally:
        conn.close()


def check_health():
    """Check whether Postgres is reachable and the counter row is valid."""

    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {COUNTER_TABLE} (
                        id SMALLINT PRIMARY KEY,
                        value BIGINT NOT NULL DEFAULT 0,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                cur.execute(
                    f"""
                    INSERT INTO {COUNTER_TABLE} (id, value)
                    VALUES (1, 0)
                    ON CONFLICT (id) DO NOTHING
                    """
                )
                cur.execute(f"SELECT value FROM {COUNTER_TABLE} WHERE id = 1")
                value = cur.fetchone()[0]

        logger.info(f"✅ Health check OK - current batch value: {value}")
        return "healthy"
    except Exception as e:
        logger.error(f"❌ Health check FAILED - database error: {e}")
        raise
    finally:
        conn.close()
