import mysql.connector
from mysql.connector import Error
import psycopg2
from datetime import datetime
import random

# PostgreSQL connection parameters
postgres_conn_params = {
    "host": "airbyte-db",
    "database": "airbyte",
    "user": "docker",
    "password": "docker"
}

# MySQL connection parameters
mysql_conn_params = {
    "host": "mysql",
    "database": "data",
    "user": "docker",
    "password": "docker"
}

def fetch_transaction_ids(data_interval_start):
    """
    Fetch transaction IDs from the PostgreSQL database for transactions that occurred today.
    """
    if data_interval_start is not None:
        today = data_interval_start.strftime('%Y-%m-%d')
    else:
        today = datetime.now().strftime('%Y-%m-%d')
    fetch_query = """
    SELECT transaction_id FROM customer_transactions
    WHERE transaction_date >= %s AND transaction_date < %s::date + interval '1 day'
    ORDER BY transaction_id;
    """
    try:
        conn = psycopg2.connect(**postgres_conn_params)
        cur = conn.cursor()
        cur.execute(fetch_query, (today, today))
        transaction_ids = [row[0] for row in cur.fetchall()]
        cur.close()
        return transaction_ids
    except Exception as e:
        print(f"Error fetching transaction IDs: {e}")
        return []
    finally:
        if conn is not None:
            conn.close()

def insert_labeled_transactions(transaction_ids):
    """
    Insert labeled transaction data into the MySQL database.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS labeled_transactions (
        transaction_id INT PRIMARY KEY,
        is_fraudulent BOOLEAN NOT NULL
    );
    """
    insert_query = "INSERT INTO labeled_transactions (transaction_id, is_fraudulent) VALUES (%s, %s)"
    
    try:
        conn = mysql.connector.connect(**mysql_conn_params)
        cur = conn.cursor()
        cur.execute(create_table_query)
        for transaction_id in transaction_ids:
            is_fraudulent = True if random.choice([True, False]) else False  # Randomly assign fraudulent flag
            cur.execute(insert_query, (transaction_id, is_fraudulent))
        conn.commit()
        cur.close()
        print("Labeled transaction data inserted successfully.")
    except Error as e:
        print(f"Error inserting labeled transaction data: {e}")
    finally:
        if conn is not None and conn.is_connected():
            conn.close()

def main(data_interval_start=None):
    transaction_ids = fetch_transaction_ids(data_interval_start)
    if transaction_ids:
        insert_labeled_transactions(transaction_ids)
    else:
        print("No transaction IDs fetched for the current day. No data inserted into labeled_transactions.")

if __name__ == "__main__":
    main()
