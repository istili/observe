import logging
import psycopg2
from batch_pipeline_settings import COUNTER_TABLE, DB_CONFIG

logger = logging.getLogger(__name__)

def run_batch_pipeline():
    """Increment the counter safely using a transactional row lock."""

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
                cur.execute(
                    f"SELECT value FROM {COUNTER_TABLE} WHERE id = 1 FOR UPDATE"
                )
                current_value = cur.fetchone()[0]
                new_value = current_value + 1
                cur.execute(
                    f"""
                    UPDATE {COUNTER_TABLE}
                    SET value = %s, updated_at = NOW()
                    WHERE id = 1
                    """,
                    (new_value,),
                )

        logger.info(f"📖 READ from Postgres: value = {current_value}")
        logger.info(f"⚙️ PROCESS: {current_value} -> {new_value}")
        logger.info(f"💾 WRITE to Postgres: value = {new_value}")
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
