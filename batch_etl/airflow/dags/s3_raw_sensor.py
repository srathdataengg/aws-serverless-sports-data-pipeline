from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

BUCKET_NAME = "sports-analytics-data-platform"
KEY_PREFIX = "raw/league=PL/date={{ ds }}/matches.json"

default_args = {
    "owner": "soumyakanta",
    "retries": 1,
    "retry_delay": timedelta(minutes=3)
}

with DAG(
    dag_id="check_s3_raw_data",
    start_date=datetime(2025,12,5),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["aws","s3","sensor"],
) as dag:

    wait_for_raw = S3KeySensor(
        task_id="wait_for_raw_file",
        bucket_name=BUCKET_NAME,
        bucket_key=KEY_PREFIX,
        poke_interval=60,
        timeout=3600
    )