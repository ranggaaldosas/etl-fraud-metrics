### Project ETL Fraud

> End-to-end data pipeline with write-audit-publish (WAP) pattern

- **Data Stack**
  - Orchestration = Apache Airlow
  - Connector = Airbyte
  - Data Transformation = dbt
  - Data Quality Platform = Soda
  - Database = Postgre & MySQL & AWS S3
  - OLAP/Data Warehouse = Snowflake


#### A. System Design
![system_design](./assets/system_design_fraud_etl.png)

#### B. Airflow Graph
![flow](./assets/airflow_graph.png)

#### C. Data Quality Check
![soda](./assets/soda_data_quality_check.png)

#### D. Snowflake Data Warehouse
![dwh](./assets/Snowflake_DWH.png)