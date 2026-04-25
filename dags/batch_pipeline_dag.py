from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from batch_pipeline_settings import DEFAULT_ARGS
from batch_pipeline_steps import check_health, increment_data, read_data, write_data

dag = DAG(
    'batch_pipeline',
    default_args=DEFAULT_ARGS,
    description='Batch pipeline: READ → INCREMENT → WRITE',
    schedule='*/2 * * * *',  # Runs every 2 minutes automatically
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=False,  # Already set - good!
    tags=['batch', 'read-write', 'ikram', 'trading'],
)

read_task = PythonOperator(
    task_id='read_data',
    python_callable=read_data,
    dag=dag,
)

increment_task = PythonOperator(
    task_id='increment_data',
    python_callable=increment_data,
    dag=dag,
)

write_task = PythonOperator(
    task_id='write_data',
    python_callable=write_data,
    dag=dag,
)

health_task = PythonOperator(
    task_id='health_check',
    python_callable=check_health,
    dag=dag,
)

notification = BashOperator(
    task_id='notify_complete',
    bash_command='echo "✅ Batch pipeline completed at $(date)"',
    dag=dag,
)

read_task >> increment_task >> write_task >> health_task >> notification
