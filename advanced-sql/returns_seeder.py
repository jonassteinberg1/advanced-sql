import sys
import psycopg2
from faker import Faker
from datetime import datetime

def create_connection():
    return psycopg2.connect(
        dbname="returns", 
        user="user", 
        password="password", 
        host="localhost", 
        port="5433"
    )

def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                return_id SERIAL PRIMARY KEY,
                firstName VARCHAR(100) NOT NULL,
                lastName VARCHAR(100) NOT NULL,
                address VARCHAR(500) NOT NULL,
                returnDate TIMESTAMP WITH TIME ZONE
            )
        """)
        conn.commit()

def insert_data(conn, data):
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO returns (firstName, lastName, address, returnDate)
            VALUES (%s, %s, %s, %s)
        """, data)
        conn.commit()

def generate_data(n):
    fake = Faker()
    return [
        (fake.first_name(), fake.last_name(), fake.address(), fake.date_time_this_decade())
        for _ in range(n)
    ]

def main():
    if len(sys.argv) != 2:
        print("Usage: python returns_seeder.py <number_of_rows>")
        sys.exit(1)

    num_rows = int(sys.argv[1])
    data = generate_data(num_rows)

    conn = create_connection()
    create_table(conn)
    insert_data(conn, data)
    conn.close()
    print(f"Inserted {num_rows} rows into 'returns' table.")

if __name__ == "__main__":
    main()

