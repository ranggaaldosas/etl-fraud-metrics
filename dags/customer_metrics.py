from datetime import datetime

from airflow.decorators import dag, task
from airflow.models.baseoperator import chain
from airflow.providers.airbyte.operators.airbyte import AirbyteTriggerSyncOperator
from cosmos.airflow.task_group import DbtTaskGroup
from cosmos.config import RenderConfig
from cosmos.constants import LoadMode
from include.dbt.fraud.cosmos_config import DBT_CONFIG, DBT_PROJECT_CONFIG

AIRBYTE_JOB_ID_LOAD_CUSTOMER_TRANSACTIONS_RAW = "057d138b-f07c-4803-ba4a-dfbccbdfcb31"
AIRBYTE_JOB_ID_LOAD_LABELED_TRANSACTIONS_RAW = "4a0af944-be1d-461a-bcb1-60cff049cc90"
AIRBYTE_JOB_ID_RAW_TO_STAGING = "66ddc0b5-d76c-4966-9565-f9c248d45bb3"


@dag(
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
    tags=["airbyte", "risk"],
)
def customer_metrics():
    load_customer_transactions_raw = AirbyteTriggerSyncOperator(
        task_id="load_customer_transactions_raw",
        airbyte_conn_id="airbyte",
        connection_id=AIRBYTE_JOB_ID_LOAD_CUSTOMER_TRANSACTIONS_RAW,
    )

    load_labeled_transactions_raw = AirbyteTriggerSyncOperator(
        task_id="load_labeled_transactions_raw",
        airbyte_conn_id="airbyte",
        connection_id=AIRBYTE_JOB_ID_LOAD_LABELED_TRANSACTIONS_RAW,
    )

    write_to_staging = AirbyteTriggerSyncOperator(
        task_id="write_to_staging",
        airbyte_conn_id="airbyte",
        connection_id=AIRBYTE_JOB_ID_RAW_TO_STAGING,
    )

    @task
    def airbyte_job_complete():
        print("All Airbyte jobs are complete")

    @task.external_python(python="/opt/airflow/soda_venv/bin/python")
    def audit_customer_transactions(
        scan_name="customer_transactions",
        checks_subpath="tables",
        data_source="staging",
    ):
        from include.soda.helpers import check

        check(scan_name, checks_subpath, data_source)

    @task.external_python(python="/opt/airflow/soda_venv/bin/python")
    def audit_labeled_transactions(
        scan_name="labeled_transactions", checks_subpath="tables", data_source="staging"
    ):
        from include.soda.helpers import check

        check(scan_name, checks_subpath, data_source)

    @task
    def quality_check():
        print("All quality checks are complete")

    publish = DbtTaskGroup(
        group_id="publish",
        project_config=DBT_PROJECT_CONFIG,
        profile_config=DBT_CONFIG,
        render_config=RenderConfig(load_method=LoadMode.DBT_LS, select=["path:models"]),
    )

    chain(
        [load_labeled_transactions_raw, load_customer_transactions_raw],
        write_to_staging,
        airbyte_job_complete(),
        [audit_customer_transactions(), audit_labeled_transactions()],
        quality_check(),
        publish,
    )


customer_metrics = customer_metrics()
