from airflow.decorators import dag, task
from datetime import datetime
from include.scripts.transaction_generator import main as _generate_transaction_data
from include.scripts.detection_generator import main as _generate_fraud_data
from airflow.models.baseoperator import chain

@dag(schedule='@daily', start_date=datetime(2024, 1, 1), catchup=False)
def generate_data():
    
    @task
    def generate_transaction_data(data_interval_start=None):
        _generate_transaction_data(data_interval_start)
        
    @task
    def generate_fraud_data(data_interval_start=None):
        _generate_fraud_data(data_interval_start)
        
    chain(generate_transaction_data(), generate_fraud_data())
    
generate_data()