from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from batch_pipeline_settings import DEFAULT_ARGS
from batch_pipeline_steps import check_health, run_batch_pipeline


dag = DAG(
    'batch_pipeline',
    default_args=DEFAULT_ARGS,
    description='Batch pipeline: READ → INCREMENT → WRITE every 2 minutes',
    schedule='*/2 * * * *',
    catchup=False,
    max_active_runs=1,
    schedule_interval=None,
    is_paused_upon_creation=False,
    tags=['batch', 'read-write', 'ikram'],
)

process_task = PythonOperator(
    task_id='batch_process',
    python_callable=run_batch_pipeline,
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

process_task >> health_task >> notification
