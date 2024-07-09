import psycopg2
from psycopg2 import sql
import random
from datetime import datetime, timedelta

# Database connection parameters
conn_params = {
    "host": "airbyte-db",
    "database": "airbyte",
    "user": "docker",
    "password": "docker"
}

def create_transactions_table():
    """
    Create the customer_transactions table if it doesn't exist.
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS customer_transactions (
        transaction_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        transaction_date TIMESTAMP NOT NULL,
        amount DECIMAL(10, 2) NOT NULL
    );
    """
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute(create_table_query)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error creating table: {e}")
    finally:
        if conn is not None:
            conn.close()
            
def generate_transaction_data(user_id, num_transactions, data_interval_start):
    """
    Generate a list of tuples representing transaction data for a given user.
    """
    transactions = []
    for _ in range(num_transactions):
        if data_interval_start is not None:
            transaction_date = data_interval_start + timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59))
        else:
            transaction_date = datetime.now() - timedelta(hours=random.randint(1, 23), minutes=random.randint(0, 59))
        amount = round(random.uniform(5.0, 500.0), 2)  # Simulate transaction amount between $5 and $500
        transactions.append((user_id, transaction_date, amount))
    return transactions

def insert_transactions_into_db(transactions):
    """
    Insert transaction data into the PostgreSQL database.
    """
    query = sql.SQL("INSERT INTO customer_transactions (user_id, transaction_date, amount) VALUES (%s, %s, %s)")
    conn = None
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.executemany(query, transactions)
        conn.commit()
        cur.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn is not None:
            conn.close()

def main(data_interval_start=None):
    create_transactions_table()  # Ensure table exists before inserting data

    # Example usage
    num_users = 10  # Simulate transactions for 10 users
    for user_id in range(1, num_users + 1):
        transactions = generate_transaction_data(user_id, random.randint(5, 20), data_interval_start)  # Each user gets 5 to 20 transactions
        insert_transactions_into_db(transactions)

    print("Data generation complete.")
    
if __name__ == "__main__":
    main()