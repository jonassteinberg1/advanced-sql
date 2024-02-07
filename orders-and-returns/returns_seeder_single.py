import sys
import psycopg2
from faker import Faker
from datetime import datetime

def create_connection():
    return psycopg2.connect(
        dbname="postgres",
        user="user",
        password="password",
        host="localhost",
        port="5432"
    )

def create_schema(conn):
    with conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS returns;")
        conn.commit()

def create_returns_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS returns.returns (
                returnID SERIAL PRIMARY KEY,
                orderID INT NOT NULL,
                productName VARCHAR(255) NOT NULL,
                returnDate TIMESTAMP WITH TIME ZONE,
                reason TEXT
            );
        """)
        conn.commit()

def generate_returns_data(n, order_id_range):
    fake = Faker()
    return [
        (fake.random_int(min=order_id_range[0], max=order_id_range[1]),
         fake.word(),
         fake.date_time_this_decade(),
         fake.sentence())
        for _ in range(n)
    ]

def insert_into_returns(conn, returns_data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO returns.returns (orderID, productName, returnDate, reason)
            VALUES (%s, %s, %s, %s);
        """, returns_data)
        conn.commit()

def create_customer_feedback_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS returns.customer_feedback (
                feedbackID SERIAL PRIMARY KEY,
                returnID INT REFERENCES returns.returns(returnID),
                customerID INT,
                feedback TEXT,
                feedbackDate TIMESTAMP WITH TIME ZONE
            );
        """)
        conn.commit()

def generate_customer_feedback_data(n, return_id_range):
    fake = Faker()
    return [
        (fake.random_int(min=return_id_range[0], max=return_id_range[1]),
         fake.random_int(min=1, max=1000),
         fake.sentence(),
         fake.date_time_this_decade())
        for _ in range(n)
    ]

def insert_into_customer_feedback(conn, feedback_data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO returns.customer_feedback (returnID, customerID, feedback, feedbackDate)
            VALUES (%s, %s, %s, %s);
        """, feedback_data)
        conn.commit()

def create_return_processing_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS returns.return_processing (
                processingID SERIAL PRIMARY KEY,
                returnID INT REFERENCES returns.returns(returnID),
                processingStep VARCHAR(255),
                status VARCHAR(100),
                updateDate TIMESTAMP WITH TIME ZONE
            );
        """)
        conn.commit()

def generate_return_processing_data(n, return_id_range):
    fake = Faker()
    processing_steps = ['Received', 'Under Review', 'Refunded', 'Declined']
    return [
        (fake.random_int(min=return_id_range[0], max=return_id_range[1]),
         fake.word(ext_word_list=processing_steps),
         fake.word(ext_word_list=['Pending', 'Completed', 'Cancelled']),
         fake.date_time_this_decade())
        for _ in range(n)
    ]

def insert_into_return_processing(conn, processing_data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO returns.return_processing (returnID, processingStep, status, updateDate)
            VALUES (%s, %s, %s, %s);
        """, processing_data)
        conn.commit()

def main():
    if len(sys.argv) != 2:
        print("Usage: python seed_returns_database.py <number_of_rows>")
        sys.exit(1)

    num_rows = int(sys.argv[1])
    conn = create_connection()
    create_schema(conn)  # Ensure the schema exists before creating tables
    create_returns_table(conn)
    returns_data = generate_returns_data(num_rows, (1, 1000))  # Example orderID range
    insert_into_returns(conn, returns_data)

    create_customer_feedback_table(conn)
    feedback_data = generate_customer_feedback_data(num_rows, (1, num_rows))  # Example returnID range
    insert_into_customer_feedback(conn, feedback_data)

    create_return_processing_table(conn)
    processing_data = generate_return_processing_data(num_rows, (1, num_rows))  # Example returnID range
    insert_into_return_processing(conn, processing_data)

    conn.close()
    print(f"Inserted {num_rows} rows into 'returns.returns', 'returns.customer_feedback', and 'returns.return_processing' tables.")

if __name__ == "__main__":
    main()

